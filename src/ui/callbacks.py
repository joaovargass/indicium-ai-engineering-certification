"""
Chat callback handlers for Dash UI.

This module registers and implements all chat-related callbacks:
- Message submission and processing
- Loading indicator updates
- Conversation clearing
- Report download handling
- Auto-scroll behavior

The callbacks follow a two-phase pattern:
1. _handle_user_message: Immediately shows user message and triggers loading
2. _process_agent_response: Invokes agent and displays response

"""

import uuid

import dash
from dash import Input, Output, State, callback_context
from dash.exceptions import PreventUpdate

from agent import invoke_agent
from agent.graph import _to_langchain_messages
from ui.constants import (
    LOADING_DEFAULT_MESSAGE,
    LOADING_HIDDEN_CLASS,
    LOADING_VISIBLE_CLASS,
)
from ui.download import handle_download_click
from ui.loading import create_loading_indicator
from ui.response_parsing import parse_agent_response
from ui.utils import extract_file_path, get_initial_store, render_messages

# Shared mutable state for loading step message (updated by agent callback)
_current_loading_step: dict[str, str] = {"step": LOADING_DEFAULT_MESSAGE}


def register_chat_callbacks(app: dash.Dash) -> None:
    """
    Register all chat-related callbacks with the Dash app.

    This sets up the complete chat interaction flow including:
    - Message submission (button click or Enter key)
    - Agent response processing
    - Loading indicator animation
    - Conversation clearing
    - Report download handling
    - Auto-scroll to latest message

    Args:
        app: Dash application instance

    """
    _register_send_message_callback(app)
    _register_process_response_callback(app)
    _register_loading_callbacks(app)
    _register_clear_callback(app)
    _register_download_callback(app)
    _register_scroll_callback(app)


def _register_send_message_callback(app: dash.Dash) -> None:
    """Register callback for sending messages."""
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
            Output("chat-send-button", "disabled", allow_duplicate=True),
            Output("chat-input", "disabled", allow_duplicate=True),
        ],
        [Input("chat-send-button", "n_clicks"), Input("chat-input", "n_submit")],
        [
            State("chat-input", "value"),
            State("chat-store", "data"),
            State("chat-scroll-trigger", "data"),
        ],
        prevent_initial_call=True,
    )(_handle_user_message)


def _register_process_response_callback(app: dash.Dash) -> None:
    """Register callback for processing agent response."""
    app.callback(
        [
            Output("chat-messages", "children", allow_duplicate=True),
            Output("chat-store", "data", allow_duplicate=True),
            Output("chat-loading", "data", allow_duplicate=True),
            Output("chat-pending-request", "data", allow_duplicate=True),
            Output("chat-scroll-trigger", "data", allow_duplicate=True),
            Output("chat-send-button", "disabled", allow_duplicate=True),
            Output("chat-input", "disabled", allow_duplicate=True),
        ],
        Input("chat-pending-request", "data"),
        [State("chat-store", "data"), State("chat-scroll-trigger", "data")],
        prevent_initial_call=True,
    )(_process_agent_response)


def _register_loading_callbacks(app: dash.Dash) -> None:
    """Register loading indicator callbacks."""
    app.callback(
        [
            Output("chat-loading-step", "data", allow_duplicate=True),
            Output("chat-loading-interval", "disabled"),
        ],
        [Input("chat-loading-interval", "n_intervals"), Input("chat-loading", "data")],
        prevent_initial_call=True,
    )(_update_loading_step)

    app.callback(
        Output("chat-loading-indicator", "children"),
        [Input("chat-loading", "data"), Input("chat-loading-step", "data")],
        prevent_initial_call=True,
    )(_display_loading_indicator)

    app.callback(
        Output("chat-loading-indicator", "className"),
        Input("chat-loading", "data"),
    )(_update_loading_visibility)


def _register_clear_callback(app: dash.Dash) -> None:
    """Register conversation clear callback."""
    app.callback(
        [
            Output("chat-store", "data", allow_duplicate=True),
            Output("chat-messages", "children", allow_duplicate=True),
            Output("chat-scroll-trigger", "data", allow_duplicate=True),
            Output("chat-pending-request", "data", allow_duplicate=True),
            Output("chat-loading", "data", allow_duplicate=True),
            Output("chat-loading-interval", "disabled", allow_duplicate=True),
            Output("chat-send-button", "disabled", allow_duplicate=True),
            Output("chat-input", "disabled", allow_duplicate=True),
        ],
        Input("chat-clear-button", "n_clicks"),
        [State("chat-store", "data"), State("chat-scroll-trigger", "data")],
        prevent_initial_call=True,
    )(_clear_conversation)


def _register_download_callback(app: dash.Dash) -> None:
    """Register download callback."""
    app.callback(
        Output("chat-download", "data"),
        Input("download-report-btn", "n_clicks"),
        State("chat-store", "data"),
        prevent_initial_call=True,
    )(handle_download_click)


def _register_scroll_callback(app: dash.Dash) -> None:
    """Register auto-scroll callback."""
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


# Callback handler functions


def _handle_user_message(
    n_clicks: int,
    n_submit: int,
    user_input: str | None,
    store_data: dict,
    scroll_trigger: int,
) -> tuple[list, dict, str, bool, dict, dict, bool, int, bool, bool]:
    """
    Handle user message submission (phase 1 of chat interaction).

    Immediately adds user message to display, clears input, and triggers
    the agent processing callback via pending request store.

    Args:
        n_clicks: Send button click count
        n_submit: Input field submit count (Enter key)
        user_input: Text entered by user
        store_data: Current chat store data
        scroll_trigger: Current scroll trigger value

    Returns:
        Tuple of outputs for all callback targets

    Raises:
        PreventUpdate: If no valid trigger or empty input

    """
    if store_data is None:
        store_data = get_initial_store()

    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    triggered_id = ctx.triggered[0]["prop_id"]
    if triggered_id not in ["chat-send-button.n_clicks", "chat-input.n_submit"]:
        raise PreventUpdate

    if not user_input or not user_input.strip():
        raise PreventUpdate

    thread_id = store_data.get("thread_id") or str(uuid.uuid4())
    store_data["thread_id"] = thread_id

    messages = store_data.get("messages", [])
    messages.append({"role": "user", "content": user_input})
    store_data["messages"] = messages

    return (
        render_messages(messages),
        store_data,
        "",
        True,
        {"user_input": user_input, "thread_id": thread_id},
        {"step": "Thinking..."},
        False,
        (scroll_trigger or 0) + 1,
        True,
        True,
    )


def _process_agent_response(
    pending_request: dict | None,
    store_data: dict,
    scroll_trigger: int,
) -> tuple[list, dict, bool, None, int, bool, bool]:
    """
    Process agent response (phase 2 of chat interaction).

    Invokes the LangGraph agent with the user message, parses the response
    to extract text, charts, and report paths, then updates the chat display.

    Args:
        pending_request: Dict with user_input and thread_id
        store_data: Current chat store data
        scroll_trigger: Current scroll trigger value

    Returns:
        Tuple of outputs including rendered messages and updated store

    Raises:
        PreventUpdate: If no pending request or conversation was cleared

    """
    if not pending_request or not store_data:
        raise PreventUpdate

    # Check if conversation was cleared (store has only welcome message)
    messages = store_data.get("messages", [])
    if len(messages) <= 1 and messages and messages[0].get("role") == "assistant":
        # Only welcome message remains - conversation was cleared, stop processing
        raise PreventUpdate

    user_input = pending_request.get("user_input")
    thread_id = pending_request.get("thread_id")
    if not user_input or not thread_id:
        raise PreventUpdate

    try:
        _current_loading_step["step"] = LOADING_DEFAULT_MESSAGE

        def update_step(msg: str) -> None:
            _current_loading_step["step"] = msg

        history_ui = [
            m
            for m in (messages[:-1] if len(messages) > 1 else [])
            if isinstance(m, dict)
        ]
        history = _to_langchain_messages(history_ui)

        result = invoke_agent(
            user_input,
            thread_id=thread_id,
            step_callback=update_step,
            conversation_history=history,
        )
        text, charts, report_path, is_explicit = parse_agent_response(result)

        if not report_path:
            report_path = extract_file_path(text)
            if report_path:
                is_explicit = True

        chart_dicts = [fig.to_dict() for fig in charts] if charts else []
        messages.append(
            {
                "role": "assistant",
                "content": text,
                "chart_figure_dicts": chart_dicts,
                "report_file_path": report_path,
                "is_explicit_generation": is_explicit,
            }
        )

    except Exception as e:
        messages.append(
            {
                "role": "assistant",
                "content": f"Desculpe, ocorreu um erro: {e}",
                "chart_figure_dicts": [],
                "report_file_path": None,
                "is_explicit_generation": False,
            }
        )

    store_data["messages"] = messages
    store_data["thread_id"] = thread_id

    return (
        render_messages(messages),
        store_data,
        False,
        None,
        (scroll_trigger or 0) + 1,
        False,
        False,
    )


def _update_loading_step(n_intervals: int, is_loading: bool) -> tuple[dict, bool]:
    """
    Update loading step message from shared state.

    Called periodically by interval component while loading is active.

    Args:
        n_intervals: Number of interval ticks
        is_loading: Whether loading is currently active

    Returns:
        Tuple of (step_data dict, interval_disabled bool)

    """
    if not is_loading:
        return {"step": LOADING_DEFAULT_MESSAGE}, True
    return {"step": _current_loading_step.get("step", LOADING_DEFAULT_MESSAGE)}, False


def _display_loading_indicator(is_loading: bool, step_data: dict) -> list:
    """
    Create loading indicator component based on current state.

    Args:
        is_loading: Whether loading is active
        step_data: Dict with current step message

    Returns:
        List with loading indicator component or empty list

    """
    if not is_loading:
        return []
    step_message = (step_data or {}).get("step", LOADING_DEFAULT_MESSAGE)
    return [create_loading_indicator(step_message)]


def _update_loading_visibility(is_loading: bool) -> str:
    """
    Get CSS class for loading indicator visibility.

    Args:
        is_loading: Whether loading is active

    Returns:
        CSS class string for visible or hidden state

    """
    return LOADING_VISIBLE_CLASS if is_loading else LOADING_HIDDEN_CLASS


def _clear_conversation(
    n_clicks: int, store_data: dict | None, scroll_trigger: int
) -> tuple[dict, list, int, None, bool, bool, bool, bool]:
    """
    Clear conversation history and reset to initial state.

    Stops any pending requests and resets all chat state.

    Args:
        n_clicks: Clear button click count
        store_data: Current chat store data
        scroll_trigger: Current scroll trigger value

    Returns:
        Tuple of (new_store, rendered_messages, scroll_trigger, None, False, True, False, False)
        - None for pending_request (clears it)
        - False for loading (stops loading)
        - True for loading_interval disabled (stops interval)
        - False for send_button disabled (unlock button)
        - False for input disabled (unlock input)

    """
    if store_data is None:
        store_data = get_initial_store()

    ctx = callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]["prop_id"]
        if triggered_id == "chat-clear-button.n_clicks" and n_clicks and n_clicks > 0:
            new_store = get_initial_store()
            # Reset loading step message
            _current_loading_step["step"] = LOADING_DEFAULT_MESSAGE
            return (
                new_store,
                render_messages(new_store["messages"]),
                (scroll_trigger or 0) + 1,
                None,   # Clear pending request
                False,  # Stop loading
                True,   # Disable loading interval
                False,  # Unlock send button
                False,  # Unlock input
            )

    return (
        store_data,
        render_messages(store_data.get("messages", [])),
        scroll_trigger or 0,
        None,
        False,
        True,
        False,
        False,
    )
