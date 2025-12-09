# Retrieval Module

> [← Back to Main README](../../README.md)

## Purpose

External data retrieval module that fetches ICU bed counts from CNES API and health news from Tavily API. Provides cached, fallback-enabled access to external data sources.

## Architecture

**Key Components**:

**`icu_beds.py`** - CNES ICU bed data:
- `get_icu_beds_data()`: Fetches ICU bed counts by state/city from CNES API
- `get_location_icu_beds()`: Gets ICU beds for specific location (UF, city code, or national)
- Caching: 7-day TTL cache stored as JSON in `data/cleaned/icu_beds_cache.json`
- Fallback: Uses static fallback data (Dec 2024) if API unavailable
- Data structure: Returns dict with `icu_beds_by_uf`, `icu_beds_by_city`, `brazil_total`, `competency` (YYYYMM), `source`

**`news_fetcher.py`** - Tavily news search:
- `search_srag_news()`: Searches health news using Tavily API
- Query enhancement: Automatically adds health keywords and Brazil context
- Returns list of articles with title, URL, content, date
- Requires `TAVILY_API_KEY` environment variable
- Max results: 5 (default), up to 20 (NEWS_API_MAX_RESULTS)

## Technical Details

**ICU Beds**:
- Fetches from CNES CSV API: `https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/Leitos_SUS/Leitos_{year}.csv`
- Uses latest competency period (YYYYMM) from data
- Normalizes city names (uppercase, no accents) for matching
- City lookup: Converts IBGE city code to city name, then normalizes for CNES matching
- Cache serialization: Converts tuple keys `(UF, city)` to string keys for JSON

**News Search**:
- Uses Tavily API with "advanced" search depth
- Query enhancement: Adds "Brasil" if state mentioned, adds "saúde SRAG" if no health keywords
- Health keywords: Portuguese and English keywords from `common.config`
- Error handling: Returns empty list on API errors or missing API key

## Dependencies

- `requests`: HTTP requests for CNES API
- `pandas`: CSV parsing for CNES data
- `tavily`: Tavily API client
- `tools.location_utils`: City name resolution (for city code lookup)
- `common.config`: Cache paths, fallback data, keywords, timeouts

## Usage

Used by:
- `metrics.calculators`: Fetches ICU bed counts for ICU occupancy calculations
- `tools.news`: Agent tool wrapper for news search
