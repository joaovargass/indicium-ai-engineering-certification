"""Message bubble components."""

from pathlib import Path

import dash_bootstrap_components as dbc
from dash import dcc, html
from plotly.graph_objects import Figure

from ui.download import create_download_button


def render_markdown_content(content: str) -> list:
    """Render markdown content with proper styling."""
    return [
        dcc.Markdown(
            content,
            className="mb-2 markdown-content",
            dangerously_allow_html=True,
        )
    ]


def create_message_bubble(
    role: str,
    content: str,
    chart_figures: list[Figure] | None = None,
    report_file_path: str | None = None,
) -> dbc.Card:
    """
    Create a message bubble for chat interface.

    Args:
        role: "user" or "assistant"
        content: Message text content
        chart_figures: Optional list of Plotly Figure objects
        report_file_path: Optional path to downloadable report file

    Returns:
        dbc.Card component styled as message bubble

    """
    is_user = role == "user"
    message_children = _build_message_content(is_user, content)

    if chart_figures:
        for fig in chart_figures:
            message_children.append(_create_chart_component(fig))

    if report_file_path and Path(report_file_path).exists():
        message_children.append(create_download_button(report_file_path))

    has_attachments = bool(chart_figures or report_file_path)
    return _create_card(is_user, message_children, has_attachments)


def _build_message_content(is_user: bool, content: str) -> list:
    """Build message content based on role."""
    if is_user:
        return [html.Div(content, className="mb-2 user-message-text")]
    return render_markdown_content(content)


def _create_chart_component(fig: Figure) -> dcc.Graph:
    """Create chart graph component."""
    return dcc.Graph(
        figure=fig,
        config={"displayModeBar": True, "responsive": True},
        className="chat-chart-graph",
    )


def _create_card(
    is_user: bool,
    children: list,
    has_attachments: bool,
) -> dbc.Card:
    """Create styled card for message bubble."""
    margin_class = "ms-auto" if is_user else "me-auto"
    message_class = "user-message" if is_user else "assistant-message"
    attachment_class = "has-attachments" if has_attachments else ""

    class_name = f"mb-3 {margin_class} {message_class} chat-message-bubble {attachment_class}".strip()

    return dbc.Card(
        dbc.CardBody(children, className="chat-card-body"),
        className=class_name,
        color="primary" if is_user else None,
        inverse=is_user,
    )
