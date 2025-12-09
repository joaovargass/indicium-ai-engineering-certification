"""ELT pipeline module for running incremental data updates."""

import sys
from datetime import datetime

import pandas as pd

from common.config import (
    CACHE_DIR,
    DASH_CACHE_PATH,
    FULL_REFRESH,
    PRIMARY_KEY_FIELD,
    PROJECT_ROOT,
    SRC_PATH,
)

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
from elt.extract import extract_data, fetch_web_dates, setup_dirs  # noqa: E402
from elt.load import (  # noqa: E402
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


def run_incremental_elt() -> str:
    """
    Run incremental ELT pipeline and return extraction date.

    Returns:
        ISO format date string of when extraction completed

    """
    data_dir, current_year, years = setup_dirs(PROJECT_ROOT)
    local_temp_dir = data_dir / "temp"
    local_temp_dir.mkdir(exist_ok=True)

    client = get_client()
    raw_state = load_raw_state(client)
    processed_years = raw_state.get("processed_years", [])
    last_live_date = raw_state.get("last_live_date")

    freeze_date, live_date = fetch_web_dates(
        FULL_REFRESH, processed_years, years, current_year
    )

    extract_result = extract_data(
        data_dir=data_dir,
        current_year=current_year,
        years=years,
        processed_years=processed_years,
        last_live_date=last_live_date,
        freeze_date_str=freeze_date,
        live_date_str=live_date,
        full_refresh=FULL_REFRESH,
    )

    initial_deltas_count = len(raw_state.get("deltas", []))

    for year, df in extract_result["frozen_dfs"].items():
        raw_state = upload_frozen_delta(
            client=client,
            df=df,
            year=year,
            local_temp_dir=local_temp_dir,
            raw_state=raw_state,
        )

    if extract_result["live_df"] is not None and extract_result["is_live_new"]:
        live_df = extract_result["live_df"]
        live_date_str = extract_result["live_date"]
        raw_state = upload_live_delta(
            client=client,
            df=live_df,
            year=current_year,
            date_str=live_date_str,
            local_temp_dir=local_temp_dir,
            raw_state=raw_state,
        )

    final_deltas_count = len(raw_state.get("deltas", []))
    if final_deltas_count > initial_deltas_count:
        save_raw_state(client, raw_state)

    combined_df, delta_files = download_unprocessed_deltas(client, local_temp_dir)

    if combined_df is not None and len(combined_df) > 0:
        df_essential = select_essential(combined_df)
        df_cleaned = clean_data(df_essential)

        if PRIMARY_KEY_FIELD in df_cleaned.columns:
            df_cleaned[PRIMARY_KEY_FIELD] = pd.to_numeric(
                df_cleaned[PRIMARY_KEY_FIELD], errors="coerce"
            )
            max_val = df_cleaned[PRIMARY_KEY_FIELD].max()
            max_notific = int(max_val) if pd.notna(max_val) else 0
        else:
            max_notific = 0

        rows = save_to_dw(df_cleaned)
        mark_deltas_processed(client, delta_files, rows, max_notific)
        new_data_loaded = True
    else:
        new_data_loaded = False

    # Update local cache only if new data was loaded or cache doesn't exist
    if new_data_loaded or not DASH_CACHE_PATH.exists():
        try:
            print("Updating local cache from DW...")
            full_df = read_from_dw()
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            full_df.to_parquet(DASH_CACHE_PATH, index=False)
            print(
                f"Local cache updated: {len(full_df):,} rows saved to {DASH_CACHE_PATH.name}"
            )
        except Exception as e:
            print(f"Warning: Could not update local cache: {e}")
    else:
        print("No new data loaded, local cache unchanged")

    extraction_date = datetime.now().isoformat()
    update_extraction_date(client, extraction_date)

    return extraction_date
