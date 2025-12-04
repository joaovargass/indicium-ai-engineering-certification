"""Report generation module for SRAG situation reports."""

from report.templater import (
    format_metrics_table,
    format_news_section,
    generate_executive_summary,
    generate_metric_explanation,
    render_report_template,
    save_report_to_file,
    validate_report_request,
)

__all__ = [
    "format_metrics_table",
    "format_news_section",
    "generate_executive_summary",
    "generate_metric_explanation",
    "render_report_template",
    "save_report_to_file",
    "validate_report_request",
]

