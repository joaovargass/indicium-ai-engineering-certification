"""Report generation tools for SRAG situation reports."""

import shutil
import tempfile
from pathlib import Path
from typing import Annotated, Any

import pandas as pd
from langchain_core.tools import tool

from charts.charts import figure_to_image_file, plot_daily_cases, plot_monthly_cases
from charts.stats import extract_daily_stats, extract_monthly_stats
from common.config import DEFAULT_DAYS, DEFAULT_MONTHS, MAX_NEWS_ARTICLES
from elt.load import NoDataAvailableError, load_srag_data
from report.templater import (
    format_metrics_table,
    format_news_section,
    generate_executive_summary,
    generate_report_body,
    generate_report_summary,
    render_integrated_report,
    save_report_to_file,
    save_report_zip,
    validate_report_request,
)
from tools.location_utils import determine_location_filter, get_location_description
from tools.metric_tools import (
    get_case_increase_rate,
    get_icu_occupancy_rate,
    get_mortality_rate,
    get_vaccination_rate,
)
from tools.news import search_srag_news_tool


def _fetch_all_metrics(uf: str | None, city_code: str | None) -> dict[str, Any]:
    """
    Fetch all SRAG metrics for a location.

    Args:
        uf: State code or None for national
        city_code: IBGE city code or None

    Returns:
        Dictionary with case_increase, mortality, icu_occupancy, vaccination metrics

    """
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
    location_desc: str, include_news: bool, max_results: int = MAX_NEWS_ARTICLES
) -> list[dict]:
    """
    Fetch news articles if requested.

    Args:
        location_desc: Location description for search query
        include_news: Whether to fetch news
        max_results: Maximum number of articles

    Returns:
        List of news article dictionaries or empty list

    """
    if not include_news:
        return []
    try:
        max_results = min(max_results, MAX_NEWS_ARTICLES)
        return search_srag_news_tool.invoke(
            {"query": f"SRAG {location_desc}", "max_results": max_results}
        )
    except (ValueError, KeyError, ConnectionError):
        return []


def _check_metrics_error(metrics: dict[str, Any]) -> str | None:
    """
    Check if any metric returned an error.

    Args:
        metrics: Dictionary of metrics

    Returns:
        Error message if any metric has error, None otherwise

    """
    for metric_data in metrics.values():
        if isinstance(metric_data, dict) and "error" in metric_data:
            return metric_data["error"]
    return None


def _generate_chart_images(
    df: pd.DataFrame,
    location_col: str | None,
    location_value: str | None,
    days: int,
    months: int,
    temp_path: Path,
) -> tuple[dict[str, Path], dict[str, Any], str]:
    """
    Generate chart images and extract statistics.

    Args:
        df: DataFrame with SRAG data
        location_col: Location column name
        location_value: Location filter value
        days: Number of days for daily chart
        months: Number of months for monthly chart
        temp_path: Temporary directory for images

    Returns:
        Tuple of (image_files dict, chart_info dict, charts_section markdown)

    """
    daily_stats = extract_daily_stats(df, location_col, location_value, days)
    monthly_stats = extract_monthly_stats(df, location_col, location_value, months)

    chart_info = {}
    if daily_stats:
        chart_info["daily"] = daily_stats
    if monthly_stats:
        chart_info["monthly"] = monthly_stats

    if len(chart_info) == 1:
        chart_info = list(chart_info.values())[0]

    daily_fig = plot_daily_cases(
        df, location_col=location_col, location_value=location_value, days=days
    )
    daily_image_path = temp_path / "grafico_diario.png"
    figure_to_image_file(daily_fig, daily_image_path)

    monthly_fig = plot_monthly_cases(
        df, location_col=location_col, location_value=location_value, months=months
    )
    monthly_image_path = temp_path / "grafico_mensal.png"
    figure_to_image_file(monthly_fig, monthly_image_path)

    image_files = {
        "grafico_diario.png": daily_image_path,
        "grafico_mensal.png": monthly_image_path,
    }

    charts_section = f"""**Gráfico 1:** Número diário de casos dos últimos {days} dias

![Gráfico Diário](grafico_diario.png)

**Gráfico 2:** Número mensal de casos dos últimos {months} meses

![Gráfico Mensal](grafico_mensal.png)"""

    return image_files, chart_info, charts_section


def _build_report_result(
    report_content: str,
    location_desc: str,
    include_charts: bool,
    image_files: dict[str, Path] | None,
    temp_dir: str | None,
) -> dict[str, Any]:
    """
    Save report and build result dictionary.

    Args:
        report_content: Generated report markdown
        location_desc: Location description
        include_charts: Whether charts are included
        image_files: Dictionary of image files
        temp_dir: Temporary directory path

    Returns:
        Result dictionary with report_content, file_path, file_size, report_summary

    """
    if include_charts and image_files:
        zip_path = save_report_zip(report_content, location_desc, image_files)
        file_size = zip_path.stat().st_size
        file_path = zip_path

        if temp_dir and Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
    else:
        file_path = save_report_to_file(report_content, location_desc)
        file_size = file_path.stat().st_size

    summary = generate_report_summary(report_content)

    return {
        "report_content": report_content,
        "report_summary": summary,
        "file_path": str(file_path),
        "file_size": file_size,
    }


@tool
def generate_download_report(
    uf: Annotated[str | None, "State code. None for national."] = None,
    city_code: Annotated[str | None, "IBGE city code. Overrides UF."] = None,
    days: Annotated[
        int, "Days for daily chart (default: 30, min: 7, max: 90)."
    ] = DEFAULT_DAYS,
    months: Annotated[
        int, "Months for monthly chart (default: 12, min: 1, max: 24)."
    ] = DEFAULT_MONTHS,
    include_news: Annotated[bool, "Include news (default: True)."] = True,
    max_news: Annotated[
        int, "Max news articles (default: 5, max: 5)."
    ] = MAX_NEWS_ARTICLES,
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
        - report_summary: Brief summary for chat display

    """
    error_result = {"error": "", "report_content": "", "file_path": "", "file_size": 0}

    is_valid, error_msg = validate_report_request(days, months, max_news)
    if not is_valid:
        error_result["error"] = error_msg
        return error_result

    location_desc = get_location_description(uf, city_code)
    metrics = _fetch_all_metrics(uf, city_code)

    metrics_error = _check_metrics_error(metrics)
    if metrics_error:
        error_result["error"] = metrics_error
        return error_result

    news = _fetch_news(location_desc, include_news, max_news)

    charts_section = ""
    image_files = {}
    temp_dir = None
    chart_info = None

    if include_charts:
        try:
            df = load_srag_data()
        except NoDataAvailableError as e:
            error_result["error"] = str(e)
            return error_result

        location_col, location_value = determine_location_filter(uf, city_code)
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)

        image_files, chart_info, charts_section = _generate_chart_images(
            df, location_col, location_value, days, months, temp_path
        )

    report_body, sources_section = generate_report_body(
        metrics=metrics,
        news=news,
        location=location_desc,
        chart_info=chart_info,
        include_metrics=include_metrics,
        include_news=include_news,
        include_charts=include_charts,
    )

    report_content = render_integrated_report(
        location=location_desc,
        report_body=report_body,
        charts_section=charts_section,
        sources_section=sources_section,
        include_charts=include_charts,
    )

    return _build_report_result(
        report_content, location_desc, include_charts, image_files, temp_dir
    )


@tool
def generate_chat_report(
    uf: Annotated[str | None, "State code. None for national."] = None,
    city_code: Annotated[str | None, "IBGE city code. Overrides UF."] = None,
    days: Annotated[
        int, "Days for daily chart (default: 30, min: 7, max: 90)."
    ] = DEFAULT_DAYS,
    months: Annotated[
        int, "Months for monthly chart (default: 12, min: 1, max: 24)."
    ] = DEFAULT_MONTHS,
    include_news: Annotated[bool, "Include news (default: True)."] = True,
    max_news: Annotated[
        int, "Max news articles (default: 5, max: 5)."
    ] = MAX_NEWS_ARTICLES,
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

    location_desc = get_location_description(uf, city_code)
    metrics = _fetch_all_metrics(uf, city_code)
    news = _fetch_news(location_desc, include_news, max_news)

    executive_summary = ""
    if include_executive_summary:
        executive_summary = generate_executive_summary(metrics, news, location_desc)

    metrics_table = ""
    if include_metrics:
        metrics_table = format_metrics_table(metrics, news)

    report_lines = [f"# Relatório SRAG — {location_desc}"]

    if include_executive_summary:
        report_lines.extend(["", "## Resumo Executivo", "", executive_summary, ""])

    if include_metrics:
        report_lines.extend(["", metrics_table, ""])

    report_lines.append("## Gráficos Interativos")

    if include_news and news:
        report_lines.append("")
        report_lines.append(format_news_section(news, detailed=False))

    report_text = "\n".join(report_lines)

    daily_chart_json = get_daily_chart_json.invoke({"uf": uf, "days": days})
    monthly_chart_json = get_monthly_chart_json.invoke({"uf": uf, "months": months})

    return {
        "report_text": report_text,
        "daily_chart_json": daily_chart_json,
        "monthly_chart_json": monthly_chart_json,
        "metrics": metrics,
        "news": news,
    }
