# Common Module

> [← Back to Main README](../../README.md)

## Purpose

Centralized configuration module containing all constants, paths, defaults, and validation rules used across the platform. Provides single source of truth for configuration values.

## Architecture

**Key Components**:

**`config.py`**:
- **Path Configuration**: Project directories (data, cache, reports, assets), Azure storage paths
- **Timeout Configuration**: Request/connection timeouts for various operations (600s base, 30-120s for specific operations)
- **Chart Configuration**: Default dimensions (1200x600px), styling (colors, fonts, margins), default periods (30 days, 12 months)
- **Metrics Configuration**: Default lookback periods (7 days for case increase, 30 days for ICU)
- **LLM Configuration**: Model name (`gpt-5-nano`), temperatures (0.0 for agent, 0.3 for reports)
- **Agent Configuration**: Tool step message mappings for UI loading indicators
- **Azure Configuration**: Storage account names, file system names, data warehouse table names
- **Data Validation**: Primary keys, date columns, categorical validations, essential columns
- **Geographic Data**: Brazilian states (UF codes), IBGE state mappings, state name patterns
- **ICU Beds**: Fallback static data, cache TTL (7 days)
- **News Configuration**: Health keywords (Portuguese/English), max results (20), article limits (5)
- **Error Messages**: Standardized Portuguese error messages for no-data scenarios

## Technical Details

- Loads environment variables via `dotenv` at module import
- Paths are resolved relative to `PROJECT_ROOT` (3 levels up from config.py)
- Constants are organized into logical sections with clear headers
- Validation limits ensure data quality (chart days: 7-90, months: 1-24)
- Fallback values provided for critical data (ICU beds) when APIs unavailable

## Usage

Imported by virtually every module in the codebase:
- `agent`: Model configuration, tool mappings
- `charts`: Styling constants, default periods
- `elt`: Azure config, data validation rules, paths
- `metrics`: Default lookback periods
- `tools`: Defaults, validation limits
- `ui`: UI intervals, CSS classes, error messages
- `report`: LLM config, text truncation limits
- `retrieval`: ICU beds fallback, cache TTL
