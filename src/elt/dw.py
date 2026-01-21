"""Data Warehouse: read/write to Azure Synapse via COPY INTO, staging in ADLS Gen2. Adds PK constraint on replace."""

import os
from datetime import datetime
from urllib.parse import quote_plus

import pandas as pd

from common.config import (
    DW_FULLY_QUALIFIED_TABLE,
    DW_MAX_ROWS,
    DW_UPLOAD_CHUNK_SIZE,
    FILE_SYSTEM_NAME,
    ODBC_DRIVER_SQL_SERVER,
    PRIMARY_KEY_FIELD,
    STORAGE_ACCOUNT_NAME,
    TEMP_DIR,
)
from common.logging import logger
from elt.azure import _delete_directory, _upload_parquet, get_client


def _get_sql_connection() -> tuple[str, str, str]:
    """Build SQL connection string from environment."""
    server = os.getenv("AZURE_SYNAPSE_SQL_ENDPOINT") or os.getenv("AZURE_SQL_SERVER")
    db = os.getenv("AZURE_SQL_POOL_NAME") or os.getenv("AZURE_SQL_DATABASE")
    user = os.getenv("AZURE_SQL_ADMIN_USER")
    password = os.getenv("AZURE_SQL_ADMIN_PASSWORD")

    if not server or not db:
        raise ValueError("Azure SQL connection variables not set")

    driver = ODBC_DRIVER_SQL_SERVER.replace(" ", "+")
    if user and password:
        conn_str = (
            f"mssql+pyodbc://{quote_plus(user)}:{quote_plus(password)}@{server}/"
            f"{quote_plus(db)}?"
            f"driver={driver}&"
            f"Encrypt=yes&TrustServerCertificate=no&AutoCommit=Yes"
        )
    else:
        conn_str = (
            f"mssql+pyodbc://{server}/{quote_plus(db)}?"
            f"driver={driver}&"
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

    logger.info(f"Reading from {server}/{db}")
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    engine.dispose()
    logger.info(f"Loaded {len(df):,} rows")
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

    return _copy_into_dw(df, table, if_exists, storage_key)


def _prepare_for_dw(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare DataFrame for DW upload by converting primary key to proper type.

    Args:
        df: DataFrame to prepare

    Returns:
        Prepared DataFrame with proper column types

    """
    if PRIMARY_KEY_FIELD in df.columns:
        df = df.copy()
        df[PRIMARY_KEY_FIELD] = pd.to_numeric(
            df[PRIMARY_KEY_FIELD], errors="coerce"
        ).astype("Int64")
    return df


def _upload_to_staging(
    client: object,
    df: pd.DataFrame,
    staging_dir: str,
    chunk_size: int,
) -> list[str]:
    """
    Upload DataFrame to ADLS Gen2 staging area in chunks.

    Args:
        client: Azure FileSystemClient
        df: DataFrame to upload
        staging_dir: Target staging directory path
        chunk_size: Number of rows per parquet file

    Returns:
        List of uploaded parquet file paths

    """
    parquet_files = []
    for i, start in enumerate(range(0, len(df), chunk_size)):
        chunk = df.iloc[start : start + chunk_size]
        parquet_path = f"{staging_dir}/part_{i:04d}.parquet"
        _upload_parquet(client, chunk, parquet_path, TEMP_DIR)
        parquet_files.append(parquet_path)
    return parquet_files


def _execute_copy_into(
    conn: object,
    schema: str,
    tbl: str,
    staging_dir: str,
    storage_key: str,
    if_exists: str,
    has_pk: bool,
) -> int:
    """
    Execute COPY INTO SQL command and return row count.

    Args:
        conn: Database connection
        schema: Database schema name
        tbl: Table name
        staging_dir: Staging directory path in ADLS
        storage_key: Azure storage account key
        if_exists: 'append' or 'replace'
        has_pk: Whether DataFrame has primary key column

    Returns:
        Total row count in table after operation

    """
    from sqlalchemy import text

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

    if if_exists == "replace" and has_pk:
        _add_pk_constraint(conn, schema, tbl)

    return row_count


def _add_pk_constraint(conn: object, schema: str, tbl: str) -> None:
    """
    Add primary key constraint to table after COPY INTO.

    Args:
        conn: Database connection
        schema: Database schema name
        tbl: Table name

    """
    from sqlalchemy import text

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
        logger.info(f"  Added PK constraint on {PRIMARY_KEY_FIELD}")
    except Exception as pk_err:
        logger.warning(f"  PK constraint skipped: {pk_err}")


def _copy_into_dw(
    df: pd.DataFrame,
    table: str,
    if_exists: str,
    storage_key: str,
) -> int:
    """
    Save DataFrame using COPY INTO (fastest for large datasets).

    Args:
        df: DataFrame to save
        table: Target table name (can include schema)
        if_exists: 'append' or 'replace'
        storage_key: Azure storage account key

    Returns:
        Total row count in table after operation

    """
    import uuid

    from sqlalchemy import create_engine

    schema = os.getenv("AZURE_SQL_SCHEMA", "dbo")
    if "." in table:
        schema, tbl = table.rsplit(".", 1)
    else:
        tbl = table

    df = _prepare_for_dw(df)
    has_pk = PRIMARY_KEY_FIELD in df.columns

    conn_str, server, db = _get_sql_connection()
    logger.info(f"Connecting to {server}/{db}")
    logger.info(
        f"COPY INTO: Loading {len(df):,} rows to {schema}.{tbl} ({if_exists} mode)"
    )

    client = get_client()
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    upload_id = str(uuid.uuid4())[:8]
    staging_dir = f"staging/{timestamp}_{upload_id}"

    engine = create_engine(conn_str, isolation_level="AUTOCOMMIT")

    try:
        logger.info("Uploading to ADLS Gen2 staging...")
        parquet_files = _upload_to_staging(
            client, df, staging_dir, DW_UPLOAD_CHUNK_SIZE
        )
        logger.info(f"Staged {len(parquet_files)} files, executing COPY INTO...")

        with engine.connect() as conn:
            row_count = _execute_copy_into(
                conn, schema, tbl, staging_dir, storage_key, if_exists, has_pk
            )

        logger.info(f"COPY INTO complete: {row_count:,} rows loaded")
        return row_count

    finally:
        logger.info("Cleaning up staging files...")
        _delete_directory(client, staging_dir)
        logger.debug(f"Deleted staging directory: {staging_dir}")
        engine.dispose()


def trim_dw_to_max_rows(
    table: str = DW_FULLY_QUALIFIED_TABLE,
    max_rows: int | None = None,
) -> None:
    """
    Delete oldest rows (by NU_NOTIFIC) when table count exceeds max_rows.

    Keeps the most recent ~8M rows to cap storage and cost.
    """
    if max_rows is None:
        max_rows = DW_MAX_ROWS
    try:
        from sqlalchemy import create_engine, text
    except ImportError:
        logger.warning("trim_dw_to_max_rows requires sqlalchemy")
        return
    schema = os.getenv("AZURE_SQL_SCHEMA", "dbo")
    if "." in table:
        schema, tbl = table.rsplit(".", 1)
    else:
        tbl = table
    conn_str, server, db = _get_sql_connection()
    engine = create_engine(conn_str, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as conn:
            r = conn.execute(text(f"SELECT COUNT(*) FROM [{schema}].[{tbl}]"))
            cnt = r.scalar()
            if cnt is None or cnt <= max_rows:
                return
            over = int(cnt) - max_rows
            conn.execute(
                text(
                    f"DELETE FROM [{schema}].[{tbl}] WHERE {PRIMARY_KEY_FIELD} IN "
                    f"(SELECT {PRIMARY_KEY_FIELD} FROM (SELECT {PRIMARY_KEY_FIELD}, "
                    f"ROW_NUMBER() OVER (ORDER BY {PRIMARY_KEY_FIELD} ASC) AS rn FROM [{schema}].[{tbl}]) x WHERE rn <= :over)"
                ),
                {"over": over},
            )
            logger.info(f"Trimmed DW to {max_rows:,} rows (removed {over:,} oldest)")
    except Exception as e:
        logger.warning(f"Could not trim DW to {max_rows:,} rows: {e}")
    finally:
        engine.dispose()
