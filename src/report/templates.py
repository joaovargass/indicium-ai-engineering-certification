"""Jinja2 templates for SRAG reports."""

from datetime import datetime

from jinja2 import Template

from common.config import (
    CHART_DAYS_MAX,
    CHART_DAYS_MIN,
    CHART_MONTHS_MAX,
    CHART_MONTHS_MIN,
    MAX_NEWS_ARTICLES,
)


def validate_report_request(
    days: int,
    months: int,
    max_news: int,
) -> tuple[bool, str]:
    """
    Validate report generation request parameters.

    Args:
        days: Days for daily chart
        months: Months for monthly chart
        max_news: Maximum number of news articles

    Returns:
        Tuple of (is_valid, error_message)

    """
    if days < CHART_DAYS_MIN or days > CHART_DAYS_MAX:
        return False, f"Days must be between {CHART_DAYS_MIN} and {CHART_DAYS_MAX}"

    if months < CHART_MONTHS_MIN or months > CHART_MONTHS_MAX:
        return (
            False,
            f"Months must be between {CHART_MONTHS_MIN} and {CHART_MONTHS_MAX}",
        )

    if max_news < 0 or max_news > MAX_NEWS_ARTICLES:
        return (
            False,
            f"Maximum {MAX_NEWS_ARTICLES} news articles allowed (0-{MAX_NEWS_ARTICLES})",
        )

    return True, ""


def render_integrated_report(
    location: str,
    report_body: str,
    charts_section: str,
    sources_section: str,
    include_charts: bool = True,
) -> str:
    """
    Render integrated report with seamless narrative.

    Args:
        location: Location description
        report_body: Integrated narrative text
        charts_section: Charts description section (only if include_charts=True)
        sources_section: Sources section (only if news were included)
        include_charts: Whether charts were confirmed for inclusion

    Returns:
        Complete report as Markdown string

    """
    template_str = """# Relatório SRAG — {{ location }}
**Gerado em:** {{ generation_date }}

{{ report_body }}

{% if include_charts and charts_section %}
{{ charts_section }}

{% endif %}
{{ sources_section }}

---

**Fonte de Dados:** OpenDATASUS SRAG Dataset (2023-2025)
*Gerado automaticamente pelo Agente SRAG com análises contextualizadas.*
"""

    template = Template(template_str)
    generation_date = datetime.now().strftime("%d/%m/%Y %H:%M")

    return template.render(
        location=location,
        generation_date=generation_date,
        report_body=report_body,
        charts_section=charts_section,
        sources_section=sources_section,
        include_charts=include_charts,
    )
