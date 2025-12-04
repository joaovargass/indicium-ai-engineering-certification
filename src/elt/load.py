"""Data loading module for Azure storage and Data Warehouse."""

import json
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient, FileSystemClient
from dotenv import load_dotenv

from common.config import (
    DW_FULLY_QUALIFIED_TABLE,
    DW_STATE_PATH,
    FILE_SYSTEM_NAME,
    PRIMARY_KEY_FIELD,
    RAW_DELTAS_DIR,
    RAW_STATE_PATH,
    STORAGE_ACCOUNT_NAME,
)

load_dotenv()


def get_client() -> FileSystemClient:
    """Initialize and return Azure Data Lake client."""
    credential = DefaultAzureCredential()
    service_client = DataLakeServiceClient(
        account_url=f"https://{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
        credential=credential,
        connection_timeout=600,  # 10 minutes
        read_timeout=600,  # 10 minutes
    )
    return service_client.get_file_system_client(FILE_SYSTEM_NAME)


def _read_json(client: FileSystemClient, path: str) -> dict | None:
    """Read JSON file from Azure."""
    try:
        file_client = client.get_file_client(path)
        content = file_client.download_file().readall().decode("utf-8")
        return json.loads(content)
    except ResourceNotFoundError:
        return None
    except Exception as e:
        print(f"Warning: Could not read {path}: {e}")
        return None


def _write_json(client: FileSystemClient, path: str, data: dict) -> None:
    """Write JSON file to Azure."""
    file_client = client.get_file_client(path)
    content = json.dumps(data, indent=2)
    file_client.upload_data(content.encode("utf-8"), overwrite=True)


def _delete_file(client: FileSystemClient, path: str) -> bool:
    """Delete a file from Azure."""
    try:
        file_client = client.get_file_client(path)
        file_client.delete_file()
        return True
    except ResourceNotFoundError:
        return False


def _delete_directory(client: FileSystemClient, dir_path: str) -> None:
    """Delete all files in a directory from Azure."""
    try:
        paths = client.get_paths(path=dir_path, recursive=True)
        for path in paths:
            if not path.is_directory:
                try:
                    file_client = client.get_file_client(path.name)
                    file_client.delete_file()
                except Exception as e:
                    print(f"Warning: Could not delete {path.name}: {e}")
    except ResourceNotFoundError:
        pass
    except Exception as e:
        print(f"Warning: Could not delete directory {dir_path}: {e}")


def _get_default_raw_state() -> dict:
    """Return default raw state structure."""
    return {
        "processed_years": [],
        "current_year": None,
        "last_vivo_date": None,
        "deltas": [],
    }


def _get_default_dw_state() -> dict:
    """Return default DW state structure."""
    return {
        "last_max_notific": 0,
        "processed_deltas": [],
        "last_upload_timestamp": None,
        "total_rows": 0,
    }


def load_raw_state(client: FileSystemClient) -> dict:
    """Load raw data state from Azure."""
    state = _read_json(client, RAW_STATE_PATH)
    if state is None:
        print("Raw state file not found, creating new state")
        return _get_default_raw_state()
    return state


def save_raw_state(client: FileSystemClient, state: dict) -> None:
    """Save raw data state to Azure."""
    _write_json(client, RAW_STATE_PATH, state)
    print(f"Raw state saved: {len(state.get('deltas', []))} deltas tracked")


def load_dw_state(client: FileSystemClient) -> dict:
    """Load DW state from Azure."""
    state = _read_json(client, DW_STATE_PATH)
    if state is None:
        print("DW state file not found, creating new state")
        return _get_default_dw_state()
    return state


def save_dw_state(client: FileSystemClient, state: dict) -> None:
    """Save DW state to Azure."""
    _write_json(client, DW_STATE_PATH, state)
    print(f"DW state saved: last_max_notific={state.get('last_max_notific')}")


def reset_all_state(local_data_dir: Path | None = None) -> None:
    """Reset all Azure state files, deltas, DW table, and optionally local files."""
    client = get_client()

    # Delete all delta files (including orphaned ones not in state)
    try:
        _delete_directory(client, RAW_DELTAS_DIR)
        print("Deleted all Azure delta files")
    except Exception as e:
        print(f"Warning: Could not delete delta files: {e}")

    if _delete_file(client, RAW_STATE_PATH):
        print("Deleted raw state file")

    if _delete_file(client, DW_STATE_PATH):
        print("Deleted DW state file")

    # Clean up any leftover staging directories
    try:
        _delete_directory(client, "staging")
        print("Deleted staging directories")
    except Exception as e:
        print(f"Warning: Could not delete staging directories: {e}")

    # Clear DW table
    try:
        conn_str, server, db = _get_sql_connection()
        from sqlalchemy import create_engine, text

        engine = create_engine(conn_str, isolation_level="AUTOCOMMIT")
        schema, tbl = DW_FULLY_QUALIFIED_TABLE.rsplit(".", 1)
        with engine.connect() as conn:
            conn.execute(text(f"TRUNCATE TABLE {schema}.{tbl}"))
        engine.dispose()
        print(f"Cleared DW table: {DW_FULLY_QUALIFIED_TABLE}")
    except Exception as e:
        print(f"Warning: Could not clear DW table: {e}")

    if local_data_dir and local_data_dir.exists():
        _delete_local_files(local_data_dir)


def _delete_local_files(data_dir: Path) -> None:
    """Delete all local data files and temp directories."""
    import shutil

    if not data_dir.exists():
        return

    for year_dir in data_dir.iterdir():
        if year_dir.is_dir() and year_dir.name.isdigit():
            shutil.rmtree(year_dir)
            print(f"Deleted year directory: {year_dir.name}")

    temp_dirs = ["temp", "temp_azure_read"]
    for temp_name in temp_dirs:
        temp_dir = data_dir / temp_name
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"Deleted {temp_name} directory")

    project_temp = data_dir.parent.parent / "temp"
    if project_temp.exists():
        shutil.rmtree(project_temp)
        print("Deleted project temp directory")

    cleaned_dir = data_dir.parent / "cleaned"
    if cleaned_dir.exists():
        shutil.rmtree(cleaned_dir)
        print("Deleted cleaned directory")


def _generate_delta_filename(year: int, date_str: str) -> str:
    """Generate a unique delta filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"delta_{year}_{date_str}_{timestamp}.parquet"


def _upload_parquet(
    client: FileSystemClient,
    df: pd.DataFrame,
    azure_path: str,
    local_temp_dir: Path,
) -> None:
    """Upload DataFrame as parquet to Azure."""
    temp_file = local_temp_dir / "temp_upload.parquet"
    temp_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(temp_file, index=False, engine="pyarrow")

    file_client = client.get_file_client(azure_path)
    with open(temp_file, "rb") as f:
        file_client.upload_data(f.read(), overwrite=True)

    temp_file.unlink(missing_ok=True)
    print(f"Uploaded {len(df):,} rows to {azure_path}")


def _download_parquet(
    client: FileSystemClient,
    azure_path: str,
    local_temp_dir: Path,
) -> pd.DataFrame:
    """Download parquet from Azure."""
    file_client = client.get_file_client(azure_path)
    temp_file = local_temp_dir / "temp_download.parquet"
    temp_file.parent.mkdir(parents=True, exist_ok=True)

    with open(temp_file, "wb") as f:
        download = file_client.download_file()
        f.write(download.readall())

    df = pd.read_parquet(temp_file)
    temp_file.unlink(missing_ok=True)
    return df


def _cleanup_vivo_deltas(
    client: FileSystemClient, year: int, raw_state: dict
) -> tuple[dict, bool]:
    """Remove vivo deltas for a year transitioning to congelado."""
    vivo_deltas = [
        d
        for d in raw_state.get("deltas", [])
        if d.get("type") == "vivo" and d.get("year") == year
    ]

    if not vivo_deltas:
        return raw_state, False

    dw_state = load_dw_state(client)
    processed_by_dw = set(dw_state.get("processed_deltas", []))
    vivo_filenames = {d["filename"] for d in vivo_deltas}
    any_vivo_processed = bool(vivo_filenames & processed_by_dw)

    print(f"Year {year} transitioning from vivo to congelado")
    print(f"Removing {len(vivo_deltas)} old vivo delta(s)...")

    for delta in vivo_deltas:
        azure_path = f"{RAW_DELTAS_DIR}/{delta['filename']}"
        if _delete_file(client, azure_path):
            print(f"  Deleted: {delta['filename']}")

    raw_state["deltas"] = [
        d
        for d in raw_state["deltas"]
        if not (d.get("type") == "vivo" and d.get("year") == year)
    ]

    if any_vivo_processed:
        dw_state["processed_deltas"] = [
            f for f in dw_state["processed_deltas"] if f not in vivo_filenames
        ]
        save_dw_state(client, dw_state)
        print(f"  Cleaned up DW state (removed {len(vivo_filenames)} old entries)")

    return raw_state, any_vivo_processed


def upload_congelado_delta(
    client: FileSystemClient,
    df: pd.DataFrame,
    year: int,
    local_temp_dir: Path,
    raw_state: dict,
) -> dict:
    """Upload congelado (frozen year) data as a delta file."""
    if year in raw_state.get("processed_years", []):
        print(f"Year {year} already processed, skipping")
        return raw_state

    raw_state, vivo_was_in_dw = _cleanup_vivo_deltas(client, year, raw_state)

    filename = f"congelado_{year}.parquet"
    azure_path = f"{RAW_DELTAS_DIR}/{filename}"

    if PRIMARY_KEY_FIELD in df.columns:
        df[PRIMARY_KEY_FIELD] = pd.to_numeric(df[PRIMARY_KEY_FIELD], errors="coerce")
        max_val = df[PRIMARY_KEY_FIELD].max()
        max_notific = int(max_val) if pd.notna(max_val) else 0
    else:
        max_notific = 0

    _upload_parquet(client, df, azure_path, local_temp_dir)

    if "processed_years" not in raw_state:
        raw_state["processed_years"] = []
    raw_state["processed_years"].append(year)
    raw_state["processed_years"] = sorted(raw_state["processed_years"])

    raw_state["deltas"].append(
        {
            "filename": filename,
            "year": year,
            "type": "congelado",
            "max_notific": max_notific,
            "rows": len(df),
            "uploaded_at": datetime.now().isoformat(),
        }
    )

    if vivo_was_in_dw:
        dw_state = load_dw_state(client)
        dw_state["processed_deltas"].append(filename)
        save_dw_state(client, dw_state)
        print(f"  Marked {filename} as already processed (data from vivo)")

    return raw_state


def upload_vivo_delta(
    client: FileSystemClient,
    df: pd.DataFrame,
    year: int,
    date_str: str,
    local_temp_dir: Path,
    raw_state: dict,
) -> dict:
    """Upload vivo (live year) data as incremental delta."""
    last_max = 0
    for delta in raw_state.get("deltas", []):
        if delta.get("type") == "vivo" and delta.get("year") == year:
            last_max = max(last_max, delta.get("max_notific", 0))

    if PRIMARY_KEY_FIELD in df.columns:
        df[PRIMARY_KEY_FIELD] = pd.to_numeric(df[PRIMARY_KEY_FIELD], errors="coerce")
        new_records = df[df[PRIMARY_KEY_FIELD] > last_max].copy()
    else:
        new_records = df

    if len(new_records) == 0:
        print("No new vivo records to upload")
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
    raw_state["last_vivo_date"] = date_str
    raw_state["deltas"].append(
        {
            "filename": filename,
            "year": year,
            "type": "vivo",
            "date": date_str,
            "max_notific": max_notific,
            "rows": len(new_records),
            "uploaded_at": datetime.now().isoformat(),
        }
    )

    return raw_state


def get_unprocessed_deltas(client: FileSystemClient) -> list[dict]:
    """Get list of delta files not yet processed by DW."""
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
    """Download only unprocessed delta files and combine them."""
    unprocessed = get_unprocessed_deltas(client)

    if not unprocessed:
        print("No unprocessed deltas found")
        return None, []

    print(f"Found {len(unprocessed)} unprocessed delta(s)")

    dataframes = []
    filenames = []

    for delta in unprocessed:
        azure_path = f"{RAW_DELTAS_DIR}/{delta['filename']}"
        print(f"Downloading delta: {delta['filename']} ({delta['rows']:,} rows)")

        try:
            df = _download_parquet(client, azure_path, local_temp_dir)
            dataframes.append(df)
            filenames.append(delta["filename"])
        except Exception as e:
            print(f"Warning: Could not download {delta['filename']}: {e}")

    if not dataframes:
        return None, []

    combined = pd.concat(dataframes, ignore_index=True, sort=False)
    print(f"Combined {len(filenames)} deltas: {len(combined):,} total rows")

    return combined, filenames


def mark_deltas_processed(
    client: FileSystemClient,
    filenames: list[str],
    rows_uploaded: int,
    max_notific: int,
) -> None:
    """Mark delta files as processed in DW state."""
    dw_state = load_dw_state(client)

    if "processed_deltas" not in dw_state:
        dw_state["processed_deltas"] = []

    dw_state["processed_deltas"].extend(filenames)
    dw_state["last_max_notific"] = max_notific
    dw_state["last_upload_timestamp"] = datetime.now().isoformat()
    dw_state["total_rows"] = dw_state.get("total_rows", 0) + rows_uploaded

    save_dw_state(client, dw_state)


def _get_sql_connection() -> tuple[str, str, str]:
    """Build SQL connection string from environment."""
    server = os.getenv("AZURE_SYNAPSE_SQL_ENDPOINT") or os.getenv("AZURE_SQL_SERVER")
    db = os.getenv("AZURE_SQL_POOL_NAME") or os.getenv("AZURE_SQL_DATABASE")
    user = os.getenv("AZURE_SQL_ADMIN_USER")
    password = os.getenv("AZURE_SQL_ADMIN_PASSWORD")

    if not server or not db:
        raise ValueError("Azure SQL connection variables not set")

    if user and password:
        conn_str = (
            f"mssql+pyodbc://{quote_plus(user)}:{quote_plus(password)}@{server}/"
            f"{quote_plus(db)}?"
            f"driver=ODBC+Driver+18+for+SQL+Server&"
            f"Encrypt=yes&TrustServerCertificate=no&AutoCommit=Yes"
        )
    else:
        conn_str = (
            f"mssql+pyodbc://{server}/{quote_plus(db)}?"
            f"driver=ODBC+Driver+18+for+SQL+Server&"
            f"Authentication=ActiveDirectoryDefault&"
            f"Encrypt=yes&TrustServerCertificate=no&AutoCommit=Yes"
        )

    return conn_str, server, db


def read_from_dw(
    query: str | None = None,
    table: str = DW_FULLY_QUALIFIED_TABLE,
) -> pd.DataFrame:
    """
    Read data from Azure SQL Data Warehouse.

    Args:
        query: Optional SQL query string. If None, reads entire table.
        table: Table name to read from (default: DW_FULLY_QUALIFIED_TABLE).

    Returns:
        DataFrame with data from DW.

    """
    try:
        from sqlalchemy import create_engine
    except ImportError as e:
        raise ImportError("sqlalchemy and pyodbc required") from e

    conn_str, server, db = _get_sql_connection()
    engine = create_engine(conn_str, isolation_level="AUTOCOMMIT")

    if query is None:
        schema = os.getenv("AZURE_SQL_SCHEMA", "dbo")
        if "." in table:
            schema, tbl = table.rsplit(".", 1)
        else:
            tbl = table
        query = f"SELECT * FROM {schema}.{tbl}"

    print(f"Reading from {server}/{db}")
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    engine.dispose()
    print(f"Loaded {len(df):,} rows")
    return df


def load_srag_data() -> pd.DataFrame:
    """Load SRAG data from cache or DW. Raises RuntimeError if unavailable."""
    from pathlib import Path

    project_root = Path(__file__).resolve().parent.parent.parent
    cache_dir = project_root / "data" / "cleaned"
    cache_path = cache_dir / "dash_cache.parquet"

    if cache_path.exists():
        return pd.read_parquet(cache_path)

    try:
        df = read_from_dw()
    except Exception as e:
        raise RuntimeError(
            f"Failed to load data from DW and no cache found: {e}"
        ) from e

    cache_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache_path, index=False)

    return df


def save_to_dw(
    df: pd.DataFrame,
    table: str = DW_FULLY_QUALIFIED_TABLE,
    if_exists: str = "append",
) -> int:
    """
    Save DataFrame to Azure Synapse using COPY INTO.

    Requires AZURE_STORAGE_KEY environment variable.
    """
    storage_key = os.getenv("AZURE_STORAGE_KEY")
    if not storage_key:
        raise ValueError("AZURE_STORAGE_KEY not set. Run scripts/azure-setup.sh")

    return _save_to_dw_copy_into(df, table, if_exists, storage_key)


def _save_to_dw_copy_into(
    df: pd.DataFrame,
    table: str,
    if_exists: str,
    storage_key: str,
) -> int:
    """Save DataFrame using COPY INTO (fastest for large datasets)."""
    import uuid

    try:
        from sqlalchemy import create_engine, text
    except ImportError as e:
        raise ImportError("sqlalchemy and pyodbc required") from e

    schema = os.getenv("AZURE_SQL_SCHEMA", "dbo")
    if "." in table:
        schema, tbl = table.rsplit(".", 1)
    else:
        tbl = table

    if PRIMARY_KEY_FIELD in df.columns:
        df = df.copy()
        df[PRIMARY_KEY_FIELD] = pd.to_numeric(
            df[PRIMARY_KEY_FIELD], errors="coerce"
        ).astype("Int64")

    conn_str, server, db = _get_sql_connection()
    print(f"Connecting to {server}/{db}")
    print(f"COPY INTO: Loading {len(df):,} rows to {schema}.{tbl} ({if_exists} mode)")

    client = get_client()
    local_temp_dir = Path("data/raw/temp")
    local_temp_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    upload_id = str(uuid.uuid4())[:8]
    staging_dir = f"staging/{timestamp}_{upload_id}"

    engine = create_engine(conn_str, isolation_level="AUTOCOMMIT")
    parquet_files = []

    try:
        print("Uploading to ADLS Gen2 staging...")
        file_chunk_size = 500000

        for i, start in enumerate(range(0, len(df), file_chunk_size)):
            chunk = df.iloc[start : start + file_chunk_size]
            parquet_path = f"{staging_dir}/part_{i:04d}.parquet"
            _upload_parquet(client, chunk, parquet_path, local_temp_dir)
            parquet_files.append(parquet_path)

        print(f"Staged {len(parquet_files)} files, executing COPY INTO...")

        with engine.connect() as conn:
            if if_exists == "replace":
                conn.execute(
                    text(
                        f"IF OBJECT_ID('{schema}.{tbl}', 'U') IS NOT NULL "
                        f"DROP TABLE {schema}.{tbl}"
                    )
                )

            adls_url = (
                f"https://{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net/"
                f"{FILE_SYSTEM_NAME}/{staging_dir}/*.parquet"
            )

            copy_sql = f"""
            COPY INTO {schema}.{tbl}
            FROM '{adls_url}'
            WITH (
                FILE_TYPE = 'PARQUET',
                CREDENTIAL = (IDENTITY = 'Storage Account Key', SECRET = '{storage_key}'),
                AUTO_CREATE_TABLE = 'ON'
            )
            """

            conn.execute(text(copy_sql))

            result = conn.execute(text(f"SELECT COUNT(*) FROM {schema}.{tbl}"))
            row_count = result.scalar()

            if if_exists == "replace" and PRIMARY_KEY_FIELD in df.columns:
                try:
                    conn.execute(
                        text(
                            f"ALTER TABLE {schema}.{tbl} "
                            f"ALTER COLUMN {PRIMARY_KEY_FIELD} BIGINT NOT NULL"
                        )
                    )
                    conn.execute(
                        text(
                            f"ALTER TABLE {schema}.{tbl} "
                            f"ADD CONSTRAINT PK_{tbl} PRIMARY KEY NONCLUSTERED "
                            f"({PRIMARY_KEY_FIELD}) NOT ENFORCED"
                        )
                    )
                    print(f"  Added PK constraint on {PRIMARY_KEY_FIELD}")
                except Exception as pk_err:
                    print(f"  PK constraint skipped: {pk_err}")

        print(f"COPY INTO complete: {row_count:,} rows loaded")
        return row_count

    finally:
        # Clean up staging directory
        print("Cleaning up staging files...")
        _delete_directory(client, staging_dir)
        print(f"Deleted staging directory: {staging_dir}")
        engine.dispose()
