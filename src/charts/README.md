# Charts Module

> [← Back to Main README](../../README.md)

## Purpose

Plotly-based visualization module that generates interactive charts (line and bar) for SRAG case data. Provides chart generation, statistical analysis, and export capabilities for daily and monthly case visualizations.

## Architecture

**Key Components**:

**`charts.py`**:
- `plot_daily_cases()`: Generates line charts for daily case counts over specified days (default: 30)
- `plot_monthly_cases()`: Generates bar charts for monthly aggregated case counts (default: 12 months)
- `figure_to_json()`: Converts Plotly Figure to JSON string for web embedding
- `figure_to_image_file()`: Exports Plotly Figure as PNG for reports (requires kaleido, default 1200x600px)
- Internal helpers:
  - `_prepare_data()`: Prepares and filters data for charting (date parsing, location filtering)
  - `_filter_by_date_range()`: Filters DataFrame by date range
  - `_aggregate_daily()`: Aggregates data by day
  - `_aggregate_monthly()`: Aggregates data by month
  - `_create_line_chart()`: Creates line chart with standard styling
  - `_create_bar_chart()`: Creates bar chart with standard styling
  - `_create_empty_chart()`: Creates empty chart with "no data" message
  - `_build_title()`: Builds chart title with optional location suffix

**`stats.py`**:
- `prepare_chart_data()`: Filters and prepares DataFrame with date parsing and location filtering
- `calculate_trend()`: Computes trend direction (increasing/decreasing/stable) and percentage change by comparing first vs second half averages
- `extract_daily_stats()`: Extracts statistics from daily data (total cases, averages, peaks, trends, date ranges)
- `extract_monthly_stats()`: Extracts statistics from monthly data with period limitation detection

## Technical Details

**Chart Generation Flow**:
1. Data preparation: Parse dates, filter by location (UF/city) if specified
2. Date range filtering: Calculate start/end dates based on lookback period
3. Aggregation: Group by day (daily) or month (monthly)
4. Visualization: Create Plotly Figure with standardized styling
5. Export: Convert to JSON (for UI) or PNG (for reports)

**Styling Configuration**:
- Colors: Single color scheme (`#2E86AB`) from `common.config`
- Dimensions: Default 1200x600px (configurable)
- Fonts: Title 20px, body 12px, annotations 16px
- Formatting: Portuguese date formats (`%d/%m/%Y`), thousand separators

**Statistical Analysis**:
- Trend calculation compares first half vs second half averages using `calculate_trend()`
- Statistics include: total cases, averages, min/max values with dates, trend direction and percentage
- Period limitation detection for monthly charts when data availability is shorter than requested
- Daily stats: `extract_daily_stats()` returns total_cases, avg_daily, max_daily, max_date, min_daily, trend_direction, trend_percentage
- Monthly stats: `extract_monthly_stats()` returns similar metrics plus period_limited_by_data flag when applicable

## Dependencies

- `plotly`: Chart generation and export
- `pandas`: Data manipulation and aggregation
- `common.config`: Styling constants and defaults

## Usage

Used by:
- `tools.chart_tools`: Agent tool wrappers that generate charts from user queries
- `tools.reports`: Report generation that includes chart images
- `ui.chart_render`: UI components that render charts in chat interface
- `ui.chart_data`: Data preparation helpers for UI
