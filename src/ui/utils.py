"""UI utility functions."""

import re
from datetime import datetime
from pathlib import Path

from plotly.graph_objects import Figure

from elt.load import get_extraction_date
from ui.constants import WELCOME_MESSAGE
from ui.message import create_message_bubble


def get_initial_store() -> dict:
    """Create initial store data with welcome message."""
    return {
        "messages": [
            {
                "role": "assistant",
                "content": WELCOME_MESSAGE,
                "chart_figure_dicts": [],
                "report_file_path": None,
                "is_explicit_generation": False,
            }
        ],
        "thread_id": None,
    }


def render_messages(messages: list[dict]) -> list:
    """Render list of message dictionaries as Dash components."""
    if not messages:
        return [create_message_bubble("assistant", WELCOME_MESSAGE)]

    rendered = []
    for msg in messages:
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        chart_dicts = msg.get("chart_figure_dicts", [])
        report_path = msg.get("report_file_path")

        chart_figures = [Figure(d) for d in chart_dicts] if chart_dicts else []
        rendered.append(
            create_message_bubble(
                role, content, chart_figures, report_file_path=report_path
            )
        )

    return rendered


def extract_file_path(text: str) -> str | None:
    """Extract report file path from response text."""
    patterns = [
        r"(/[^\s]+/reports/[^\s]+\.md)",
        r"File path:\s*([^\s\n]+\.md)",
        r'file_path["\']?:\s*["\']?([^\s"\',\n]+\.md)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            file_path = match.group(1)
            if Path(file_path).exists():
                return file_path
    return None


def format_extraction_date(date_str: str | None) -> str:
    """Format extraction date for display."""
    if not date_str:
        return "Nenhuma extração realizada ainda"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return f"Última extração: {dt.strftime('%d/%m/%Y %H:%M')}"
    except Exception:
        return f"Última extração: {date_str}"


def load_extraction_date() -> str:
    """Load and format last extraction date."""
    date_str = get_extraction_date()
    return format_extraction_date(date_str)
