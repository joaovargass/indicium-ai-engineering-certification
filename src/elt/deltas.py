"""
Delta file operations for ELT pipeline.

Manages incremental loading via delta files:

Delta Types:
- **Frozen**: Complete year data that won't change (e.g., frozen_2023.parquet)
- **Live**: Current year incremental updates (e.g., delta_2024_15-11-2024_*.parquet)

Workflow:
1. Raw data is downloaded and uploaded to Azure as delta files
2. DW processes unprocessed deltas and marks them processed
3. When a year transitions from live to frozen, old live deltas are cleaned up

State Tracking:
- raw_state.json: Tracks uploaded deltas and processed years
- dw_state.json: Tracks which deltas have been loaded to DW

"""

from datetime import datetime
from pathlib import Path

import pandas as pd
from azure.storage.filedatalake import FileSystemClient

from common.config import PRIMARY_KEY_FIELD, RAW_DELTAS_DIR
from common.logging import logger
from elt.azure import _delete_file, _download_parquet, _upload_parquet
from elt.state import load_dw_state, load_raw_state, save_dw_state


def _generate_delta_filename(year: int, date_str: str) -> str:
    """
    Generate a unique delta filename with timestamp.

    Args:
        year: Data year
        date_str: Date string from source (e.g., "15-11-2024")

    Returns:
        Unique filename like "delta_2024_15-11-2024_20241115_143022.parquet"

    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"delta_{year}_{date_str}_{timestamp}.parquet"


def _cleanup_live_deltas(
    client: FileSystemClient, year: int, raw_state: dict
) -> tuple[dict, bool]:
    """
    Remove live deltas when a year transitions to frozen.

    When a year's data becomes frozen (complete), we remove any previous
    live deltas for that year since the frozen file contains all data.

    Args:
        client: Azure FileSystemClient
        year: Year transitioning to frozen
        raw_state: Current raw state dictionary

    Returns:
        Tuple of (updated_raw_state, was_any_live_in_dw)

    """
    live_deltas = [
        d
        for d in raw_state.get("deltas", [])
        if d.get("type") == "live" and d.get("year") == year
    ]

    if not live_deltas:
        return raw_state, False

    dw_state = load_dw_state(client)
    processed_by_dw = set(dw_state.get("processed_deltas", []))
    live_filenames = {d["filename"] for d in live_deltas}
    any_live_processed = bool(live_filenames & processed_by_dw)

    logger.info(f"Year {year} transitioning from live to frozen")
    logger.info(f"Removing {len(live_deltas)} old live delta(s)...")

    for delta in live_deltas:
        azure_path = f"{RAW_DELTAS_DIR}/{delta['filename']}"
        if _delete_file(client, azure_path):
            logger.debug(f"  Deleted: {delta['filename']}")

    raw_state["deltas"] = [
        d
        for d in raw_state["deltas"]
        if not (d.get("type") == "live" and d.get("year") == year)
    ]

    if any_live_processed:
        dw_state["processed_deltas"] = [
            f for f in dw_state["processed_deltas"] if f not in live_filenames
        ]
        save_dw_state(client, dw_state)
        logger.info(
            f"  Cleaned up DW state (removed {len(live_filenames)} old entries)"
        )

    return raw_state, any_live_processed


def upload_frozen_delta(
    client: FileSystemClient,
    df: pd.DataFrame,
    year: int,
    local_temp_dir: Path,
    raw_state: dict,
    full_refresh: bool = False,
) -> dict:
    """
    Upload frozen (complete) year data as a delta file.

    Frozen data represents a complete, unchanging year. This function:
    1. Cleans up any previous live deltas for the year
    2. Uploads the frozen parquet file
    3. Updates raw_state to mark year as processed

    Args:
        client: Azure FileSystemClient
        df: DataFrame with year's complete data
        year: Year being uploaded
        local_temp_dir: Local directory for temp files
        raw_state: Current raw state dictionary
        full_refresh: When True, re-upload even if year is in processed_years.

    Returns:
        Updated raw_state dictionary

    """
    if year in raw_state.get("processed_years", []) and not full_refresh:
        logger.info(f"Year {year} already processed, skipping")
        return raw_state

    raw_state, live_was_in_dw = _cleanup_live_deltas(client, year, raw_state)

    filename = f"frozen_{year}.parquet"
    azure_path = f"{RAW_DELTAS_DIR}/{filename}"

    if PRIMARY_KEY_FIELD in df.columns:
        df[PRIMARY_KEY_FIELD] = pd.to_numeric(df[PRIMARY_KEY_FIELD], errors="coerce")
        max_val = df[PRIMARY_KEY_FIELD].max()
        max_notific = int(max_val) if pd.notna(max_val) else 0
    else:
        max_notific = 0

    _upload_parquet(client, df, azure_path, local_temp_dir)

    # On full_refresh re-upload: overwrite file and mark as unprocessed so it gets loaded to DW
    if full_refresh and year in raw_state.get("processed_years", []):
        dw_state = load_dw_state(client)
        processed = dw_state.get("processed_deltas", [])
        if filename in processed:
            dw_state["processed_deltas"] = [f for f in processed if f != filename]
            save_dw_state(client, dw_state)
            logger.info(f"  Marked {filename} as unprocessed for full refresh")
        return raw_state

    if "processed_years" not in raw_state:
        raw_state["processed_years"] = []
    if year not in raw_state["processed_years"]:
        raw_state["processed_years"].append(year)
        raw_state["processed_years"] = sorted(raw_state["processed_years"])

    if "deltas" not in raw_state:
        raw_state["deltas"] = []
    # Avoid duplicate delta entry for the same frozen file
    if not any(d.get("filename") == filename for d in raw_state["deltas"]):
        raw_state["deltas"].append(
            {
                "filename": filename,
                "year": year,
                "type": "frozen",
                "max_notific": max_notific,
                "rows": len(df),
                "uploaded_at": datetime.now().isoformat(),
            }
        )

    if live_was_in_dw:
        dw_state = load_dw_state(client)
        dw_state["processed_deltas"].append(filename)
        save_dw_state(client, dw_state)
        logger.info(f"  Marked {filename} as already processed (data from live)")

    return raw_state


def upload_live_delta(
    client: FileSystemClient,
    df: pd.DataFrame,
    year: int,
    date_str: str,
    local_temp_dir: Path,
    raw_state: dict,
) -> dict:
    """
    Upload live (current year) data as incremental delta.

    Live deltas contain only new records since the last upload,
    identified by NU_NOTIFIC primary key. Only records with
    NU_NOTIFIC greater than the last known max are uploaded.

    Args:
        client: Azure FileSystemClient
        df: DataFrame with current year's data
        year: Current year
        date_str: Date string from source
        local_temp_dir: Local directory for temp files
        raw_state: Current raw state dictionary

    Returns:
        Updated raw_state dictionary

    """
    last_max_raw = 0
    for delta in raw_state.get("deltas", []):
        if delta.get("type") == "live" and delta.get("year") == year:
            last_max_raw = max(last_max_raw, delta.get("max_notific", 0))

    dw_state = load_dw_state(client)
    last_max_dw = dw_state.get("last_max_notific", 0)
    last_max = max(last_max_raw, last_max_dw)

    if PRIMARY_KEY_FIELD in df.columns:
        df[PRIMARY_KEY_FIELD] = pd.to_numeric(df[PRIMARY_KEY_FIELD], errors="coerce")
        new_records = df[df[PRIMARY_KEY_FIELD] > last_max].copy()
    else:
        new_records = df

    if len(new_records) == 0:
        logger.info("No new live records to upload")
        return raw_state

    filename = _generate_delta_filename(year, date_str)
    azure_path = f"{RAW_DELTAS_DIR}/{filename}"

    if PRIMARY_KEY_FIELD in new_records.columns:
        max_val = new_records[PRIMARY_KEY_FIELD].max()
        max_notific = int(max_val) if pd.notna(max_val) else 0
    else:
        max_notific = 0

    _upload_parquet(client, new_records, azure_path, local_temp_dir)

    raw_state["current_year"] = year
    raw_state["last_live_date"] = date_str
    raw_state["deltas"].append(
        {
            "filename": filename,
            "year": year,
            "type": "live",
            "date": date_str,
            "max_notific": max_notific,
            "rows": len(new_records),
            "uploaded_at": datetime.now().isoformat(),
        }
    )

    return raw_state


def get_unprocessed_deltas(client: FileSystemClient) -> list[dict]:
    """
    Get list of delta files not yet processed by DW.

    Compares raw_state.deltas against dw_state.processed_deltas
    to find deltas that need to be loaded into the data warehouse.

    Args:
        client: Azure FileSystemClient

    Returns:
        List of delta info dicts for unprocessed files

    """
    raw_state = load_raw_state(client)
    dw_state = load_dw_state(client)

    processed_deltas = set(dw_state.get("processed_deltas", []))
    all_deltas = raw_state.get("deltas", [])

    unprocessed = [d for d in all_deltas if d["filename"] not in processed_deltas]
    return unprocessed


def download_unprocessed_deltas(
    client: FileSystemClient,
    local_temp_dir: Path,
) -> tuple[pd.DataFrame | None, list[str]]:
    """
    Download unprocessed delta files and combine into single DataFrame.

    Args:
        client: Azure FileSystemClient
        local_temp_dir: Local directory for temp files

    Returns:
        Tuple of (combined_dataframe, list_of_filenames)
        Returns (None, []) if no unprocessed deltas

    """
    unprocessed = get_unprocessed_deltas(client)

    if not unprocessed:
        logger.info("No unprocessed deltas found")
        return None, []

    logger.info(f"Found {len(unprocessed)} unprocessed delta(s)")

    dataframes = []
    filenames = []

    for delta in unprocessed:
        azure_path = f"{RAW_DELTAS_DIR}/{delta['filename']}"
        logger.info(f"Downloading delta: {delta['filename']} ({delta['rows']:,} rows)")

        try:
            df = _download_parquet(client, azure_path, local_temp_dir)
            dataframes.append(df)
            filenames.append(delta["filename"])
        except Exception as e:
            logger.warning(f"Could not download {delta['filename']}: {e}")

    if not dataframes:
        return None, []

    combined = pd.concat(dataframes, ignore_index=True, sort=False)
    logger.info(f"Combined {len(filenames)} deltas: {len(combined):,} total rows")

    return combined, filenames


def mark_deltas_processed(
    client: FileSystemClient,
    filenames: list[str],
    rows_uploaded: int,
    max_notific: int,
) -> None:
    """
    Mark delta files as processed in DW state.

    Updates dw_state.json to record that these deltas have been
    loaded into the data warehouse, preventing re-processing.

    Args:
        client: Azure FileSystemClient
        filenames: List of processed delta filenames
        rows_uploaded: Number of rows uploaded to DW
        max_notific: Maximum NU_NOTIFIC value in uploaded data

    """
    dw_state = load_dw_state(client)

    if "processed_deltas" not in dw_state:
        dw_state["processed_deltas"] = []

    dw_state["processed_deltas"].extend(filenames)
    dw_state["last_max_notific"] = max_notific
    dw_state["last_upload_timestamp"] = datetime.now().isoformat()
    dw_state["total_rows"] = dw_state.get("total_rows", 0) + rows_uploaded

    save_dw_state(client, dw_state)
