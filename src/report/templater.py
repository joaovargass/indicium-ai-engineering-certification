"""
Report templating - backward compatibility facade.

This module re-exports public report functionality for backward compatibility.
New code should import directly from the appropriate submodules:
- report.llm: LLM integration
- report.formatter: Formatting functions
- report.generator: Report body generation
- report.templates: Jinja2 templates
- report.files: File operations
- report.parser: Report parsing

Note: Private functions (prefixed with _) are not re-exported.
Import them directly from their source modules if needed.

"""

from report.files import save_report_to_file, save_report_zip
from report.formatter import format_metrics_table, format_news_section
from report.generator import generate_report_body
from report.llm import generate_executive_summary, generate_metric_explanation
from report.parser import generate_report_summary
from report.templates import render_integrated_report, validate_report_request

__all__ = [
    # LLM
    "generate_executive_summary",
    "generate_metric_explanation",
    # Formatter
    "format_metrics_table",
    "format_news_section",
    # Generator
    "generate_report_body",
    # Templates
    "render_integrated_report",
    "validate_report_request",
    # Files
    "save_report_to_file",
    "save_report_zip",
    # Parser
    "generate_report_summary",
]
