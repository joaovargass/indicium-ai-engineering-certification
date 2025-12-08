"""Data extraction module for SRAG data."""

import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

from common.config import (
    BASE_DOWNLOAD_URL,
    DOWNLOAD_ENABLED,
    OPENDATASUS_URL,
    REQUEST_HEAD_TIMEOUT_SECONDS,
    REQUEST_TIMEOUT_SECONDS,
    START_YEAR,
)


def get_dates(page_url: str, only_live: bool = False) -> tuple[str | None, str | None]:
    """Extract freeze and live dates from OpenDataSUS website."""
    freeze_date_str = None
    live_date_str = None
    date_pattern = r"\d{2}/\d{2}/\d{4}"

    try:
        response = requests.get(page_url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        for text in soup.stripped_strings:
            text_lower = text.lower()
            date_match = re.search(date_pattern, text)

            if date_match:
                date_str = date_match.group(0)
                date_formatted = date_str.replace("/", "-")

                if not only_live:
                    is_congelado = (
                        "congelado" in text_lower
                        and "parquet" in text_lower
                        and not freeze_date_str
                    )
                    if is_congelado:
                        freeze_date_str = date_formatted
                        print(f"Found freeze date: {freeze_date_str}")

                is_vivo = (
                    ("vivo" in text_lower or "ativo" in text_lower)
                    and "csv" in text_lower
                    and not live_date_str
                )
                if is_vivo:
                    live_date_str = date_formatted
                    print(f"Found live date: {live_date_str}")

                if (only_live and live_date_str) or (freeze_date_str and live_date_str):
                    break
    except Exception as e:
        print(f"Error getting dates: {e}")

    return freeze_date_str, live_date_str


def _download_file(
    url: str, file_path: Path, timeout: int = REQUEST_TIMEOUT_SECONDS
) -> bool:
    """Download a file from URL with streaming."""
    session = requests.Session()
    try:
        head = session.head(url, timeout=REQUEST_HEAD_TIMEOUT_SECONDS)
        if head.status_code != 200:
            print(f"File not found: {url}")
            return False

        file_size = int(head.headers.get("content-length", 0))
        file_size_mb = file_size / (1024 * 1024)
        print(f"Downloading: {file_path.name} ({file_size_mb:.1f} MB)...")

        response = session.get(url, timeout=timeout, stream=True)
        response.raise_for_status()

        chunk_size = 1024 * 1024
        downloaded = 0
        last_progress = 0

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if file_size > 0:
                        progress_mb = downloaded / (1024 * 1024)
                        if progress_mb - last_progress >= 10:
                            pct = (downloaded / file_size) * 100
                            print(f"  Progress: {pct:.1f}%")
                            last_progress = progress_mb

        print(f"Downloaded: {file_path}")
        return True
    except Exception as e:
        print(f"Error downloading: {e}")
        return False
    finally:
        session.close()


def setup_dirs(project_root: Path) -> tuple[Path, int, list[int]]:
    """Set up directories and return configuration."""
    data_dir = project_root / "data" / "raw"
    data_dir.mkdir(parents=True, exist_ok=True)

    current_year = datetime.now().year
    years = list(range(START_YEAR, current_year + 1))

    return data_dir, current_year, years


def read_csv(file_path: Path) -> pd.DataFrame:
    """Read CSV file with fallback encoding."""
    try:
        return pd.read_csv(
            file_path,
            sep=";",
            quotechar='"',
            doublequote=True,
            low_memory=False,
            dtype=str,
            encoding="utf-8",
        )
    except (pd.errors.ParserError, UnicodeDecodeError):
        try:
            return pd.read_csv(
                file_path,
                sep=";",
                quotechar='"',
                doublequote=True,
                low_memory=False,
                dtype=str,
                encoding="latin-1",
            )
        except Exception:
            return pd.read_csv(
                file_path,
                sep=";",
                quotechar='"',
                doublequote=True,
                low_memory=False,
                dtype=str,
                encoding="latin-1",
                engine="python",
                on_bad_lines="skip",
            )


def _cleanup_local_live_files(year_dir: Path, year: int) -> None:
    """Remove local CSV files when a year transitions to frozen."""
    csv_files = list(year_dir.glob("*.csv"))
    if csv_files:
        print(f"Year {year} transitioning: removing {len(csv_files)} local CSV file(s)")
        for csv_file in csv_files:
            csv_file.unlink()
            print(f"  Deleted: {csv_file.name}")


def download_frozen(
    data_dir: Path,
    year: int,
    freeze_date_str: str,
    processed_years: list[int],
) -> pd.DataFrame | None:
    """Download frozen data for a specific year."""
    if year in processed_years:
        print(f"Year {year} already processed in Azure, skipping download")
        return None

    year_dir = data_dir / str(year)
    year_dir.mkdir(exist_ok=True)

    _cleanup_local_live_files(year_dir, year)

    if not DOWNLOAD_ENABLED:
        parquet_files = list(year_dir.glob("*.parquet"))
        if parquet_files:
            print(f"Using local file for {year}: {parquet_files[0].name}")
            return pd.read_parquet(parquet_files[0])
        print(f"No local file for {year} and download disabled")
        return None

    existing = list(year_dir.glob("*.parquet"))
    if existing:
        print(f"Found local parquet for {year}: {existing[0].name}")
        return pd.read_parquet(existing[0])

    year_str = str(year)[2:]
    filename = f"INFLUD{year_str}-{freeze_date_str}.parquet"
    url = f"{BASE_DOWNLOAD_URL}/{year}/{filename}"
    file_path = year_dir / filename

    if _download_file(url, file_path):
        return pd.read_parquet(file_path)

    return None


def _get_local_live_date(year_dir: Path) -> str | None:
    """Extract date from local live CSV filename."""
    csv_files = list(year_dir.glob("*.csv"))
    if not csv_files:
        return None
    match = re.search(r"(\d{2}-\d{2}-\d{4})", csv_files[0].name)
    return match.group(1) if match else None


def download_live(
    data_dir: Path,
    year: int,
    live_date_str: str,
    last_live_date: str | None,
) -> tuple[pd.DataFrame | None, bool]:
    """
    Download live data for current year.

    Returns:
        Tuple of (DataFrame or None, is_new_data: bool)

    """
    year_dir = data_dir / str(year)
    year_dir.mkdir(exist_ok=True)

    local_date = _get_local_live_date(year_dir)

    if local_date == live_date_str:
        print(f"Local live file already has latest date ({live_date_str})")
        csv_files = list(year_dir.glob("*.csv"))
        if csv_files:
            is_new = last_live_date != live_date_str
            return read_csv(csv_files[0]), is_new
        return None, False

    if last_live_date == live_date_str:
        print(f"Live date unchanged in Azure ({live_date_str})")
        csv_files = list(year_dir.glob("*.csv"))
        if csv_files:
            return read_csv(csv_files[0]), False
        return None, False

    if not DOWNLOAD_ENABLED:
        csv_files = list(year_dir.glob("*.csv"))
        if csv_files:
            print(f"Using local CSV for {year}: {csv_files[0].name}")
            return read_csv(csv_files[0]), True
        print(f"No local CSV for {year} and download disabled")
        return None, False

    for old_csv in year_dir.glob("*.csv"):
        print(f"Removing outdated live file: {old_csv.name}")
        old_csv.unlink()

    year_str = str(year)[2:]
    filename = f"INFLUD{year_str}-{live_date_str}.csv"
    url = f"{BASE_DOWNLOAD_URL}/{year}/{filename}"
    file_path = year_dir / filename

    if _download_file(url, file_path):
        return read_csv(file_path), True

    return None, False


def fetch_web_dates(
    full_refresh: bool,
    processed_years: list[int],
    years: list[int],
    current_year: int,
) -> tuple[str | None, str | None]:
    """Fetch dates from OpenDataSUS website."""
    frozen_years = [y for y in years if y != current_year]
    all_frozen_processed = all(y in processed_years for y in frozen_years)

    if full_refresh or not all_frozen_processed:
        return get_dates(OPENDATASUS_URL)
    else:
        _, live_date = get_dates(OPENDATASUS_URL, only_live=True)
        return None, live_date


def extract_data(
    data_dir: Path,
    current_year: int,
    years: list[int],
    processed_years: list[int],
    last_live_date: str | None,
    freeze_date_str: str | None,
    live_date_str: str | None,
    full_refresh: bool,
) -> dict:
    """
    Extract data from source, downloading only what's new.

    Returns:
        Dict with keys: frozen_dfs, live_df, live_date, is_live_new

    """
    result = {
        "frozen_dfs": {},
        "live_df": None,
        "live_date": None,
        "is_live_new": False,
    }

    for year in years:
        if year == current_year:
            continue

        if year in processed_years and not full_refresh:
            print(f"Year {year} already in Azure, skipping")
            continue

        if freeze_date_str:
            df = download_frozen(data_dir, year, freeze_date_str, processed_years)
            if df is not None:
                result["frozen_dfs"][year] = df

    if live_date_str:
        live_df, is_new = download_live(
            data_dir, current_year, live_date_str, last_live_date
        )
        if live_df is not None:
            result["live_df"] = live_df
            result["live_date"] = live_date_str
            result["is_live_new"] = is_new

    return result
