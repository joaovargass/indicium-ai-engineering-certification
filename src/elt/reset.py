"""Reset operations for ELT pipeline."""

from pathlib import Path

from common.config import (
    DW_FULLY_QUALIFIED_TABLE,
    DW_STATE_PATH,
    RAW_DELTAS_DIR,
    RAW_STATE_PATH,
)
from elt.azure import _delete_directory, _delete_file, get_client
from elt.dw import _get_sql_connection


def reset_all_state(local_data_dir: Path | None = None) -> None:
    """Reset all Azure state files, deltas, DW table, and optionally local files."""
    client = get_client()

    try:
        _delete_directory(client, RAW_DELTAS_DIR)
        print("Deleted all Azure delta files")
    except Exception as e:
        print(f"Warning: Could not delete delta files: {e}")

    if _delete_file(client, RAW_STATE_PATH):
        print("Deleted raw state file")

    if _delete_file(client, DW_STATE_PATH):
        print("Deleted DW state file")

    try:
        _delete_directory(client, "staging")
        print("Deleted staging directories")
    except Exception as e:
        print(f"Warning: Could not delete staging directories: {e}")

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
