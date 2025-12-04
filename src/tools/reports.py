"""Report generation tools for SRAG situation reports."""

from pathlib import Path
from typing import Annotated, Any

from langchain_core.tools import tool

from report.templater import (
    format_metrics_table,
    format_news_section,
    generate_executive_summary,
    render_report_template,
    save_report_to_file,
    validate_report_request,
)
from tools.chart_tools import get_daily_chart_json, get_monthly_chart_json
from tools.location_utils import get_location_description
from tools.metric_tools import (
    get_case_increase_rate,
    get_icu_occupancy_rate,
    get_mortality_rate,
    get_vaccination_rate,
)
from tools.news import search_srag_news_tool


def _fetch_all_metrics(uf: str | None, city_code: str | None) -> dict[str, Any]:
    """Fetch all metrics for a location."""
    return {
        "case_increase": get_case_increase_rate.invoke(
            {"uf": uf, "city_code": city_code}
        ),
        "mortality": get_mortality_rate.invoke({"uf": uf, "city_code": city_code}),
        "icu_occupancy": get_icu_occupancy_rate.invoke(
            {"uf": uf, "city_code": city_code}
        ),
        "vaccination": get_vaccination_rate.invoke({"uf": uf, "city_code": city_code}),
    }


def _fetch_news(
    location_desc: str, include_news: bool, max_results: int = 5
) -> list[dict]:
    """Fetch news articles if requested."""
    if not include_news:
        return []
    try:
        # Limit to max 5 news articles
        max_results = min(max_results, 5)
        return search_srag_news_tool.invoke(
            {"query": f"SRAG {location_desc}", "max_results": max_results}
        )
    except Exception:
        return []




@tool
def generate_download_report(
    uf: Annotated[str | None, "State code. None for national."] = None,
    city_code: Annotated[str | None, "IBGE city code. Overrides UF."] = None,
    days: Annotated[int, "Days for daily chart (default: 30, min: 7, max: 90)."] = 30,
    months: Annotated[
        int, "Months for monthly chart (default: 12, min: 1, max: 24)."
    ] = 12,
    include_news: Annotated[bool, "Include news (default: True)."] = True,
    max_news: Annotated[int, "Max news articles (default: 5, max: 5)."] = 5,
    include_executive_summary: Annotated[
        bool, "Include executive summary (default: True)."
    ] = True,
    include_metrics: Annotated[bool, "Include metrics (default: True)."] = True,
    include_charts: Annotated[bool, "Include charts section (default: True)."] = True,
) -> dict[str, Any]:
    """
    Generate and save SRAG report for download.

    Uses LLM to generate contextualized explanations based on metrics and news.
    Report is saved to file and returned as dictionary with content and file path.

    Returns:
        Dictionary with:
        - report_content: Markdown string
        - file_path: Path to saved file (as string)
        - file_size: File size in bytes
    """
    # Validate request
    is_valid, error_msg = validate_report_request(days, months, max_news)
    if not is_valid:
        return {
            "error": error_msg,
            "report_content": "",
            "file_path": "",
            "file_size": 0,
        }

    # Fetch data
    location_desc = get_location_description(uf, city_code)
    metrics = _fetch_all_metrics(uf, city_code)
    news = _fetch_news(location_desc, include_news, max_news)

    # Generate LLM-based content
    executive_summary = ""
    if include_executive_summary:
        executive_summary = generate_executive_summary(metrics, news, location_desc)

    # Format metrics table with LLM explanations
    metrics_table = ""
    if include_metrics:
        metrics_table = format_metrics_table(metrics, news)

    # Format charts section - generate actual charts for download
    charts_section = ""
    if include_charts:
        # Generate chart JSONs for reference (can be used to render charts)
        daily_chart_json = get_daily_chart_json.invoke({"uf": uf, "days": days})
        monthly_chart_json = get_monthly_chart_json.invoke(
            {"uf": uf, "months": months}
        )
        
        charts_section = f"""**Gráfico 1:** Número diário de casos dos últimos {days} dias
**Gráfico 2:** Número mensal de casos dos últimos {months} meses

*Os gráficos interativos estão disponíveis na versão de chat do relatório. Os dados dos gráficos foram gerados e estão incluídos neste relatório.*"""

    # Format news section
    news_section = ""
    if include_news:
        news_section = format_news_section(news, detailed=True)

    # Render report using template
    report_content = render_report_template(
        location=location_desc,
        executive_summary=executive_summary,
        metrics_table=metrics_table,
        charts_section=charts_section,
        news_section=news_section,
        include_executive_summary=include_executive_summary,
        include_metrics=include_metrics,
        include_charts=include_charts,
        include_news=include_news,
    )

    # Save to file
    file_path = save_report_to_file(report_content, location_desc)
    file_size = file_path.stat().st_size

    return {
        "report_content": report_content,
        "file_path": str(file_path),
        "file_size": file_size,
    }


@tool
def generate_chat_report(
    uf: Annotated[str | None, "State code. None for national."] = None,
    city_code: Annotated[str | None, "IBGE city code. Overrides UF."] = None,
    days: Annotated[int, "Days for daily chart (default: 30, min: 7, max: 90)."] = 30,
    months: Annotated[
        int, "Months for monthly chart (default: 12, min: 1, max: 24)."
    ] = 12,
    include_news: Annotated[bool, "Include news (default: True)."] = True,
    max_news: Annotated[int, "Max news articles (default: 5, max: 5)."] = 5,
    include_executive_summary: Annotated[
        bool, "Include executive summary (default: True)."
    ] = True,
    include_metrics: Annotated[bool, "Include metrics (default: True)."] = True,
) -> dict[str, Any]:
    """
    Generate SRAG report with interactive charts for chat display.

    Uses LLM to generate contextualized explanations. Returns report text
    and Plotly JSON charts for inline rendering.

    Returns:
        Dictionary with:
        - report_text: Markdown formatted report text
        - daily_chart_json: Plotly JSON for daily chart
        - monthly_chart_json: Plotly JSON for monthly chart
        - metrics: All metrics data
        - news: News articles
    """
    # Validate request
    is_valid, error_msg = validate_report_request(days, months, max_news)
    if not is_valid:
        return {
            "error": error_msg,
            "report_text": "",
            "daily_chart_json": "",
            "monthly_chart_json": "",
            "metrics": {},
            "news": [],
        }

    # Fetch data
    location_desc = get_location_description(uf, city_code)
    metrics = _fetch_all_metrics(uf, city_code)
    news = _fetch_news(location_desc, include_news, max_news)

    # Generate LLM-based content
    executive_summary = ""
    if include_executive_summary:
        executive_summary = generate_executive_summary(metrics, news, location_desc)

    # Format metrics table with LLM explanations
    metrics_table = ""
    if include_metrics:
        metrics_table = format_metrics_table(metrics, news)

    # Build report text (shorter version for chat)
    report_lines = [f"# Relatório SRAG — {location_desc}"]

    if include_executive_summary:
        report_lines.extend(["", "## Resumo Executivo", "", executive_summary, ""])

    if include_metrics:
        report_lines.extend(["", metrics_table, ""])

    report_lines.append("## Gráficos Interativos")

    # Add news (brief format for chat)
    if include_news and news:
        report_lines.append("")
        report_lines.append(format_news_section(news, detailed=False))

    report_text = "\n".join(report_lines)

    # Generate charts
    daily_chart_json = get_daily_chart_json.invoke({"uf": uf, "days": days})
    monthly_chart_json = get_monthly_chart_json.invoke({"uf": uf, "months": months})

    return {
        "report_text": report_text,
        "daily_chart_json": daily_chart_json,
        "monthly_chart_json": monthly_chart_json,
        "metrics": metrics,
        "news": news,
    }
