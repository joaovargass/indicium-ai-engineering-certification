"""Main entry point for Dash application."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from charts.dash_app import main  # noqa: E402

if __name__ == "__main__":
    main()

