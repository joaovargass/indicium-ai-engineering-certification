"""Download button and file handling components."""

import base64
from pathlib import Path

import dash_bootstrap_components as dbc
from dash import html
from dash.exceptions import PreventUpdate


def create_download_button(file_path: str, button_id: str | None = None) -> html.Div:
    """
    Create a styled download button for report files.

    Args:
        file_path: Path to the report file
        button_id: Optional button ID for callback targeting

    Returns:
        html.Div containing styled download button

    """
    path = Path(file_path)
    filename = path.name if path.exists() else "report.md"

    return html.Div(
        [
            html.Div(
                [
                    html.P(
                        filename,
                        className="small mb-2 download-filename",
                    ),
                    dbc.Button(
                        "Baixar",
                        id=button_id or "download-report-btn",
                        color="success",
                        size="md",
                        className="w-100 download-btn",
                    ),
                ],
                className="download-container",
            ),
        ],
    )


def handle_download_click(n_clicks: int | None, store_data: dict | None) -> dict:
    """
    Handle download button click - find latest report and trigger download.

    Args:
        n_clicks: Number of button clicks
        store_data: Chat store data containing messages

    Returns:
        Dictionary with file content for download

    """
    if not n_clicks or not store_data:
        raise PreventUpdate

    # Find the most recent message with a report file path
    messages = store_data.get("messages", [])
    report_file_path = None

    # Search from most recent to oldest
    for msg in reversed(messages):
        if msg.get("report_file_path"):
            report_file_path = msg.get("report_file_path")
            break

    if not report_file_path:
        raise PreventUpdate

    report_path = Path(report_file_path)
    if not report_path.exists():
        raise PreventUpdate

    # Read file and return for download
    try:
        # Check if it's a zip file (binary) or markdown (text)
        if report_path.suffix == ".zip":
            with open(report_path, "rb") as f:
                content = f.read()
            content_b64 = base64.b64encode(content).decode("utf-8")
            return {
                "content": content_b64,
                "filename": report_path.name,
                "base64": True,
                "type": "application/zip",
            }
        else:
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"content": content, "filename": report_path.name}
    except Exception:
        raise PreventUpdate from None
