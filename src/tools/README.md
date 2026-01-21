# Tools Module

> [← Back to Main README](../../README.md)

## Purpose

LangChain tool wrappers that expose SRAG data analysis capabilities to the agent. These tools are dynamically bound to the LLM and called based on user queries. Provides 9 tools: 4 metrics, 2 charts, 2 reports, and 1 news search.

## Architecture

**Complete tools catalog organized by category (Metrics, Charts, Reports, News) and their relationships with the data layer.**

<div align="center">

```mermaid
flowchart TB
    Agent[Agent] -->|Calls| Tools[Tools Layer<br/>9 Tools Available]
    
    subgraph METRIC_TOOLS["Metric Tools - 4 Tools"]
        direction TB
        M1[get_case_increase_rate<br/>Period comparison]
        M2[get_mortality_rate<br/>Deaths/Cases ratio]
        M3[get_icu_occupancy_rate<br/>ICU capacity]
        M4[get_vaccination_rate<br/>Vaccine coverage]
    end
    
    subgraph CHART_TOOLS["Chart Tools - 2 Tools"]
        direction TB
        C1[get_daily_chart_json<br/>Plotly JSON]
        C2[get_monthly_chart_json<br/>Plotly JSON]
    end
    
    subgraph REPORT_TOOLS["Report Tools - 2 Tools"]
        direction TB
        R1[generate_download_report<br/>Markdown + ZIP]
        R2[generate_chat_report<br/>Markdown + JSON charts]
    end
    
    subgraph NEWS_TOOL["News Tool - 1 Tool"]
        direction TB
        N1[search_srag_news_tool<br/>Tavily API]
    end
    
    Tools --> METRIC_TOOLS
    Tools --> CHART_TOOLS
    Tools --> REPORT_TOOLS
    Tools --> NEWS_TOOL
    
    METRIC_TOOLS -->|Uses| Data[Data Layer<br/>load_srag_data]
    CHART_TOOLS -->|Uses| Data
    REPORT_TOOLS -->|Uses| Data
    REPORT_TOOLS -->|Calls| METRIC_TOOLS
    REPORT_TOOLS -->|Calls| CHART_TOOLS
    REPORT_TOOLS -->|Calls| NEWS_TOOL
    
    classDef agentStyle fill:#ea580c,stroke:#c2410c,stroke-width:3px,color:#fff
    classDef toolsStyle fill:#9333ea,stroke:#7e22ce,stroke-width:3px,color:#fff
    classDef metricStyle fill:#059669,stroke:#047857,stroke-width:2px,color:#fff
    classDef chartStyle fill:#be185d,stroke:#9f1239,stroke-width:2px,color:#fff
    classDef reportStyle fill:#dc2626,stroke:#b91c1c,stroke-width:2px,color:#fff
    classDef newsStyle fill:#64748b,stroke:#475569,stroke-width:2px,color:#fff
    classDef dataStyle fill:#1e40af,stroke:#1e3a8a,stroke-width:2px,color:#fff
    
    class Agent agentStyle
    class Tools toolsStyle
    class M1,M2,M3,M4 metricStyle
    class C1,C2 chartStyle
    class R1,R2 reportStyle
    class N1 newsStyle
    class Data dataStyle
```

**Flow of metric calculations showing how each metric tool loads data, applies location filters, and computes epidemiological indicators.**

```mermaid
flowchart LR
    Tool[Tool Call] -->|load_srag_data| LoadData[Load SRAG Data<br/>DataFrame]
    
    LoadData --> Filter[Apply Location Filter<br/>UF or City Code]
    
    Filter -->|Case Increase| Calc1[calculate_case_growth<br/>Compare periods]
    Filter -->|Mortality| Calc2[calculate_mortality_rate<br/>Deaths / Cases]
    Filter -->|ICU Occupancy| Calc3[calculate_icu_occupancy_rate<br/>ICU Beds / Cases]
    Filter -->|Vaccination| Calc4[calculate_vaccination_rate<br/>Vaccinated / Cases]
    
    Calc3 -->|Needs Beds Data| CNES[CNES API<br/>ICU Beds Data<br/>Cached 7 days]
    CNES --> Calc3
    
    Calc1 --> Format1[Format Result<br/>Add Location]
    Calc2 --> Format2[Format Result<br/>Add Location]
    Calc3 --> Format3[Format Result<br/>Add Location]
    Calc4 --> Format4[Format Result<br/>Add Location]
    
    Format1 --> Return1[Return Dict]
    Format2 --> Return2[Return Dict]
    Format3 --> Return3[Return Dict]
    Format4 --> Return4[Return Dict]
    
    classDef toolStyle fill:#9333ea,stroke:#7e22ce,stroke-width:3px,color:#fff
    classDef loadStyle fill:#059669,stroke:#047857,stroke-width:2px,color:#fff
    classDef calcStyle fill:#ea580c,stroke:#c2410c,stroke-width:2px,color:#fff
    classDef formatStyle fill:#ca8a04,stroke:#a16207,stroke-width:2px,color:#fff
    classDef externalStyle fill:#64748b,stroke:#475569,stroke-width:2px,color:#fff
    
    class Tool toolStyle
    class LoadData,Filter loadStyle
    class Calc1,Calc2,Calc3,Calc4 calcStyle
    class Format1,Format2,Format3,Format4,Return1,Return2,Return3,Return4 formatStyle
    class CNES externalStyle
```

</div>

**Complete report generation workflow from parameter validation through metric fetching, chart creation, LLM narrative generation, and file output.**

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

**`metric_tools.py`** - Metric calculation tools:
- `get_case_increase_rate()`: Case growth rate comparing current vs previous period (default: 7 days)
- `get_mortality_rate()`: Mortality percentage (deaths/cases, default: 12 months lookback)
- `get_icu_occupancy_rate()`: ICU bed occupancy rate (default: 30 days lookback). Sources: OpenDataSUS (SRAG), CNES (beds)
- `get_vaccination_rate()`: COVID-19 and/or flu vaccination rates (default: 12 months lookback)
- All tools support `uf` (state code) and `city_code` (IBGE code) parameters
- Returns structured dictionaries with rates, counts, periods, and metadata
- Handles `NoDataAvailableError` with Portuguese error messages

**`chart_tools.py`** - Chart generation tools:
- `get_daily_chart_json()`: Generates daily cases line chart as Plotly JSON
- `get_monthly_chart_json()`: Generates monthly cases bar chart as Plotly JSON
- Supports custom titles and axis labels (in user's language)
- Returns Plotly JSON strings for UI rendering
- Default periods: 30 days (daily), 12 months (monthly)

**`reports.py`** - Report generation tools:
- `generate_download_report()`: Generates complete report with LLM narrative, saves to file/ZIP
  - Fetches all 4 metrics
  - Generates chart images (PNG) for inclusion in ZIP
  - Uses LLM to generate integrated narrative
  - Saves as Markdown file or ZIP (with images)
  - Returns file path, size, and summary for chat display
- `generate_chat_report()`: Generates interactive report for chat display
  - Returns Markdown text with executive summary and metrics table
  - Includes Plotly JSON charts for inline rendering
  - No file saving (for chat display only)
- Both tools support parameter validation, component flags (include_metrics, include_news, include_charts)

**`news.py`** - News search tool:
- `search_srag_news_tool()`: Searches health news via Tavily API
- Query enhancement handled by `retrieval.news_fetcher`
- Returns list of articles with title, URL, content, date
- Max results: 5 (default), up to 20

**`location_utils.py`** - Location resolution utilities:
- `resolve_city_name()`: Converts IBGE 6-digit code to city name
  - Uses cached mapping file (`data/cleaned/city_mapping.json`)
  - Falls back to IBGE API if cache missing
  - Caches API response for future use
- `determine_location_filter()`: Returns (column, value) tuple for DataFrame filtering
  - Returns `("CO_MUN_NOT", city_code)` if city_code provided
  - Returns `("SG_UF_NOT", uf)` if uf provided
  - Returns `(None, None)` for national data
- `get_location_description()`: Returns human-readable location string
  - "Brasil (nacional)" for national
  - UF code for state
  - City name for city (resolved from code)

## Technical Details

**Tool Decorators**:
- All tools use `@tool` decorator from `langchain_core.tools`
- Parameters use `Annotated` type hints with descriptions for LLM
- Descriptions guide LLM on when to use each tool

**Error Handling**:
- All tools catch `NoDataAvailableError` and return error dictionaries
- Error messages in Portuguese from `common.config`
- Tools return structured dicts even on errors (for consistent parsing)

**Location Handling**:
- Tools accept `uf` (state) and `city_code` (IBGE) parameters
- `city_code` overrides `uf` if both provided
- Location filtering handled via `location_utils.determine_location_filter()`
- Results include `location` field with human-readable description

**Report Generation Flow**:
1. Validate parameters (days: 7-90, months: 1-24, news: 0-5)
2. Fetch all metrics for location
3. Fetch news if requested
4. Generate chart images (if charts included)
5. Generate LLM narrative with confirmed components
6. Render final report using Jinja2 template
7. Save to file/ZIP and return result dict

## Dependencies

- `langchain_core.tools`: Tool decorators and base classes
- `metrics.calculators`: Core metric calculation functions
- `charts.charts`: Chart generation functions
- `report.templater`: Report generation and formatting
- `retrieval.news_fetcher`: News search
- `elt.load`: Data loading
- `tools.location_utils`: Location resolution

## Usage

Used by:
- `agent.graph`: All 9 tools bound to LLM via `llm.bind_tools(ALL_TOOLS)`
- Tools are called automatically by agent based on user queries
