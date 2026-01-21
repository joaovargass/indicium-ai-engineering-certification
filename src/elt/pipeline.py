"""
ELT pipeline: incremental Extract, Load, Transform for SRAG data.

Stages: datas -> extracao -> upload -> download_deltas -> transform -> load_dw -> cache -> estado.
Raises ELTError(stage, message) on failure. Extraction date in Azure is updated only on full success.
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from azure.storage.filedatalake import FileSystemClient

from common.config import (
    CACHE_DIR,
    DASH_CACHE_PATH,
    FULL_REFRESH,
    PRIMARY_KEY_FIELD,
    PROJECT_ROOT,
    SRC_PATH,
)
from common.logging import logger
from elt.dw import trim_dw_to_max_rows
from elt.errors import ELTError

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
from elt.extract import extract_data, fetch_web_dates, setup_dirs  # noqa: E402
from elt.load import (  # noqa: E402
    cache_extraction_date_local,
    download_unprocessed_deltas,
    get_client,
    load_raw_state,
    mark_deltas_processed,
    read_from_dw,
    save_raw_state,
    save_to_dw,
    update_extraction_date,
    upload_frozen_delta,
    upload_live_delta,
)
from elt.transform import clean_data, select_essential  # noqa: E402


def _elt_upload_deltas(
    client: FileSystemClient,
    extract_result: dict,
    local_temp_dir: Path,
    raw_state: dict,
    do_full: bool,
    current_year: int,
) -> None:
    """Upload frozen and live deltas to Azure; save raw_state when deltas change."""
    try:
        initial_deltas_count = len(raw_state.get("deltas", []))
        for year, df in extract_result["frozen_dfs"].items():
            raw_state = upload_frozen_delta(
                client=client,
                df=df,
                year=year,
                local_temp_dir=local_temp_dir,
                raw_state=raw_state,
                full_refresh=do_full,
            )
        if extract_result["live_df"] is not None and extract_result["is_live_new"]:
            effective_live_year = extract_result.get("live_year") or current_year
            raw_state = upload_live_delta(
                client=client,
                df=extract_result["live_df"],
                year=effective_live_year,
                date_str=extract_result["live_date"],
                local_temp_dir=local_temp_dir,
                raw_state=raw_state,
            )
        final_deltas_count = len(raw_state.get("deltas", []))
        if final_deltas_count > initial_deltas_count:
            save_raw_state(client, raw_state)
    except ELTError:
        raise
    except Exception as e:
        raise ELTError("upload", f"Falha no upload: {e}") from e


def _elt_process_deltas(
    combined_df: pd.DataFrame | None,
    delta_files: list[str],
    client: FileSystemClient,
    do_full: bool,
) -> bool:
    """Transform, load to DW, and trim. Returns True if new data was loaded."""
    if combined_df is None or len(combined_df) == 0:
        return False
    try:
        if PRIMARY_KEY_FIELD in combined_df.columns:
            combined_df = combined_df.drop_duplicates(
                subset=[PRIMARY_KEY_FIELD], keep="last"
            )
        df_essential = select_essential(combined_df)
        df_cleaned = clean_data(df_essential)
    except Exception as e:
        raise ELTError("transform", f"Falha na transformacao: {e}") from e

    try:
        if PRIMARY_KEY_FIELD in df_cleaned.columns:
            df_cleaned[PRIMARY_KEY_FIELD] = pd.to_numeric(
                df_cleaned[PRIMARY_KEY_FIELD], errors="coerce"
            )
            max_val = df_cleaned[PRIMARY_KEY_FIELD].max()
            max_notific = int(max_val) if pd.notna(max_val) else 0
        else:
            max_notific = 0

        rows = save_to_dw(df_cleaned, if_exists="replace" if do_full else "append")
        mark_deltas_processed(client, delta_files, rows, max_notific)
        try:
            trim_dw_to_max_rows()
        except Exception as e:
            logger.warning(f"trim_dw_to_max_rows: {e}")
        return True
    except Exception as e:
        raise ELTError("load_dw", f"Falha ao carregar DW: {e}") from e


def _elt_update_cache(new_data_loaded: bool) -> None:
    """Update local parquet cache from DW when new data or cache missing."""
    if new_data_loaded or not DASH_CACHE_PATH.exists():
        try:
            logger.info("Updating local cache from DW...")
            full_df = read_from_dw()
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            full_df.to_parquet(DASH_CACHE_PATH, index=False)
            logger.info(f"Local cache updated: {len(full_df):,} rows")
        except Exception as e:
            raise ELTError("cache", f"Falha ao atualizar cache: {e}") from e
    else:
        logger.info("No new data loaded, local cache unchanged")


def _elt_save_estado(client: FileSystemClient) -> str:
    """Persist extraction date to Azure and local; return ISO extraction date."""
    try:
        extraction_date = datetime.now().isoformat()
        update_extraction_date(client, extraction_date)
        cache_extraction_date_local(extraction_date)
        return extraction_date
    except Exception as e:
        raise ELTError("estado", f"Falha ao salvar estado: {e}") from e


def _sql_pool_resume() -> bool:
    ws = os.getenv("AZURE_SYNAPSE_WORKSPACE_NAME")
    pool = os.getenv("AZURE_SQL_POOL_NAME") or os.getenv("AZURE_SQL_DATABASE")
    rg = os.getenv("AZURE_RESOURCE_GROUP", "ai-engineering")
    if not ws or not pool:
        return False
    try:
        out = subprocess.run(
            [
                "az",
                "synapse",
                "sql",
                "pool",
                "show",
                "--name",
                pool,
                "--workspace-name",
                ws,
                "-g",
                rg,
                "--query",
                "status",
                "-o",
                "tsv",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        status = (out.stdout or "").strip().lower() if out.returncode == 0 else ""
        if status != "paused":
            return False
        r = subprocess.run(
            [
                "az",
                "synapse",
                "sql",
                "pool",
                "resume",
                "--name",
                pool,
                "--workspace-name",
                ws,
                "-g",
                rg,
            ],
            capture_output=True,
            text=True,
            timeout=600,
        )
        if r.returncode != 0:
            logger.warning("sql pool resume: %s", r.stderr or r.stdout)
            return False
        time.sleep(90)
        return True
    except Exception as e:
        logger.warning("sql pool resume: %s", e)
        return False


def _sql_pool_pause() -> None:
    ws = os.getenv("AZURE_SYNAPSE_WORKSPACE_NAME")
    pool = os.getenv("AZURE_SQL_POOL_NAME") or os.getenv("AZURE_SQL_DATABASE")
    rg = os.getenv("AZURE_RESOURCE_GROUP", "ai-engineering")
    if not ws or not pool:
        return
    try:
        out = subprocess.run(
            [
                "az",
                "synapse",
                "sql",
                "pool",
                "show",
                "--name",
                pool,
                "--workspace-name",
                ws,
                "-g",
                rg,
                "--query",
                "status",
                "-o",
                "tsv",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        status = (out.stdout or "").strip().lower() if out.returncode == 0 else ""
        if status != "online":
            return
        r = subprocess.run(
            [
                "az",
                "synapse",
                "sql",
                "pool",
                "pause",
                "--name",
                pool,
                "--workspace-name",
                ws,
                "-g",
                rg,
            ],
            capture_output=True,
            text=True,
            timeout=600,
        )
        if r.returncode != 0:
            logger.warning("sql pool pause: %s", r.stderr or r.stdout)
    except Exception as e:
        logger.warning("sql pool pause: %s", e)


def run_incremental_elt(full_refresh: bool | None = None) -> str:
    """
    Run incremental ELT pipeline and return extraction date.

    Raises ELTError with stage info on failure. Only updates extraction date
    in Azure when the full pipeline completes successfully.

    Args:
        full_refresh: When True, re-download all; when None, uses config.

    Returns:
        ISO format extraction date string

    Raises:
        ELTError: On pipeline failure with stage and message

    """
    do_full = full_refresh if full_refresh is not None else FULL_REFRESH
    did_resume = _sql_pool_resume()

    try:
        data_dir, current_year, years = setup_dirs(PROJECT_ROOT)
        local_temp_dir = data_dir / "temp"
        local_temp_dir.mkdir(exist_ok=True)

        client = get_client()
        raw_state = load_raw_state(client)
        processed_years = raw_state.get("processed_years", [])
        last_live_date = raw_state.get("last_live_date")

        try:
            freeze_date, live_date, live_year = fetch_web_dates(
                do_full, processed_years, years, current_year
            )
        except ELTError:
            raise
        except Exception as e:
            raise ELTError("datas", f"Falha ao obter datas: {e}") from e

        try:
            extract_result = extract_data(
                data_dir=data_dir,
                current_year=current_year,
                years=years,
                processed_years=processed_years,
                last_live_date=last_live_date,
                freeze_date_str=freeze_date,
                live_date_str=live_date,
                live_year=live_year,
                full_refresh=do_full,
            )
        except ELTError:
            raise
        except Exception as e:
            raise ELTError("extracao", f"Falha na extracao: {e}") from e

        _elt_upload_deltas(
            client, extract_result, local_temp_dir, raw_state, do_full, current_year
        )

        try:
            combined_df, delta_files = download_unprocessed_deltas(
                client, local_temp_dir
            )
        except Exception as e:
            raise ELTError("download_deltas", f"Falha ao baixar deltas: {e}") from e

        new_data_loaded = _elt_process_deltas(combined_df, delta_files, client, do_full)
        _elt_update_cache(new_data_loaded)
        extraction_date = _elt_save_estado(client)
        return extraction_date
    finally:
        if did_resume:
            _sql_pool_pause()
