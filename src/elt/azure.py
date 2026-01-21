"""Azure Data Lake client operations."""

import json
from pathlib import Path

import pandas as pd
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient, FileSystemClient

from common.config import (
    CONNECTION_TIMEOUT_SECONDS,
    FILE_SYSTEM_NAME,
    READ_TIMEOUT_SECONDS,
    STORAGE_ACCOUNT_NAME,
)
from common.logging import logger


def get_client() -> FileSystemClient:
    """Initialize and return Azure Data Lake client."""
    credential = DefaultAzureCredential()
    service_client = DataLakeServiceClient(
        account_url=f"https://{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
        credential=credential,
        connection_timeout=CONNECTION_TIMEOUT_SECONDS,
        read_timeout=READ_TIMEOUT_SECONDS,
    )
    return service_client.get_file_system_client(FILE_SYSTEM_NAME)


def _read_json(client: FileSystemClient, path: str) -> dict | None:
    """
    Read JSON file from Azure Data Lake.

    Args:
        client: Azure FileSystemClient
        path: Path to JSON file in ADLS

    Returns:
        Parsed dict or None if file not found or error

    """
    try:
        file_client = client.get_file_client(path)
        content = file_client.download_file().readall().decode("utf-8")
        return json.loads(content)
    except ResourceNotFoundError:
        return None
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.warning(f"Could not parse {path}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Could not read {path}: {e}")
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
    """
    Delete all files in a directory from Azure Data Lake.

    Args:
        client: Azure FileSystemClient
        dir_path: Directory path to delete

    """
    try:
        paths = client.get_paths(path=dir_path, recursive=True)
        for path in paths:
            if not path.is_directory:
                try:
                    file_client = client.get_file_client(path.name)
                    file_client.delete_file()
                except ResourceNotFoundError:
                    pass
                except Exception as e:
                    logger.warning(f"Could not delete {path.name}: {e}")
    except ResourceNotFoundError:
        pass
    except Exception as e:
        logger.warning(f"Could not delete directory {dir_path}: {e}")


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
    logger.info(f"Uploaded {len(df):,} rows to {azure_path}")


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
