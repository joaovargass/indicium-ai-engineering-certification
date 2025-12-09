"""Loading indicator components."""

from dash import html


def create_loading_indicator(step_message: str) -> html.Div:
    """
    Create animated gradient text loading indicator.

    Args:
        step_message: Current step message to display

    Returns:
        html.Div with animated gradient text

    """
    return html.Div(
        html.Div(
            html.Span(step_message, className="gradient-text"),
            className="loading-indicator-box",
        ),
        className="loading-indicator-wrapper",
    )
