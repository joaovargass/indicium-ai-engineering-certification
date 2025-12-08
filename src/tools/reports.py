"""Report generation tools for SRAG situation reports."""

import shutil
import tempfile
from pathlib import Path
from typing import Annotated, Any

import pandas as pd
from langchain_core.tools import tool

from charts.charts import figure_to_image_file, plot_daily_cases, plot_monthly_cases
from elt.load import NoDataAvailableError, load_srag_data
from report.templater import (
    format_metrics_table,
    format_news_section,
    generate_executive_summary,
    generate_integrated_report_body,
    generate_report_summary,
    render_integrated_report,
    render_report_template,
    save_report_to_file,
    save_report_with_images_to_zip,
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


def _extract_daily_chart_stats(
    df: pd.DataFrame,
    location_col: str | None,
    location_value: str | None,
    days: int,
) -> dict[str, Any] | None:
    """Extract statistics from daily chart data."""
    from datetime import timedelta
    
    date_col = "DT_SIN_PRI"
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    
    if location_col and location_value:
        df = df.dropna(subset=[date_col, location_col])
        df = df[df[location_col] == location_value]
    else:
        df = df.dropna(subset=[date_col])
    
    end_date = df[date_col].max()
    if pd.isna(end_date):
        return None
    
    start_date = end_date - timedelta(days=days)
    df_filtered = df[(df[date_col] >= start_date) & (df[date_col] <= end_date)].copy()
    
    daily_counts = df_filtered.groupby(date_col).size().reset_index(name="casos")
    daily_counts = daily_counts.sort_values(date_col)
    
    if len(daily_counts) == 0:
        return None
    
    total_cases = daily_counts["casos"].sum()
    avg_daily = daily_counts["casos"].mean()
    max_daily = daily_counts["casos"].max()
    max_date = daily_counts.loc[daily_counts["casos"].idxmax(), date_col]
    
    # Calculate trend (comparing first half vs second half)
    mid_point = len(daily_counts) // 2
    first_half_avg = daily_counts.iloc[:mid_point]["casos"].mean() if mid_point > 0 else avg_daily
    second_half_avg = daily_counts.iloc[mid_point:]["casos"].mean() if mid_point < len(daily_counts) else avg_daily
    trend_direction = "increasing" if second_half_avg > first_half_avg else "decreasing" if second_half_avg < first_half_avg else "stable"
    trend_percentage = abs((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
    
    return {
        "chart_type": "daily",
        "total_cases": int(total_cases),
        "avg_daily": float(avg_daily),
        "max_daily": int(max_daily),
        "max_date": max_date,
        "trend_direction": trend_direction,
        "trend_percentage": float(trend_percentage),
    }


def _extract_monthly_chart_stats(
    df: pd.DataFrame,
    location_col: str | None,
    location_value: str | None,
    months: int,
) -> dict[str, Any] | None:
    """Extract statistics from monthly chart data."""
    date_col = "DT_SIN_PRI"
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    
    if location_col and location_value:
        df = df.dropna(subset=[date_col, location_col])
        df = df[df[location_col] == location_value]
    else:
        df = df.dropna(subset=[date_col])
    
    end_date = df[date_col].max()
    if pd.isna(end_date):
        return None
    
    data_min_date = df[date_col].min()
    desired_start_date = end_date - pd.DateOffset(months=months)
    start_date = max(desired_start_date, data_min_date)
    
    df_filtered = df[(df[date_col] >= start_date) & (df[date_col] <= end_date)].copy()
    
    df_filtered["ano_mes"] = df_filtered[date_col].dt.to_period("M")
    monthly_counts = df_filtered.groupby("ano_mes").size().reset_index(name="casos")
    monthly_counts["ano_mes"] = monthly_counts["ano_mes"].dt.to_timestamp()
    monthly_counts = monthly_counts.sort_values("ano_mes")
    
    if len(monthly_counts) == 0:
        return None
    
    total_cases = monthly_counts["casos"].sum()
    avg_monthly = monthly_counts["casos"].mean()
    max_monthly = monthly_counts["casos"].max()
    max_date = monthly_counts.loc[monthly_counts["casos"].idxmax(), "ano_mes"]
    
    # Calculate trend
    if len(monthly_counts) >= 2:
        first_half_avg = monthly_counts.iloc[:len(monthly_counts)//2]["casos"].mean()
        second_half_avg = monthly_counts.iloc[len(monthly_counts)//2:]["casos"].mean()
        trend_direction = "increasing" if second_half_avg > first_half_avg else "decreasing" if second_half_avg < first_half_avg else "stable"
        trend_percentage = abs((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
    else:
        trend_direction = "stable"
        trend_percentage = 0.0
    
    return {
        "chart_type": "monthly",
        "total_cases": int(total_cases),
        "avg_monthly": float(avg_monthly),
        "max_monthly": int(max_monthly),
        "max_date": max_date,
        "trend_direction": trend_direction,
        "trend_percentage": float(trend_percentage),
    }


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

    # Check if any metric returned an error (no data available)
    for metric_name, metric_data in metrics.items():
        if isinstance(metric_data, dict) and "error" in metric_data:
            return {
                "error": metric_data["error"],
                "report_content": "",
                "file_path": "",
                "file_size": 0,
            }

    news = _fetch_news(location_desc, include_news, max_news)

    # Generate charts and images if requested, and extract statistics
    charts_section = ""
    image_files = {}
    temp_dir = None
    chart_info = None

    if include_charts:
        # Load data and generate actual Plotly figures
        try:
            df = load_srag_data()
        except NoDataAvailableError as e:
            return {
                "error": str(e),
                "report_content": "",
                "file_path": "",
                "file_size": 0,
            }
        location_col, location_value = determine_location_filter(uf, city_code)
        
        # Extract chart statistics for integration
        daily_stats = _extract_daily_chart_stats(df, location_col, location_value, days)
        monthly_stats = _extract_monthly_chart_stats(df, location_col, location_value, months)
        
        # Combine both chart stats if available
        chart_info = {}
        if daily_stats:
            chart_info["daily"] = daily_stats
        if monthly_stats:
            chart_info["monthly"] = monthly_stats
        
        # If only one chart type, use it directly for simpler prompt
        if len(chart_info) == 1:
            chart_info = list(chart_info.values())[0]
        
        # Create temporary directory for images (keep until zip is created)
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)
        
        # Generate daily chart
        daily_fig = plot_daily_cases(
            df, location_col=location_col, location_value=location_value, days=days
        )
        daily_image_path = temp_path / "grafico_diario.png"
        figure_to_image_file(daily_fig, daily_image_path)
        image_files["grafico_diario.png"] = daily_image_path
        
        # Generate monthly chart
        monthly_fig = plot_monthly_cases(
            df, location_col=location_col, location_value=location_value, months=months
        )
        monthly_image_path = temp_path / "grafico_mensal.png"
        figure_to_image_file(monthly_fig, monthly_image_path)
        image_files["grafico_mensal.png"] = monthly_image_path
        
        # Format charts section with image references
        charts_section = f"""**Gráfico 1:** Número diário de casos dos últimos {days} dias

![Gráfico Diário](grafico_diario.png)

**Gráfico 2:** Número mensal de casos dos últimos {months} meses

![Gráfico Mensal](grafico_mensal.png)"""

    # Generate integrated report body (only uses confirmed components)
    report_body, sources_section = generate_integrated_report_body(
        metrics=metrics,
        news=news,
        location=location_desc,
        chart_info=chart_info,
        include_metrics=include_metrics,
        include_news=include_news,
        include_charts=include_charts,
    )

    # Render using integrated template
    report_content = render_integrated_report(
        location=location_desc,
        report_body=report_body,
        charts_section=charts_section,
        sources_section=sources_section,
        include_charts=include_charts,
    )

    # Save to zip file with images if charts were generated, otherwise save as markdown
    if include_charts and image_files:
        zip_path = save_report_with_images_to_zip(
            report_content, location_desc, image_files
        )
        file_size = zip_path.stat().st_size
        file_path = zip_path
        
        # Clean up temporary directory
        if temp_dir and Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
    else:
        file_path = save_report_to_file(report_content, location_desc)
        file_size = file_path.stat().st_size

    # Auto-generate summary for chat display
    summary = generate_report_summary(report_content)

    return {
        "report_content": report_content,
        "report_summary": summary,
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
