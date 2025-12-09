"""ELT pipeline callback handlers."""

import dash
from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from common.config import SPINNER_CLASS_HIDDEN, SPINNER_CLASS_VISIBLE
from elt.pipeline import run_incremental_elt
from ui.state import get_elt_running_status, set_elt_running_status
from ui.utils import format_extraction_date, load_extraction_date


def register_elt_callbacks(app: dash.Dash) -> None:
    """Register all ELT-related callbacks."""
    _register_load_date_callback(app)
    _register_start_pipeline_callback(app)
    _register_button_state_callback(app)
    _register_date_update_callback(app)


def _register_load_date_callback(app: dash.Dash) -> None:
    """Register callback to load extraction date on page load."""

    @app.callback(
        Output("last-extraction-date", "children"),
        Input("chat-main-container", "id"),
        prevent_initial_call=False,
    )
    def _on_page_load(_: str) -> str:
        return load_extraction_date()


def _register_start_pipeline_callback(app: dash.Dash) -> None:
    """Register background callback to start ELT pipeline."""

    @app.callback(
        Output("elt-pipeline-status", "data", allow_duplicate=True),
        Input("update-data-button", "n_clicks"),
        State("elt-pipeline-status", "data"),
        background=True,
        running=[
            (Output("update-data-button", "disabled"), True, False),
            (
                Output("update-data-button", "children"),
                "Atualizando...",
                "Atualizar Dados",
            ),
            (
                Output("update-button-spinner", "spinner_class_name"),
                SPINNER_CLASS_VISIBLE,
                SPINNER_CLASS_HIDDEN,
            ),
        ],
        prevent_initial_call=True,
    )
    def start_elt_pipeline(n_clicks: int | None, current_status: dict | None) -> dict:
        if not n_clicks:
            return current_status or {"running": False, "result": None}

        if get_elt_running_status():
            return {"running": True, "result": "Em andamento..."}

        set_elt_running_status(True)
        try:
            extraction_date = _run_elt()
            return {"running": False, "result": extraction_date}
        except Exception as e:
            return {"running": False, "result": f"Erro: {str(e)}"}
        finally:
            set_elt_running_status(False)


def _register_button_state_callback(app: dash.Dash) -> None:
    """Register callback to update button state based on server-side status."""

    @app.callback(
        [
            Output("update-data-button", "disabled"),
            Output("update-button-spinner", "spinner_class_name"),
            Output("update-data-button", "children"),
            Output("elt-status-check-interval", "disabled"),
        ],
        [
            Input("elt-pipeline-status", "data"),
            Input("elt-status-check-interval", "n_intervals"),
            Input("chat-main-container", "id"),
        ],
        prevent_initial_call=False,
    )
    def update_button_state(
        status_data: dict | None, _intervals: int, _container_id: str
    ) -> tuple[bool, str, str, bool]:
        server_running = get_elt_running_status()

        if server_running:
            return True, SPINNER_CLASS_VISIBLE, "Atualizando...", False

        return False, SPINNER_CLASS_HIDDEN, "Atualizar Dados", True


def _register_date_update_callback(app: dash.Dash) -> None:
    """Register callback to update extraction date display."""

    @app.callback(
        Output("last-extraction-date", "children", allow_duplicate=True),
        Input("elt-pipeline-status", "data"),
        prevent_initial_call=True,
    )
    def update_extraction_date(status_data: dict | None) -> str:
        if not status_data:
            raise PreventUpdate

        result = status_data.get("result")
        if result and not result.startswith("Erro"):
            return format_extraction_date(result)
        raise PreventUpdate


def _run_elt() -> str:
    """Run ELT pipeline."""
    try:
        return run_incremental_elt()
    except Exception as e:
        return f"Erro: {str(e)}"
