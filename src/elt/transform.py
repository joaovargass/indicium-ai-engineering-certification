"""Data transformation: 9-step cleaning (nulls, whitespace, dates, categories, imputation, validation, filtering). select_essential keeps only ESSENTIAL_COLUMNS."""

import pandas as pd

from common.logging import logger
from common.config import (
    CATEGORICAL_VALIDATIONS,
    COVID_VACCINATION_START_DATE,
    COVID_VACCINE_DATE_COLS,
    DATE_COLUMNS,
    ESSENTIAL_COLUMNS,
    EXCLUDED_FROM_NULL_CHECK,
    IGNORED_FIELDS,
    NULL_STRINGS,
    PRIMARY_KEY_FIELD,
)


def _get_string_cols(df: pd.DataFrame) -> list[str]:
    """Get all string columns from DataFrame."""
    return df.select_dtypes(include=["object", "string"]).columns.tolist()


def convert_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize all null value representations to actual null."""
    df = df.copy()

    for col_name in df.columns:
        is_string = df[col_name].dtype == "object" or str(
            df[col_name].dtype
        ).startswith("string")

        if is_string:
            col_str = df[col_name].astype(str)
            col_upper = col_str.str.strip().str.upper()
            null_mask = (
                col_upper.isin([s.upper() for s in NULL_STRINGS])
                | (col_str == "")
                | (col_str.str.strip() == "")
                | col_str.str.upper().isin(["NAN", "<NA>", "NAT", "NONE"])
                | df[col_name].isna()
            )
            df.loc[null_mask, col_name] = None

    return df


def fix_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize whitespace in string columns."""
    df = df.copy()
    for col_name in _get_string_cols(df):
        if col_name not in df.columns:
            continue

        non_null = df[col_name].notna()
        if not non_null.any():
            continue

        cleaned = (
            df[col_name].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
        )

        empty = (cleaned == "") | (cleaned == " ")
        df.loc[empty, col_name] = None
        df.loc[non_null & ~empty, col_name] = cleaned[non_null & ~empty]

    return df


def convert_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convert date columns to datetime."""
    df = df.copy()
    date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"]
    today = pd.Timestamp.now().normalize()
    max_valid_year = (
        today.year + 1
    )  # Allow up to 1 year in future for data collection lag

    for col_name in DATE_COLUMNS:
        if col_name not in df.columns:
            continue

        col_data = df[col_name]
        if col_data.isna().all():
            df[col_name] = pd.to_datetime(col_data, errors="coerce")
            continue

        converted = None
        for fmt in date_formats:
            try:
                converted = pd.to_datetime(col_data, format=fmt, errors="coerce")
                if converted.notna().any():
                    break
            except Exception:
                continue

        if converted is None or converted.isna().all():
            converted = pd.to_datetime(col_data, errors="coerce")

        # Filter out dates that are clearly wrong (way in the future)
        # This catches cases where pandas misinterprets dates (e.g., "32" as 2032)
        if converted is not None:
            invalid_future = converted > pd.Timestamp(f"{max_valid_year}-12-31")
            if invalid_future.any():
                # Set clearly invalid future dates to NaT (Not a Time)
                converted.loc[invalid_future] = pd.NaT

        df[col_name] = converted

    return df


def convert_ignored(df: pd.DataFrame) -> pd.DataFrame:
    """Convert '9 = Ignored' values to NULL."""
    df = df.copy()
    for field in IGNORED_FIELDS:
        if field not in df.columns:
            continue
        field_str = df[field].astype(str).str.strip()
        mask = (field_str == "9") | (field_str == "9.0")
        df.loc[mask, field] = None
    return df


def _impute_symptom_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Impute DT_SIN_PRI from DT_NOTIFIC."""
    if "DT_SIN_PRI" in df.columns and "DT_NOTIFIC" in df.columns:
        df["DT_SIN_PRI"] = df["DT_SIN_PRI"].fillna(df["DT_NOTIFIC"])

    if "DT_SIN_PRI" in df.columns:
        valid_dates = df["DT_SIN_PRI"].dropna()
        if len(valid_dates) > 0:
            # Use maximum date from dataset to cap future dates
            data_max_date = valid_dates.max().normalize()
            future = df["DT_SIN_PRI"] > data_max_date
            if future.any():
                df.loc[future, "DT_SIN_PRI"] = data_max_date
        else:
            # Fallback: if no valid dates exist, use current date for data cleaning
            today = pd.Timestamp.now().normalize()
            future = df["DT_SIN_PRI"] > today
            if future.any():
                df.loc[future, "DT_SIN_PRI"] = today

    return df


def _impute_icu(df: pd.DataFrame) -> pd.DataFrame:
    """Impute ICU-related dates and flags."""
    if all(c in df.columns for c in ["DT_ENTUTI", "DT_INTERNA", "UTI"]):
        mask = (df["UTI"] == "1") & df["DT_ENTUTI"].isna() & df["DT_INTERNA"].notna()
        df.loc[mask, "DT_ENTUTI"] = df.loc[mask, "DT_INTERNA"]

    if "UTI" in df.columns:
        for date_col in ["DT_ENTUTI", "DT_SAIDUTI"]:
            if date_col in df.columns:
                mask = df["UTI"].isna() & df[date_col].notna()
                if mask.any():
                    df.loc[mask, "UTI"] = "1"

    if all(c in df.columns for c in ["UTI", "HOSPITAL", "DT_ENTUTI"]):
        mask = df["UTI"].isna() & (df["HOSPITAL"] == "1") & df["DT_ENTUTI"].isna()
        if mask.any():
            df.loc[mask, "UTI"] = "2"

    if all(c in df.columns for c in ["DT_SAIDUTI", "DT_EVOLUCA", "UTI", "DT_ENTUTI"]):
        mask = (
            (df["UTI"] == "1")
            & df["DT_SAIDUTI"].isna()
            & df["DT_EVOLUCA"].notna()
            & (df["DT_EVOLUCA"] >= df["DT_ENTUTI"])
        )
        df.loc[mask, "DT_SAIDUTI"] = df.loc[mask, "DT_EVOLUCA"]

    return df


def _impute_vaccine(df: pd.DataFrame) -> pd.DataFrame:
    """Impute vaccination status."""
    available = [c for c in COVID_VACCINE_DATE_COLS if c in df.columns]

    if "VACINA_COV" in df.columns and available:
        has_date = df[available].notna().any(axis=1)
        mask = df["VACINA_COV"].isna() & has_date
        if mask.any():
            df.loc[mask, "VACINA_COV"] = "1"

    if "VACINA_COV" in df.columns and "DT_NOTIFIC" in df.columns and available:
        cutoff = pd.Timestamp(COVID_VACCINATION_START_DATE)
        no_evidence = ~df[available].notna().any(axis=1)
        post_era = df["DT_NOTIFIC"] >= cutoff
        mask = df["VACINA_COV"].isna() & no_evidence & post_era
        if mask.any():
            df.loc[mask, "VACINA_COV"] = "2"

    if all(c in df.columns for c in ["VACINA", "DT_UT_DOSE"]):
        mask = df["VACINA"].isna() & df["DT_UT_DOSE"].notna()
        if mask.any():
            df.loc[mask, "VACINA"] = "1"

    return df


def impute_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Impute missing values using business logic."""
    df = df.copy()
    df = _impute_symptom_dates(df)
    df = _impute_icu(df)
    df = _impute_vaccine(df)
    return df


def validate_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Fix invalid date relationships."""
    df = df.copy()
    if all(c in df.columns for c in ["DT_SIN_PRI", "DT_NOTIFIC"]):
        mask = (df["DT_SIN_PRI"] > df["DT_NOTIFIC"]) & df["DT_NOTIFIC"].notna()
        df.loc[mask, "DT_SIN_PRI"] = df.loc[mask, "DT_NOTIFIC"]
    return df


def validate_cats(df: pd.DataFrame) -> pd.DataFrame:
    """Set invalid categorical values to NULL."""
    df = df.copy()
    for col_name, valid in CATEGORICAL_VALIDATIONS.items():
        if col_name not in df.columns:
            continue
        cleaned = df[col_name].astype(str).str.strip()
        invalid = cleaned.notna() & ~cleaned.isin(valid)
        count = invalid.sum()
        if count > 0:
            logger.debug(f"  {col_name}: {count:,} invalid -> NULL")
            df.loc[invalid, col_name] = None
    return df


def remove_invalid(df: pd.DataFrame) -> pd.DataFrame:
    """Remove records missing primary key or all null."""
    if PRIMARY_KEY_FIELD not in df.columns:
        logger.warning(f"{PRIMARY_KEY_FIELD} not found")
        return df

    initial = len(df)

    df = df[df[PRIMARY_KEY_FIELD].notna()].copy()
    removed_pk = initial - len(df)

    excluded = set(c for c in EXCLUDED_FROM_NULL_CHECK if c in df.columns)
    check_cols = [c for c in df.columns if c not in excluded]

    removed_null = 0
    if check_cols:
        all_null = df[check_cols].isna().all(axis=1)
        before = len(df)
        df = df[~all_null].copy()
        removed_null = before - len(df)

    total = initial - len(df)
    if total > 0:
        logger.info(f"Removed {total:,} ({removed_pk:,} no PK, {removed_null:,} all null)")

    return df


def _is_valid_date(df: pd.DataFrame, col: str) -> pd.Series:
    """Check if column has valid dates."""
    if col not in df.columns:
        return pd.Series([False] * len(df), index=df.index)
    c = df[col]
    if pd.api.types.is_datetime64_any_dtype(c):
        return c.notna()
    return c.notna() & (c.astype(str).str.strip() != "")


def _is_valid_cat(df: pd.DataFrame, col: str, values: list[str]) -> pd.Series:
    """Check if column has valid categorical values."""
    if col not in df.columns:
        return pd.Series([False] * len(df), index=df.index)
    return df[col].astype(str).str.strip().isin(values)


def filter_actionable(df: pd.DataFrame) -> pd.DataFrame:
    """Filter records that can contribute to metrics."""
    initial = len(df)

    for_incidence = _is_valid_date(df, "DT_SIN_PRI") | _is_valid_date(df, "DT_NOTIFIC")
    for_mortality = _is_valid_cat(df, "EVOLUCAO", ["1", "2", "3"])
    for_icu = _is_valid_cat(df, "UTI", ["1", "2"])
    for_vaccine = _is_valid_cat(df, "VACINA_COV", ["1", "2"]) | _is_valid_cat(
        df, "VACINA", ["1", "2"]
    )

    actionable = for_incidence | for_mortality | for_icu | for_vaccine

    non_actionable = (~actionable).sum()
    if non_actionable > 0:
        logger.debug(f"Non-actionable: {non_actionable:,}")

    df = df[actionable].copy()
    excluded = initial - len(df)
    if excluded > 0:
        pct = (excluded / initial * 100) if initial > 0 else 0
        logger.info(f"Excluded {excluded:,} non-actionable ({pct:.2f}%)")

    return df


def select_essential(df: pd.DataFrame) -> pd.DataFrame:
    """Select only essential columns."""
    available = df.columns.tolist()
    missing = [c for c in ESSENTIAL_COLUMNS if c not in available]

    cols = ESSENTIAL_COLUMNS
    if missing:
        logger.warning(f"Missing columns: {missing}")
        cols = [c for c in ESSENTIAL_COLUMNS if c in available]

    logger.info(f"Selecting {len(cols)} essential columns from {len(available)} total")
    result = df[cols]

    logger.debug(f"  Rows: {len(result):,}")
    logger.debug(f"  Columns: {len(result.columns)}")

    return result


def analyze_schema(df: pd.DataFrame) -> None:
    """Log schema summary."""
    logger.info("=" * 60)
    logger.info("SCHEMA ANALYSIS")
    logger.info("=" * 60)
    logger.info(f"Columns: {len(df.columns)}")
    logger.info(f"Records: {len(df):,}")
    for col in df.columns:
        logger.debug(f"  {col:30s} {str(df[col].dtype)}")


def report_quality(df: pd.DataFrame, original: pd.DataFrame) -> None:
    """Log data quality report."""
    logger.info("=" * 60)
    logger.info("DATA QUALITY REPORT")
    logger.info("=" * 60)
    initial = len(original)
    final = len(df)
    removed = initial - final
    pct = (removed / initial * 100) if initial > 0 else 0
    logger.info(f"Records: {initial:,} -> {final:,}")
    logger.info(f"Removed: {removed:,} ({pct:.2f}%)")

    missing = []
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            p = (null_count / final * 100) if final > 0 else 0
            missing.append((col, null_count, p))

    if missing:
        logger.debug("Missing values (top 10):")
        for name, count, p in sorted(missing, key=lambda x: x[2], reverse=True)[:10]:
            logger.debug(f"  {name:30s} {count:10,} ({p:6.2f}%)")
    logger.info("=" * 60)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Execute the data cleaning pipeline."""
    logger.info("=" * 60)
    logger.info("DATA CLEANING PIPELINE")
    logger.info("=" * 60)

    original = df.copy()
    analyze_schema(df)

    logger.info("1. Converting NULL strings...")
    df = convert_nulls(df)

    logger.info("2. Fixing whitespace...")
    df = fix_strings(df)

    logger.info("3. Converting date types...")
    df = convert_types(df)

    logger.info("4. Converting 'Ignored' (9) to NULL...")
    df = convert_ignored(df)

    logger.info("5. Imputing missing values...")
    df = impute_missing(df)

    logger.info("6. Validating dates...")
    df = validate_dates(df)

    logger.info("7. Validating categories...")
    df = validate_cats(df)

    logger.info("8. Removing invalid records...")
    df = remove_invalid(df)

    logger.info("9. Filtering actionable records...")
    df = filter_actionable(df)

    logger.info("Final schema:")
    analyze_schema(df)
    report_quality(df, original)

    return df
