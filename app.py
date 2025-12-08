"""Main Dash application entry point."""

import sys
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import diskcache
from dash import DiskcacheManager, html

# Setup paths - must be before imports from src
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from common.config import (  # noqa: E402
    ASSETS_DIR,
    BACKGROUND_CALLBACKS_CACHE_DIR,
    DEFAULT_HOST,
    DEFAULT_PORT,
)
from ui.callbacks import register_chat_callbacks  # noqa: E402
from ui.elt_callbacks import register_elt_callbacks  # noqa: E402
from ui.layout import create_chat_layout  # noqa: E402


def create_app() -> dash.Dash:
    """
    Create main Dash application with AI chat interface.

    Returns:
        Configured Dash app instance

    """
    background_manager = _create_background_manager()

    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True,
        assets_folder=str(ASSETS_DIR) if ASSETS_DIR.exists() else None,
        background_callback_manager=background_manager,
    )

    app.layout = _create_layout()

    register_chat_callbacks(app)
    register_elt_callbacks(app)

    return app


def _create_background_manager() -> DiskcacheManager:
    """Create background callback manager."""
    BACKGROUND_CALLBACKS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = diskcache.Cache(str(BACKGROUND_CALLBACKS_CACHE_DIR))
    return DiskcacheManager(cache)


def _create_layout() -> dbc.Container:
    """Create main application layout."""
    return dbc.Container(
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


def main() -> None:
    """Run the Dash application."""
    app = create_app()
    app.run(debug=True, host=DEFAULT_HOST, port=DEFAULT_PORT)


if __name__ == "__main__":
    main()
