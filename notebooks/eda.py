"""Main EDA pipeline with incremental processing."""

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from common.config import FULL_REFRESH, PRIMARY_KEY_FIELD, RESET
from elt.extract import (
    extract_data,
    fetch_web_dates,
    setup_dirs,
)
from elt.load import (
    download_unprocessed_deltas,
    get_client,
    load_dw_state,
    load_raw_state,
    mark_deltas_processed,
    reset_all_state,
    save_raw_state,
    save_to_dw,
    upload_congelado_delta,
    upload_vivo_delta,
)
from elt.transform import clean_data, select_essential


def _run_extract(
    data_dir: Path,
    current_year: int,
    years: list[int],
) -> dict:
    """
    Extract stage: download new data from source.

    Only downloads what's not already in Azure (based on raw state).
    """
    print("=" * 80)
    print("STAGE: EXTRACT")
    print("=" * 80)

    client = get_client()
    raw_state = load_raw_state(client)
    processed_years = raw_state.get("processed_years", [])
    last_vivo_date = raw_state.get("last_vivo_date")

    print(f"Processed years in Azure: {processed_years}")
    print(f"Last vivo date: {last_vivo_date}")

    freeze_date, live_date = fetch_web_dates(
        FULL_REFRESH, processed_years, years, current_year
    )

    print(f"Freeze date from web: {freeze_date}")
    print(f"Live date from web: {live_date}")

    result = extract_data(
        data_dir=data_dir,
        current_year=current_year,
        years=years,
        processed_years=processed_years,
        last_vivo_date=last_vivo_date,
        freeze_date_str=freeze_date,
        live_date_str=live_date,
        full_refresh=FULL_REFRESH,
    )

    print(f"\nExtracted: {len(result['congelado_dfs'])} congelado years")
    if result["vivo_df"] is not None:
        print(
            f"Extracted vivo: {len(result['vivo_df']):,} rows (new={result['is_vivo_new']})"
        )

    print()
    return result


def _run_load(
    extract_result: dict,
    current_year: int,
    local_temp_dir: Path,
) -> None:
    """
    Load stage: upload new data to Azure as delta files.

    Only uploads what's new (not already tracked in raw state).
    """
    print("=" * 80)
    print("STAGE: LOAD")
    print("=" * 80)

    client = get_client()
    raw_state = load_raw_state(client)
    initial_deltas_count = len(raw_state.get("deltas", []))

    for year, df in extract_result["congelado_dfs"].items():
        print(f"\nUploading congelado {year}: {len(df):,} rows")
        raw_state = upload_congelado_delta(
            client=client,
            df=df,
            year=year,
            local_temp_dir=local_temp_dir,
            raw_state=raw_state,
        )

    if extract_result["vivo_df"] is not None and extract_result["is_vivo_new"]:
        vivo_df = extract_result["vivo_df"]
        vivo_date = extract_result["vivo_date"]
        print(f"\nUploading vivo {current_year}: {len(vivo_df):,} rows")
        raw_state = upload_vivo_delta(
            client=client,
            df=vivo_df,
            year=current_year,
            date_str=vivo_date,
            local_temp_dir=local_temp_dir,
            raw_state=raw_state,
        )

    final_deltas_count = len(raw_state.get("deltas", []))
    if final_deltas_count > initial_deltas_count:
        save_raw_state(client, raw_state)
    else:
        print("No new data uploaded, state unchanged")
    print()


def _run_transform(local_temp_dir: Path) -> None:
    """
    Transform stage: process only unprocessed delta files.

    Downloads only deltas not yet in DW, transforms, and loads to DW.
    """
    print("=" * 80)
    print("STAGE: TRANSFORM")
    print("=" * 80)

    client = get_client()
    combined_df, delta_files = download_unprocessed_deltas(client, local_temp_dir)
    
    # Get state info after download (avoids duplicate load_dw_state call)
    dw_state = load_dw_state(client)
    print(f"DW state: {len(dw_state.get('processed_deltas', []))} deltas processed")
    print(f"Last max notific: {dw_state.get('last_max_notific', 0)}")

    if combined_df is None or len(combined_df) == 0:
        print("No new data to transform")
        return

    print(
        f"\nTransforming {len(combined_df):,} new records from {len(delta_files)} delta(s)"
    )

    df_essential = select_essential(combined_df)
    df_cleaned = clean_data(df_essential)

    print(f"\nCleaned dataset: {len(df_cleaned):,} rows")

    if PRIMARY_KEY_FIELD in df_cleaned.columns:
        df_cleaned[PRIMARY_KEY_FIELD] = pd.to_numeric(
            df_cleaned[PRIMARY_KEY_FIELD], errors="coerce"
        )
        max_notific = int(df_cleaned[PRIMARY_KEY_FIELD].max())
    else:
        max_notific = 0

    rows = save_to_dw(df_cleaned)
    mark_deltas_processed(client, delta_files, rows, max_notific)

    print()


def _run_standalone(local_temp_dir: Path) -> None:
    """Run standalone: full refresh to DW from local cleaned file."""
    print("=" * 80)
    print("STANDALONE MODE")
    print("=" * 80)

    cleaned_path = PROJECT_ROOT / "data" / "cleaned" / "srag_cleaned.parquet"

    if cleaned_path.exists():
        print(f"Reading: {cleaned_path}")
        df = pd.read_parquet(cleaned_path)
        print(f"Loaded {len(df):,} rows")
    else:
        print("Cleaned file not found. Run ELT first.")
        return

    save_to_dw(df, if_exists="replace")
    print("Done")


def main() -> None:
    """Execute main pipeline."""
    stages_config = "etl"

    print(f"Pipeline mode: {stages_config}")
    print(f"Full refresh: {FULL_REFRESH}")
    print(f"Reset: {RESET}")
    print()

    data_dir, current_year, years = setup_dirs(PROJECT_ROOT)
    local_temp_dir = data_dir / "temp"

    if RESET:
        print("Resetting all state and local files...")
        reset_all_state(local_data_dir=data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)

    local_temp_dir.mkdir(exist_ok=True)

    if stages_config.lower() == "s":
        _run_standalone(local_temp_dir)
        return

    stages = stages_config.lower()
    run_extract = "e" in stages
    run_load = "l" in stages
    run_transform = "t" in stages

    print(f"Stages: E={run_extract}, L={run_load}, T={run_transform}")
    print()

    extract_result = None

    try:
        if run_extract:
            extract_result = _run_extract(data_dir, current_year, years)

        if run_load:
            if extract_result is None:
                print("No extract result. Running extract first...")
                extract_result = _run_extract(data_dir, current_year, years)
            _run_load(extract_result, current_year, local_temp_dir)

        if run_transform:
            _run_transform(local_temp_dir)

        print("=" * 80)
        print("PIPELINE COMPLETED")
        print("=" * 80)

    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
