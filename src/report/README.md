# Report Module

> [← Back to Main README](../../README.md)

## Purpose

LLM-powered report generation module that creates integrated, narrative-style SRAG situation reports. Combines metrics, charts, and news into cohesive Markdown documents with contextualized explanations.

## Architecture

**Complete report generation workflow from parameter validation through metric fetching, chart creation, LLM narrative generation, and file output (ZIP or JSON).**

<div align="center">

```mermaid
flowchart TD
    Start([Report Request]) --> Validate[Validate Parameters<br/>days months max_news]
    Validate -->|Invalid| Error[Return Error]
    Validate -->|Valid| FetchMetrics[Fetch All Metrics<br/>4 metric tools]
    
    FetchMetrics --> CheckError{Metrics<br/>Error?}
    CheckError -->|Yes| Error
    CheckError -->|No| FetchNews{Fetch News?<br/>include_news}
    
    FetchNews -->|Yes| News[Search Tavily API<br/>SRAG news]
    FetchNews -->|No| SkipNews[Skip News]
    
    News --> GenerateCharts{Include<br/>Charts?}
    SkipNews --> GenerateCharts
    
    GenerateCharts -->|Yes| LoadData[Load SRAG Data]
    LoadData --> CreateDaily[Create Daily Chart<br/>plot_daily_cases]
    CreateDaily --> CreateMonthly[Create Monthly Chart<br/>plot_monthly_cases]
    CreateMonthly --> ExtractStats[Extract Statistics<br/>daily & monthly stats]
    ExtractStats --> SaveImages[Save Chart Images<br/>PNG files]
    SaveImages --> GenerateBody
    GenerateCharts -->|No| GenerateBody
    
    GenerateBody[Generate Report Body<br/>LLM + Metrics + News]
    GenerateBody --> Render[Render Report<br/>Jinja2 Template]
    
    Render --> CheckType{Report<br/>Type?}
    CheckType -->|Download| CreateZIP[Create ZIP File<br/>Markdown + Images]
    CheckType -->|Chat| CreateJSON[Create JSON<br/>Markdown + Chart JSONs]
    
    CreateZIP --> End1([Return ZIP Path])
    CreateJSON --> End2([Return JSON Data])
    
    classDef validateStyle fill:#dc2626,stroke:#b91c1c,stroke-width:2px,color:#fff
    classDef fetchStyle fill:#059669,stroke:#047857,stroke-width:2px,color:#fff
    classDef chartStyle fill:#be185d,stroke:#9f1239,stroke-width:2px,color:#fff
    classDef generateStyle fill:#9333ea,stroke:#7e22ce,stroke-width:2px,color:#fff
    classDef outputStyle fill:#ca8a04,stroke:#a16207,stroke-width:2px,color:#fff
    classDef startEndStyle fill:#1e40af,stroke:#1e3a8a,stroke-width:3px,color:#fff
    
    class Validate,CheckError,Error validateStyle
    class FetchMetrics,FetchNews,News,SkipNews fetchStyle
    class GenerateCharts,LoadData,CreateDaily,CreateMonthly,ExtractStats,SaveImages chartStyle
    class GenerateBody,Render generateStyle
    class CheckType,CreateZIP,CreateJSON outputStyle
    class Start,End1,End2 startEndStyle
```

</div>

## Key Components

**`generator.py`** - Main report generation:
- `generate_report_body()`: Generates integrated narrative report using LLM
- Builds context from confirmed components (metrics, charts, news)
- Only includes components that were confirmed via flags (include_metrics, include_charts, include_news)
- Returns tuple of (report_body, sources_section)
- Falls back to template-based report if LLM fails
- Context building helpers: `_build_context_header()`, `_build_metrics_context()`, `_build_charts_context()`, `_build_news_context()`
- Instruction building: `_build_instructions()` creates comprehensive LLM prompt with formatting rules, integration rules, narrative flow
- Date handling: Detects when data period_end is before today and instructs LLM to mention weekly updates

**`llm.py`** - LLM integration:
- `_get_llm()`: Lazy initialization of ChatOpenAI instance (temperature 0.3, model from OPENAI_MODEL or DEFAULT_MODEL_NAME)
- `generate_executive_summary()`: Generates 2-3 paragraph executive summary from metrics and news
- `generate_metric_explanation()`: Generates contextualized explanations (1 sentence) for individual metrics with calculation details
- `_check_data_outdated()`: Detects if data period_end is before today and adds note to prompts
- `_build_metric_context()`: Builds context string for metric explanation prompts
- Handles LLM failures gracefully with fallback text
- All prompts instruct LLM to use Portuguese dates (not YYYY-MM-DD format)

**`templates.py`** - Jinja2 templates:
- `validate_report_request()`: Validates report parameters (days: 7-90, months: 1-24, news: 0-5)
  - Uses CHART_DAYS_MIN/MAX, CHART_MONTHS_MIN/MAX, MAX_NEWS_ARTICLES from config
- `render_integrated_report()`: Renders final Markdown report using Jinja2 template
- Template includes: header with location and generation date (DD/MM/YYYY HH:MM), report body, charts section (if include_charts=True), sources section, footer with data source attribution (DATASET_YEAR_RANGE)

**`formatter.py`** - Report formatting:
- `format_metrics_table()`: Creates Markdown table with metrics and LLM-generated explanations
  - Calls `generate_metric_explanation()` for each metric
  - Formats all 4 metrics (case increase, mortality, ICU occupancy, vaccination)
  - Includes calculation formulas section
- `format_news_section()`: Formats news articles as Markdown section (detailed or links-only)
- Truncates explanations to max length (300 chars, EXPLANATION_MAX_LENGTH) for table display
- News summaries truncated to NEWS_SUMMARY_MAX_LENGTH (200 chars)

**`parser.py`** - Report parsing:
- `generate_report_summary()`: Extracts summary from full report for chat display
- Extracts location from header (format: "Relatório SRAG — {location}")
- Extracts report body, stopping at charts/sources sections
- Builds paragraphs from text, respects max character limit (600 chars, REPORT_SUMMARY_MAX_CHARS)
- Returns formatted markdown with location header and summary text
- Used to show preview in chat before download

**`files.py`** - File operations:
- `save_report_to_file()`: Saves Markdown report to file in `reports/` directory
- `save_report_zip()`: Creates ZIP file with report and chart images (PNG files)
- Sanitizes location names for filenames (removes special characters, spaces, parentheses)
- Uses date-based naming: `Relatorio_SRAG_{location}_{date}.md` or `.zip`
- Creates `reports/` directory if it doesn't exist

**`templater.py`** - Backward compatibility facade:
- Re-exports all public functions from submodules (llm, formatter, generator, templates, files, parser)
- Provides unified import interface for backward compatibility
- New code should import directly from submodules
- Exports: LLM functions, formatter functions, generator functions, template functions, file functions, parser functions

## Technical Details

**Report Generation Flow**:
1. Validate request parameters (days, months, news count)
2. Collect confirmed components (metrics, charts, news)
3. Build LLM context with all confirmed data
4. Generate integrated narrative using LLM with structured prompt
5. Format sources section from news articles
6. Render final report using Jinja2 template
7. Save to file or ZIP with images

**LLM Prompt Structure**:
- Context header with location
- Metrics context (all 4 metrics with periods)
- Charts context (daily/monthly statistics)
- News context (article titles, content previews, URLs)
- Instructions: Use only confirmed data, Markdown formatting rules, integration rules, narrative flow
- Date handling: Detects outdated data and instructs LLM to mention it

**Markdown Formatting**:
- Required sections: Visão Geral, Análise das Métricas, Tendências dos Gráficos, Contexto e Notícias, Implicações e Recomendações
- Uses `##` headers for sections
- Bold for important values: `**11,5%**`
- Tables for metrics with explanations
- Sources as markdown links

**Error Handling**:
- LLM failures fall back to template-based report
- Missing components handled gracefully (only included if confirmed)
- Date parsing errors handled with fallbacks
- File I/O errors propagate (caller handles)

## Dependencies

- `langchain_openai`: LLM integration
- `jinja2`: Template rendering
- `zipfile`: ZIP file creation
- `common.config`: Validation limits, text truncation limits, model config

## Usage

Used by:
- `tools.reports`: Agent tool wrappers that generate reports from user queries
