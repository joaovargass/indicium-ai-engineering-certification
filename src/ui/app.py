"""Main Dash application with AI chat interface."""

import re
import sys
import uuid
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback_context, html, clientside_callback
from dash.exceptions import PreventUpdate
from plotly.graph_objects import Figure

# Add src to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from agent import invoke_agent  # noqa: E402
from agent.graph import _convert_ui_messages_to_langchain  # noqa: E402
from ui.components.chat_components import (  # noqa: E402
    WELCOME_MESSAGE,
    create_chat_layout,
    create_loading_indicator,
    create_message_bubble,
    parse_agent_response,
)

# Shared state for loading step updates
_current_loading_step = {"step": "Pensando..."}


def _create_initial_store() -> dict:
    """Create initial store data with welcome message."""
    return {
        "messages": [{
            "role": "assistant",
            "content": WELCOME_MESSAGE,
            "chart_figure_dicts": [],
            "report_file_path": None,
            "is_explicit_generation": False,
        }],
        "thread_id": None,
    }


def create_app() -> dash.Dash:
    """
    Create main Dash application with AI chat interface.

    Returns:
        Configured Dash app instance

    """
    # Get project root to find assets folder
    assets_path = PROJECT_ROOT / "assets"

    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True,
        assets_folder=str(assets_path) if assets_path.exists() else None,
    )

    # Main layout with chat interface
    app.layout = dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.H1(
                        "Plataforma de Análise de Dados SRAG",
                        className="text-center mb-4 mt-3",
                    )
                )
            ),
            create_chat_layout(),
        ],
        fluid=True,
    )

    # Register callbacks
    _register_chat_callbacks(app)

    return app


def _handle_user_message_immediate(
    n_clicks: int,
    n_submit: int,
    user_input: str | None,
    store_data: dict,
    scroll_trigger: int,
) -> tuple[list, dict, str, bool, dict, dict, bool, int]:
    """Add user message to UI instantly and trigger agent processing."""
    if store_data is None:
        store_data = _create_initial_store()

    # Only process if triggered by send button or enter key
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    triggered_id = ctx.triggered[0]["prop_id"]
    if triggered_id not in ["chat-send-button.n_clicks", "chat-input.n_submit"]:
        raise PreventUpdate

    if not user_input or not user_input.strip():
        raise PreventUpdate

    # Get or create thread_id
    thread_id = store_data.get("thread_id") or str(uuid.uuid4())
    store_data["thread_id"] = thread_id

    # Add user message
    messages = store_data.get("messages", [])
    messages.append({"role": "user", "content": user_input})
    store_data["messages"] = messages

    return (
        _render_messages(messages),
        store_data,
        "",  # Clear input
        True,  # Show loading
        {"user_input": user_input, "thread_id": thread_id},  # Pending request
        {"step": "Thinking..."},
        False,  # Enable interval
        (scroll_trigger or 0) + 1,  # Increment scroll trigger
    )


def _process_agent_response(
    pending_request: dict | None,
    store_data: dict,
    scroll_trigger: int,
) -> tuple[list, dict, bool, dict, int]:
    """Process agent response and update UI."""
    if not pending_request or not store_data:
        raise PreventUpdate

    user_input = pending_request.get("user_input")
    thread_id = pending_request.get("thread_id")
    if not user_input or not thread_id:
        raise PreventUpdate

    messages = store_data.get("messages", [])

    try:
        _current_loading_step["step"] = "Pensando..."

        def update_step(msg: str) -> None:
            _current_loading_step["step"] = msg

        # Extract conversation history (exclude current user input already added)
        conversation_history_ui = [
            msg
            for msg in (messages[:-1] if len(messages) > 1 else [])
            if isinstance(msg, dict) and "role" in msg and "content" in msg
        ]
        conversation_history = _convert_ui_messages_to_langchain(conversation_history_ui)

        result = invoke_agent(
            user_input,
            thread_id=thread_id,
            step_callback=update_step,
            conversation_history=conversation_history,
        )
        text_content, chart_figures, report_file_path, is_explicit_generation = parse_agent_response(result)

        # Fallback: extract file path from text content if not found in tool messages
        if not report_file_path:
            report_file_path = _extract_file_path_from_text(text_content)
            if report_file_path:
                is_explicit_generation = True

        # Convert Figure objects to dicts for JSON serialization in dcc.Store
        chart_figure_dicts = [fig.to_dict() for fig in chart_figures] if chart_figures else []

        messages.append({
            "role": "assistant",
            "content": text_content,
            "chart_figure_dicts": chart_figure_dicts,
            "report_file_path": report_file_path,
            "is_explicit_generation": is_explicit_generation,
        })

    except Exception as e:
        messages.append({
            "role": "assistant",
            "content": f"Desculpe, ocorreu um erro: {e}",
            "chart_figure_dicts": [],
            "report_file_path": None,
            "is_explicit_generation": False,
        })

    store_data["messages"] = messages
    store_data["thread_id"] = thread_id

    return _render_messages(messages), store_data, False, None, (scroll_trigger or 0) + 1


def _update_loading_step(n_intervals: int, is_loading: bool) -> tuple[dict, bool]:
    """Update loading step from shared state."""
    if not is_loading:
        return {"step": "Pensando..."}, True
    return {"step": _current_loading_step.get("step", "Pensando...")}, False


def _display_loading_indicator(is_loading: bool, step_data: dict) -> list:
    """Display loading indicator with current step message."""
    if not is_loading:
        return []
    step_message = (step_data or {}).get("step", "Pensando...")
    return [create_loading_indicator(step_message)]


def _update_loading_indicator_visibility(is_loading: bool) -> dict:
    """Show/hide loading indicator container."""
    base_style = {
        "position": "absolute",
        "top": "0",
        "bottom": "0",
        "left": "0",
        "right": "0",
        "padding": "1rem",
        "zIndex": "1000",
        "alignItems": "flex-end",
        "justifyContent": "center",
    }
    return {**base_style, "display": "flex" if is_loading else "none"}


def _clear_conversation(n_clicks: int, store_data: dict | None, scroll_trigger: int) -> tuple[dict, list, int]:
    """Clear conversation history."""
    if store_data is None:
        store_data = _create_initial_store()

    ctx = callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]["prop_id"]
        if triggered_id == "chat-clear-button.n_clicks" and n_clicks and n_clicks > 0:
            new_store = _create_initial_store()
            return new_store, _render_messages(new_store["messages"]), (scroll_trigger or 0) + 1

    return store_data, _render_messages(store_data.get("messages", [])), scroll_trigger or 0


def _register_chat_callbacks(app: dash.Dash) -> None:
    """Register callbacks for chat interface."""
    # Callback 1: IMMEDIATE update - add user message and show loading
    app.callback(
        [
            Output("chat-messages", "children"),
            Output("chat-store", "data", allow_duplicate=True),
            Output("chat-input", "value"),
            Output("chat-loading", "data", allow_duplicate=True),
            Output("chat-pending-request", "data", allow_duplicate=True),
            Output("chat-loading-step", "data", allow_duplicate=True),
            Output("chat-loading-interval", "disabled", allow_duplicate=True),
            Output("chat-scroll-trigger", "data", allow_duplicate=True),
        ],
        [
            Input("chat-send-button", "n_clicks"),
            Input("chat-input", "n_submit"),
        ],
        [
            State("chat-input", "value"),
            State("chat-store", "data"),
            State("chat-scroll-trigger", "data"),
        ],
        prevent_initial_call=True,
    )(_handle_user_message_immediate)

    # Callback 2: Process agent response (triggered by pending request)
    app.callback(
        [
            Output("chat-messages", "children", allow_duplicate=True),
            Output("chat-store", "data", allow_duplicate=True),
            Output("chat-loading", "data", allow_duplicate=True),
            Output("chat-pending-request", "data", allow_duplicate=True),
            Output("chat-scroll-trigger", "data", allow_duplicate=True),
        ],
        Input("chat-pending-request", "data"),
        [
            State("chat-store", "data"),
            State("chat-scroll-trigger", "data"),
        ],
        prevent_initial_call=True,
    )(_process_agent_response)

    app.callback(
        [
            Output("chat-loading-step", "data", allow_duplicate=True),
            Output("chat-loading-interval", "disabled"),
        ],
        [
            Input("chat-loading-interval", "n_intervals"),
            Input("chat-loading", "data"),
        ],
        prevent_initial_call=True,
    )(_update_loading_step)

    app.callback(
        Output("chat-loading-indicator", "children"),
        [
            Input("chat-loading", "data"),
            Input("chat-loading-step", "data"),
        ],
        prevent_initial_call=True,
    )(_display_loading_indicator)

    app.callback(
        Output("chat-loading-indicator", "style"),
        Input("chat-loading", "data"),
    )(_update_loading_indicator_visibility)

    app.callback(
        [
            Output("chat-store", "data", allow_duplicate=True),
            Output("chat-messages", "children", allow_duplicate=True),
            Output("chat-scroll-trigger", "data", allow_duplicate=True),
        ],
        Input("chat-clear-button", "n_clicks"),
        [
            State("chat-store", "data"),
            State("chat-scroll-trigger", "data"),
        ],
        prevent_initial_call=True,
    )(_clear_conversation)

    # Download callback - triggered when download button is clicked
    app.callback(
        Output("chat-download", "data"),
        Input("download-report-btn", "n_clicks"),
        State("chat-store", "data"),
        prevent_initial_call=True,
    )(_handle_download_click)

    # Auto-scroll to bottom when messages update
    app.clientside_callback(
        """
        function(scrollTrigger, currentStyle) {
            if (scrollTrigger > 0) {
                const messagesDiv = document.getElementById('chat-messages');
                if (messagesDiv) {
                    setTimeout(function() {
                        messagesDiv.scrollTop = messagesDiv.scrollHeight;
                    }, 100);
                }
            }
            return currentStyle || {};
        }
        """,
        Output("chat-messages", "style"),
        Input("chat-scroll-trigger", "data"),
        State("chat-messages", "style"),
        prevent_initial_call=True,
    )


def _render_messages(messages: list[dict]) -> list:
    """Render list of message dictionaries as Dash components."""
    if not messages:
        return [create_message_bubble("assistant", WELCOME_MESSAGE)]

    rendered = []
    for msg in messages:
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        chart_figure_dicts = msg.get("chart_figure_dicts", [])
        report_file_path = msg.get("report_file_path")

        chart_figures = [Figure(d) for d in chart_figure_dicts] if chart_figure_dicts else []
        rendered.append(create_message_bubble(
            role,
            content,
            chart_figures,
            report_file_path=report_file_path,
        ))

    return rendered


def _extract_file_path_from_text(text: str) -> str | None:
    """Extract report file path from response text."""
    patterns = [
        r'(/[^\s]+/reports/[^\s]+\.md)',  # Unix path to .md in reports folder
        r'File path:\s*([^\s\n]+\.md)',   # "File path: /path/to/file.md"
        r'file_path["\']?:\s*["\']?([^\s"\',\n]+\.md)',  # JSON-like file_path
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            file_path = match.group(1)
            if Path(file_path).exists():
                return file_path
    return None


def _handle_download_click(n_clicks: int | None, store_data: dict | None) -> dict:
    """Handle download button click - find latest report and trigger download."""
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
            # For binary content, use base64 encoding
            import base64
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


def main() -> None:
    """Run the Dash application."""
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=8050)


if __name__ == "__main__":
    main()
