"""Dash application for interactive SRAG charts."""

from datetime import date, timedelta

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, dcc, html
from plotly.graph_objects import Figure

from charts.charts import (
    plot_daily_range,
    plot_monthly_cases,
    plot_monthly_range,
)
from elt.load import load_srag_data

DATE_COL = "DT_SIN_PRI"


def _create_error_figure(message: str, title: str) -> Figure:
    """
    Create an error figure with a message.

    Args:
        message: Error message to display
        title: Figure title

    Returns:
        Plotly figure with error message.

    """
    fig = Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=16),
    )
    fig.update_layout(
        title=title,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


def _create_layout(
    available_ufs: list[str],
    start_date_default: date,
    end_date_default: date,
    available_years: list[int],
    available_months: list[int],
) -> dbc.Container:
    """
    Create Dash application layout.

    Args:
        available_ufs: List of available state codes
        start_date_default: Default start date
        end_date_default: Default end date
        available_years: List of available years
        available_months: List of available months (1-12)

    Returns:
        Dash Bootstrap Components Container with layout.

    """
    month_options = [
        {"label": "January", "value": 1},
        {"label": "February", "value": 2},
        {"label": "March", "value": 3},
        {"label": "April", "value": 4},
        {"label": "May", "value": 5},
        {"label": "June", "value": 6},
        {"label": "July", "value": 7},
        {"label": "August", "value": 8},
        {"label": "September", "value": 9},
        {"label": "October", "value": 10},
        {"label": "November", "value": 11},
        {"label": "December", "value": 12},
    ]

    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.H1(
                        "SRAG - Interactive Dashboard", className="text-center mb-4"
                    ),
                )
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4("Daily Cases Chart", className="mb-3"),
                            html.Label("Filter by State:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id="daily-uf-filter",
                                options=[{"label": "All", "value": "all"}]
                                + [{"label": uf, "value": uf} for uf in available_ufs],
                                value="all",
                                clearable=False,
                            ),
                            html.Label("Start Date:", className="fw-bold mb-2 mt-3"),
                            dcc.DatePickerSingle(
                                id="daily-start-date",
                                date=start_date_default,
                                display_format="DD/MM/YYYY",
                            ),
                            html.Label("End Date:", className="fw-bold mb-2 mt-3"),
                            dcc.DatePickerSingle(
                                id="daily-end-date",
                                date=end_date_default,
                                display_format="DD/MM/YYYY",
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            dcc.Graph(id="daily-chart"),
                        ],
                        md=9,
                        className="mb-4",
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4("Monthly Cases Chart", className="mb-3"),
                            html.Label("Filter by State:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id="monthly-uf-filter",
                                options=[{"label": "All", "value": "all"}]
                                + [{"label": uf, "value": uf} for uf in available_ufs],
                                value="all",
                                clearable=False,
                            ),
                            html.Label("Start Year:", className="fw-bold mb-2 mt-3"),
                            dcc.Dropdown(
                                id="monthly-start-year",
                                options=[{"label": "Last 12 Months", "value": "all"}]
                                + [
                                    {"label": str(year), "value": year}
                                    for year in available_years
                                ],
                                value="all",
                                clearable=False,
                            ),
                            html.Label("Start Month:", className="fw-bold mb-2 mt-3"),
                            dcc.Dropdown(
                                id="monthly-start-month",
                                options=[{"label": "All", "value": "all"}]
                                + month_options,
                                value="all",
                                clearable=False,
                            ),
                            html.Label("End Year:", className="fw-bold mb-2 mt-3"),
                            dcc.Dropdown(
                                id="monthly-end-year",
                                options=[{"label": "All", "value": "all"}]
                                + [
                                    {"label": str(year), "value": year}
                                    for year in available_years
                                ],
                                value="all",
                                clearable=False,
                            ),
                            html.Label("End Month:", className="fw-bold mb-2 mt-3"),
                            dcc.Dropdown(
                                id="monthly-end-month",
                                options=[{"label": "All", "value": "all"}]
                                + month_options,
                                value="all",
                                clearable=False,
                            ),
                        ],
                        md=3,
                    ),
                    dbc.Col(
                        [
                            dcc.Graph(id="monthly-chart"),
                        ],
                        md=9,
                    ),
                ],
            ),
        ],
        fluid=True,
        className="py-4",
    )


def _validate_daily_dates(start_date_str: str, end_date_str: str) -> str:
    """Ensure start date is before end date."""
    if not start_date_str or not end_date_str:
        return end_date_str

    start_date = pd.to_datetime(start_date_str)
    end_date = pd.to_datetime(end_date_str)

    if start_date >= end_date:
        # Adjust end date to be one day after start date
        return (start_date + pd.Timedelta(days=1)).date()

    return end_date_str


def _update_daily_chart(
    app: dash.Dash, uf_value: str, start_date_str: str, end_date_str: str
) -> Figure:
    """Update daily chart based on filters."""
    df_filtered = app.df.copy()

    if uf_value != "all":
        df_filtered = df_filtered[df_filtered["SG_UF_NOT"] == uf_value].copy()

    start_date = pd.to_datetime(start_date_str)
    end_date = pd.to_datetime(end_date_str)

    # Validate: start_date must be < end_date
    if start_date >= end_date:
        return _create_error_figure(
            "Start date must be before end date",
            "Error: Invalid Date Range",
        )

    # Check if there is data in the selected period
    date_filtered = df_filtered[
        (df_filtered[DATE_COL] >= start_date) & (df_filtered[DATE_COL] <= end_date)
    ]
    if len(date_filtered) == 0:
        return _create_error_figure(
            "No data available for the selected period",
            "No Data Available",
        )

    location_col = "SG_UF_NOT" if uf_value != "all" else None
    location_value = uf_value if uf_value != "all" else None

    return plot_daily_range(
        df_filtered,
        start_date=start_date,
        end_date=end_date,
        location_col=location_col,
        location_value=location_value,
    )


def _validate_monthly_period(
    start_year: str | int,
    start_month: str | int,
    end_year: str | int,
    end_month: str | int,
) -> tuple[str | int, str | int]:
    """Ensure start period is before end period."""
    if start_year == "all" or start_month == "all":
        return end_year, end_month

    if end_year == "all" or end_month == "all":
        return end_year, end_month

    start_date = pd.Timestamp(year=int(start_year), month=int(start_month), day=1)
    if int(end_month) == 12:
        end_date = pd.Timestamp(year=int(end_year) + 1, month=1, day=1) - pd.Timedelta(
            days=1
        )
    else:
        end_date = pd.Timestamp(
            year=int(end_year), month=int(end_month) + 1, day=1
        ) - pd.Timedelta(days=1)

    if start_date >= end_date:
        # Adjust end to be one month after start
        if int(start_month) == 12:
            adjusted_year = int(start_year) + 1
            adjusted_month = 1
        else:
            adjusted_year = int(start_year)
            adjusted_month = int(start_month) + 1
        return adjusted_year, adjusted_month

    return end_year, end_month


def _update_monthly_chart(
    app: dash.Dash,
    uf_value: str,
    start_year: str | int,
    start_month: str | int,
    end_year: str | int,
    end_month: str | int,
) -> Figure:
    """Update monthly chart based on filters."""
    df_filtered = app.df.copy()

    if uf_value != "all":
        df_filtered = df_filtered[df_filtered["SG_UF_NOT"] == uf_value].copy()

    location_col = "SG_UF_NOT" if uf_value != "all" else None
    location_value = uf_value if uf_value != "all" else None

    # If start year is "all", show last 12 months
    if start_year == "all":
        if len(df_filtered) == 0:
            return _create_error_figure("No data available", "No Data Available")
        return plot_monthly_cases(
            df_filtered,
            location_col=location_col,
            location_value=location_value,
            months=12,
        )

    # Calculate start date (first day of start month/year)
    start_date = pd.Timestamp(year=int(start_year), month=int(start_month), day=1)

    # Calculate end date (last day of end month/year)
    if end_year == "all" or end_month == "all":
        # If end is "all", use max date from data
        end_date = df_filtered[DATE_COL].max()
    else:
        # Last day of the end month
        if int(end_month) == 12:
            end_date = pd.Timestamp(
                year=int(end_year) + 1, month=1, day=1
            ) - pd.Timedelta(days=1)
        else:
            end_date = pd.Timestamp(
                year=int(end_year), month=int(end_month) + 1, day=1
            ) - pd.Timedelta(days=1)

    # Validate: start_date must be < end_date
    if start_date >= end_date:
        return _create_error_figure(
            "Start period must be before end period",
            "Error: Invalid Period Range",
        )

    # Check if there is data in the selected period
    date_filtered = df_filtered[
        (df_filtered[DATE_COL] >= start_date) & (df_filtered[DATE_COL] <= end_date)
    ]
    if len(date_filtered) == 0:
        return _create_error_figure(
            "No data available for the selected period",
            "No Data Available",
        )

    return plot_monthly_range(
        df_filtered,
        start_date=start_date,
        end_date=end_date,
        location_col=location_col,
        location_value=location_value,
    )


def _register_callbacks(app: dash.Dash) -> None:
    """
    Register Dash callbacks for chart updates.

    Args:
        app: Dash application instance.

    """
    app.callback(
        Output("daily-end-date", "date"),
        Input("daily-start-date", "date"),
        Input("daily-end-date", "date"),
    )(_validate_daily_dates)

    app.callback(
        Output("daily-chart", "figure"),
        [
            Input("daily-uf-filter", "value"),
            Input("daily-start-date", "date"),
            Input("daily-end-date", "date"),
        ],
    )(lambda uf, start, end: _update_daily_chart(app, uf, start, end))

    app.callback(
        [
            Output("monthly-end-year", "value"),
            Output("monthly-end-month", "value"),
        ],
        [
            Input("monthly-start-year", "value"),
            Input("monthly-start-month", "value"),
            Input("monthly-end-year", "value"),
            Input("monthly-end-month", "value"),
        ],
    )(_validate_monthly_period)

    app.callback(
        Output("monthly-chart", "figure"),
        [
            Input("monthly-uf-filter", "value"),
            Input("monthly-start-year", "value"),
            Input("monthly-start-month", "value"),
            Input("monthly-end-year", "value"),
            Input("monthly-end-month", "value"),
        ],
    )(lambda uf, sy, sm, ey, em: _update_monthly_chart(app, uf, sy, sm, ey, em))


def create_app() -> dash.Dash:
    """Create and configure Dash application."""
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    try:
        df = load_srag_data()
        df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
    except Exception as e:
        raise RuntimeError(f"Failed to load data: {e}") from e

    available_ufs = sorted(df["SG_UF_NOT"].dropna().unique().tolist())

    end_date_default = date.today()
    start_date_default = end_date_default - timedelta(days=30)

    available_years = sorted(df[DATE_COL].dropna().dt.year.unique().tolist())
    available_months = list(range(1, 13))

    app.layout = _create_layout(
        available_ufs,
        start_date_default,
        end_date_default,
        available_years,
        available_months,
    )
    app.df = df

    _register_callbacks(app)

    return app


def main() -> None:
    """Run the Dash application."""
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=8050)


if __name__ == "__main__":
    main()
