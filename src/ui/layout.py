"""Chat layout components for the SRAG data analysis platform."""

import dash_bootstrap_components as dbc
from dash import dcc, html

from common.config import ELT_STATUS_CHECK_INTERVAL_MS, LOADING_INTERVAL_MS
from ui.constants import WELCOME_MESSAGE
from ui.message import create_message_bubble


def create_chat_layout() -> html.Div:
    """Create the main chat interface layout."""
    return html.Div(
        [
            _create_header(),
            _create_chat_container(),
            *_create_stores(),
        ],
        className="p-4",
        id="chat-main-container",
    )


def _create_header() -> dbc.Row:
    """Create chat header with title and buttons."""
    return dbc.Row(
        [
            dbc.Col(_create_title_section(), width=8),
            dbc.Col(
                _create_button_section(),
                width=4,
                className="d-flex flex-column align-items-end",
            ),
        ],
        className="mb-3",
    )


def _create_title_section() -> list[html.H2 | html.P]:
    """Create title and subtitle elements."""
    return [
        html.H2("Agente Inteligente SRAG", className="mb-0"),
        html.P(
            "Faça perguntas sobre dados, métricas e tendências de SRAG",
            className="text-muted small mb-0",
        ),
        html.P(
            "Carregando…",
            id="last-extraction-date",
            className="text-muted small mb-0 last-extraction-date",
        ),
    ]


def _create_button_section() -> list[html.Div | dbc.Button]:
    """Create update and clear buttons."""
    return [
        html.Div(
            [
                dbc.Button(
                    "Atualizar Dados",
                    id="update-data-button",
                    color="primary",
                    size="sm",
                    className="w-100 mb-2",
                    n_clicks=0,
                ),
                dbc.Spinner(
                    html.Div(),
                    size="sm",
                    type="border",
                    color="light",
                    spinner_class_name="elt-spinner-hidden",
                    id="update-button-spinner",
                ),
            ],
            className="btn-relative-wrapper",
        ),
        dbc.Button(
            "Limpar Conversa",
            id="chat-clear-button",
            color="secondary",
            size="sm",
            outline=True,
            className="w-100",
            n_clicks=0,
        ),
    ]


def _create_chat_container() -> html.Div:
    """Create main chat container with messages and input."""
    return html.Div(
        id="chat-outer-container",
        className="chat-outer-container",
        children=[
            _create_messages_area(),
            _create_input_area(),
        ],
    )


def _create_messages_area() -> html.Div:
    """Create scrollable messages area with loading indicator."""
    return html.Div(
        id="chat-messages-container",
        className="chat-messages-wrapper",
        children=[
            html.Div(id="chat-feedback", children=[]),
            html.Div(
                id="chat-messages",
                className="chat-messages-scroll",
                children=[create_message_bubble("assistant", WELCOME_MESSAGE)],
            ),
            html.Div(
                id="chat-loading-indicator", className="loading-indicator-overlay"
            ),
        ],
    )


def _create_input_area() -> dbc.Row:
    """Create chat input area with send button."""
    return dbc.Row(
        [
            dbc.Col(
                dcc.Input(
                    id="chat-input",
                    type="text",
                    placeholder="Digite sua mensagem...",
                    className="chat-input-field",
                    n_submit=0,
                ),
                width=10,
            ),
            dbc.Col(
                dbc.Button(
                    "Enviar",
                    id="chat-send-button",
                    color="primary",
                    className="w-100",
                    n_clicks=0,
                ),
                width=2,
                className="d-flex align-items-center",
            ),
        ],
        className="mt-3 chat-input-row",
    )


def _create_stores() -> list[dcc.Store | dcc.Interval | dcc.Download]:
    """Create all dcc.Store, Interval, and Download components."""
    # Import here to avoid circular imports
    from ui.utils import get_initial_store

    initial_store = get_initial_store()

    return [
        dcc.Store(id="chat-store", data=initial_store),
        dcc.Store(id="chat-loading", data=False),
        dcc.Store(id="chat-pending-request", data=None),
        dcc.Store(id="chat-loading-step", data={"step": "Pensando..."}),
        dcc.Interval(
            id="chat-loading-interval",
            interval=LOADING_INTERVAL_MS,
            n_intervals=0,
            disabled=True,
        ),
        dcc.Download(id="chat-download"),
        dcc.Store(id="chat-scroll-trigger", data=0),
        dcc.Store(id="elt-pipeline-status", data={"running": False, "result": None}),
        dcc.Interval(
            id="elt-status-check-interval",
            interval=ELT_STATUS_CHECK_INTERVAL_MS,
            n_intervals=0,
            disabled=True,
        ),
        dcc.Interval(
            id="load-date-interval",
            interval=800,
            n_intervals=0,
            disabled=False,
        ),
    ]
