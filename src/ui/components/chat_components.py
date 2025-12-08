"""Chat UI components for Dash application."""

import ast
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html
from langchain_core.messages import AIMessage, ToolMessage
from plotly.graph_objects import Figure

from elt.load import load_srag_data
from tools.location_utils import determine_location_filter

# Constants
WELCOME_MESSAGE = (
    "Olá! Sou seu assistente de dados SRAG. Posso ajudá-lo com:\n"
    "- Consultar métricas (taxas de mortalidade, ocupação de UTI, taxas de vacinação)\n"
    "- Gerar gráficos e visualizações\n"
    "- Criar relatórios completos\n"
    "- Buscar notícias relevantes sobre saúde\n\n"
    "Como posso ajudar?"
)

_CHART_TOOL_NAMES = frozenset({"get_daily_chart_json", "get_monthly_chart_json"})


def _render_markdown_content(content: str) -> list:
    """
    Render markdown content using dcc.Markdown with proper styling.

    Args:
        content: Markdown content string

    Returns:
        List of Dash components

    """
    return [
        dcc.Markdown(
            content,
            className="mb-2 markdown-content",
            style={"fontSize": "15px", "lineHeight": "1.6", "color": "#212529"},
            dangerously_allow_html=True,
        )
    ]


def create_download_button(file_path: str, button_id: str | None = None) -> html.Div:
    """
    Create a styled download button for report files.

    Uses minimal text to support multilingual interface.

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
                        className="small mb-2",
                        style={
                            "marginBottom": "10px",
                            "color": "#155724",
                            "fontFamily": "monospace",
                            "wordBreak": "break-all",
                            "fontSize": "13px",
                        },
                    ),
                    dbc.Button(
                        "Baixar",
                        id=button_id or "download-report-btn",
                        color="success",
                        size="md",
                        className="w-100",
                        style={
                            "fontWeight": "600",
                            "padding": "12px 24px",
                            "borderRadius": "8px",
                            "fontSize": "16px",
                        },
                    ),
                ],
                style={
                    "padding": "20px",
                    "backgroundColor": "#d4edda",
                    "borderRadius": "12px",
                    "border": "2px solid #28a745",
                    "marginTop": "15px",
                    "textAlign": "center",
                },
            ),
        ],
    )


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
        content: Message text content (markdown supported for assistant)
        chart_figures: Optional list of Plotly Figure objects to render as charts
        report_file_path: Optional path to downloadable report file

    Returns:
        dbc.Card component styled as message bubble

    """
    is_user = role == "user"

    if is_user:
        bg_color = "primary"
        margin_class = "ms-auto"
        padding_side = "paddingRight"
    else:
        bg_color = "light"
        margin_class = "me-auto"
        padding_side = "paddingLeft"

    # Build message content - markdown for assistant, plain text for user
    if not is_user:
        message_children = _render_markdown_content(content)
    else:
        message_children = [
            html.Div(
                content,
                className="mb-2",
                style={"whiteSpace": "pre-wrap", "wordWrap": "break-word", "fontSize": "15px"},
            )
        ]

    # Add charts if present
    if chart_figures:
        for fig in chart_figures:
            message_children.append(
                dcc.Graph(
                    figure=fig,
                    config={"displayModeBar": True, "responsive": True},
                    style={"height": "400px", "width": "100%", "marginTop": "1rem"},
                )
            )

    # Add download button if report file path is provided
    if report_file_path and Path(report_file_path).exists():
        message_children.append(create_download_button(report_file_path))

    card_style = {
        "maxWidth": "min(800px, 90vw)",
        "width": "100%" if (chart_figures or report_file_path) else "fit-content",
        padding_side: "20px",
    }

    message_class = "user-message" if is_user else "assistant-message"

    return dbc.Card(
        dbc.CardBody(message_children, style={"padding": "15px", "margin": "0"}),
        className=f"mb-3 {margin_class} {message_class} chat-message-bubble",
        style={**card_style, "height": "fit-content", "overflow": "hidden"},
        color=bg_color if is_user else None,
        inverse=is_user,
    )


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
            html.Span(
                step_message,
                className="gradient-text",
            ),
            style={
                "backgroundColor": "#f8f9fa",
                "borderRadius": "12px",
                "padding": "8px 16px",
                "display": "inline-block",
                "boxShadow": "0 1px 3px rgba(0, 0, 0, 0.1)",
            },
        ),
        style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "padding": "0",
            "minHeight": "0",
            "height": "auto",
        },
    )


def create_chat_layout() -> html.Div:
    """Create the main chat interface layout."""
    initial_store = {
        "messages": [{
            "role": "assistant",
            "content": WELCOME_MESSAGE,
            "chart_figure_dicts": [],
            "report_file_path": None,
            "is_explicit_generation": False,
        }],
        "thread_id": None,
    }

    return html.Div([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("Agente Inteligente SRAG", className="mb-0"),
                html.P("Faça perguntas sobre dados, métricas e tendências de SRAG",
                       className="text-muted small mb-0"),
            ], width=10),
            dbc.Col([
                dbc.Button("Limpar Conversa", id="chat-clear-button",
                          color="secondary", size="sm", outline=True,
                          className="w-100", n_clicks=0),
            ], width=2, className="d-flex align-items-end"),
        ], className="mb-3"),
        # Chat container with flexbox layout
        html.Div(
            id="chat-outer-container",
            children=[
            # Message area (flexible, scrollable)
            html.Div(
                id="chat-messages-container",
                style={
                    "flex": "1",
                    "display": "flex",
                    "flexDirection": "column",
                    "overflow": "hidden",
                    "position": "relative",
                },
                children=[
                    html.Div(
                        id="chat-messages",
                        style={
                            "flex": "1",
                            "overflowY": "auto",
                            "padding": "1rem",
                        },
                        children=[create_message_bubble("assistant", WELCOME_MESSAGE)],
                    ),
                    # Loading indicator (absolute positioned, overlays entire container)
                    html.Div(
                        id="chat-loading-indicator",
                        style={
                            "display": "none",
                            "position": "absolute",
                            "top": "0",
                            "bottom": "0",
                            "left": "0",
                            "right": "0",
                            "padding": "1rem",
                            "zIndex": "1000",
                            "alignItems": "flex-end",
                            "justifyContent": "center",
                        },
                    ),
                ],
            ),
            # Input area (fixed at bottom)
            dbc.Row([
                dbc.Col([
                    dcc.Input(id="chat-input", type="text", placeholder="Digite sua mensagem...",
                             style={"width": "100%", "padding": "0.75rem",
                                    "borderRadius": "0.5rem", "border": "1px solid #dee2e6"},
                             n_submit=0),
                ], width=10),
                dbc.Col([
                    dbc.Button("Enviar", id="chat-send-button", color="primary",
                              className="w-100", n_clicks=0),
                ], width=2, className="d-flex align-items-center"),
            ], className="mt-3", style={"flexShrink": "0", "alignItems": "center"}),
            ],
            style={
                "display": "flex",
                "flexDirection": "column",
                "height": "calc(100vh - 250px)",
                "minHeight": "400px",
            },
        ),
        # State stores
        dcc.Store(id="chat-store", data=initial_store),
        dcc.Store(id="chat-loading", data=False),
        dcc.Store(id="chat-pending-request", data=None),
        dcc.Store(id="chat-loading-step", data={"step": "Pensando..."}),
        dcc.Store(id="chat-download-file", data=None),
        dcc.Interval(id="chat-loading-interval", interval=500, n_intervals=0, disabled=True),
        # Download component for file downloads
        dcc.Download(id="chat-download"),
        # Store to trigger scroll to bottom
        dcc.Store(id="chat-scroll-trigger", data=0),
    ], className="p-4", id="chat-main-container")


def parse_agent_response(result: dict[str, Any]) -> tuple[str, list[Figure], str | None, bool]:
    """
    Parse agent response to extract text, charts, report path, and generation flag.

    Returns:
        Tuple of (text_content, chart_figures, report_file_path, is_explicit_generation)

    """
    messages = result.get("messages", [])
    if not messages:
        return "No response from agent.", [], None, False

    # Get last AI message
    ai_messages = [m for m in messages if isinstance(m, AIMessage)]
    if not ai_messages:
        return "Agent response format error.", [], None, False

    text_content = getattr(ai_messages[-1], "content", "")

    # Track tool calls
    tools_called = _extract_tool_names(ai_messages)
    is_explicit_generation = "generate_download_report" in tools_called

    # Extract charts, metadata, and report path from tool messages
    chart_figures, chart_metadata_list, report_file_path, report_content = _extract_tool_outputs(messages, ai_messages)

    # Use report content if available
    if report_content:
        if is_explicit_generation:
            # For download reports, use the summary
            text_content = report_content
        else:
            # For chat reports, use the report text
            text_content = report_content
    
    # Enhance text with chart date ranges and explanations if charts are present
    if chart_metadata_list and not is_explicit_generation:
        chart_info = _format_chart_info_for_agent(chart_metadata_list)
        if chart_info:
            # Prepend chart information before the existing text
            text_content = chart_info + "\n\n" + text_content

    return text_content, chart_figures, report_file_path, is_explicit_generation


def _format_chart_info_for_agent(chart_metadata_list: list[dict]) -> str:
    """
    Format chart metadata into a structured format for the agent to include in response.
    
    Returns a formatted string with date ranges and statistics that the agent can use
    to generate multilingual explanations.
    """
    if not chart_metadata_list:
        return ""
    
    info_parts = []
    
    for metadata in chart_metadata_list:
        start_date = metadata.get("start_date")
        end_date = metadata.get("end_date")
        chart_type = metadata.get("chart_type", "chart")
        location = metadata.get("location", "Brasil (nacional)")
        
        if not start_date or not end_date:
            continue
        
        # Convert to datetime if needed
        if isinstance(start_date, pd.Timestamp):
            start_date = start_date.to_pydatetime()
        elif not isinstance(start_date, datetime):
            try:
                start_date = pd.to_datetime(start_date).to_pydatetime()
            except (ValueError, TypeError):
                continue
        
        if isinstance(end_date, pd.Timestamp):
            end_date = end_date.to_pydatetime()
        elif not isinstance(end_date, datetime):
            try:
                end_date = pd.to_datetime(end_date).to_pydatetime()
            except (ValueError, TypeError):
                continue
        
        # Extract date components
        start_year = start_date.year
        start_month = start_date.month
        start_day = start_date.day
        end_year = end_date.year
        end_month = end_date.month
        end_day = end_date.day
        
        # Build structured info for agent
        chart_info = f"[CHART_DATA]\n"
        chart_info += f"Chart Type: {chart_type}\n"
        chart_info += f"Location: {location}\n"
        chart_info += f"Start Date: year={start_year}, month={start_month}, day={start_day}\n"
        chart_info += f"End Date: year={end_year}, month={end_month}, day={end_day}\n"
        
        # Add statistics
        if chart_type == "daily":
            total = metadata.get("total_cases", 0)
            avg = metadata.get("avg_daily", 0)
            max_val = metadata.get("max_daily", 0)
            max_dt = metadata.get("max_date")
            trend = metadata.get("trend_direction", "stable")
            trend_pct = metadata.get("trend_percentage", 0)
            
            chart_info += f"Total Cases: {total}\n"
            chart_info += f"Average Daily Cases: {avg:.1f}\n"
            chart_info += f"Peak Daily Cases: {max_val}"
            if max_dt:
                if isinstance(max_dt, pd.Timestamp):
                    max_dt = max_dt.to_pydatetime()
                elif not isinstance(max_dt, datetime):
                    try:
                        max_dt = pd.to_datetime(max_dt).to_pydatetime()
                    except (ValueError, TypeError):
                        max_dt = None
                if max_dt:
                    chart_info += f" (on {max_dt.year}-{max_dt.month}-{max_dt.day})"
            chart_info += f"\nTrend: {trend} ({trend_pct:.1f}% change)\n"
        else:  # monthly
            total = metadata.get("total_cases", 0)
            avg = metadata.get("avg_monthly", 0)
            max_val = metadata.get("max_monthly", 0)
            max_dt = metadata.get("max_date")
            trend = metadata.get("trend_direction", "stable")
            trend_pct = metadata.get("trend_percentage", 0)
            
            chart_info += f"Total Cases: {total}\n"
            chart_info += f"Average Monthly Cases: {avg:.1f}\n"
            chart_info += f"Peak Monthly Cases: {max_val}"
            if max_dt:
                if isinstance(max_dt, pd.Timestamp):
                    max_dt = max_dt.to_pydatetime()
                elif not isinstance(max_dt, datetime):
                    try:
                        max_dt = pd.to_datetime(max_dt).to_pydatetime()
                    except (ValueError, TypeError):
                        max_dt = None
                if max_dt:
                    chart_info += f" (in {max_dt.year}-{max_dt.month})"
            chart_info += f"\nTrend: {trend} ({trend_pct:.1f}% change)\n"
        
        chart_info += f"[/CHART_DATA]\n"
        info_parts.append(chart_info)
    
    if info_parts:
        return "\n".join(info_parts)
    return ""


def _extract_tool_names(ai_messages: list) -> set[str]:
    """Extract tool names from AI messages."""
    tools = set()
    for msg in ai_messages:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                if tool_name:
                    tools.add(tool_name)
    return tools


def _extract_report_info_from_parsed(parsed: dict) -> tuple[str | None, str | None]:
    """Extract report file path and content from parsed tool output."""
    file_path = None
    content = None
    # generate_download_report output
    if "file_path" in parsed:
        file_path = parsed.get("file_path")
        content = parsed.get("report_summary") or parsed.get("report_content")
    # generate_chat_report output
    elif "report_text" in parsed:
        content = parsed.get("report_text")
    return file_path, content


def _process_tool_message(msg: ToolMessage) -> tuple[str | None, str | None]:
    """Process a single tool message and extract report info."""
    if not hasattr(msg, "content"):
        return None, None

    parsed = _parse_tool_content(msg.content)
    if not parsed:
        return None, None

    file_path, content = _extract_report_info_from_parsed(parsed)
    return file_path, content


def _extract_tool_outputs(messages: list, ai_messages: list) -> tuple[list[Figure], list[dict], str | None, str | None]:
    """Extract chart figures, chart metadata, and report info from tool messages."""
    chart_figures = []
    chart_metadata_list = []
    report_file_path = None
    report_content = None

    # Build map: tool_call_id -> (tool_name, tool_args) from AI messages
    tool_call_map = {}
    for msg in messages:
        if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                if isinstance(tc, dict):
                    tc_id, tc_name, tc_args = tc.get("id"), tc.get("name"), tc.get("args", {})
                else:
                    tc_id = getattr(tc, "id", None)
                    tc_name = getattr(tc, "name", None)
                    tc_args = getattr(tc, "args", {})

                if tc_id and tc_name:
                    tool_call_map[tc_id] = (tc_name, tc_args)

    # Process ToolMessages for charts and reports
    for msg in messages:
        if isinstance(msg, ToolMessage):
            tool_call_id = getattr(msg, "tool_call_id", None)
            if tool_call_id and tool_call_id in tool_call_map:
                tool_name, tool_args = tool_call_map[tool_call_id]
                if tool_name in _CHART_TOOL_NAMES:
                    fig, metadata = _generate_chart_from_tool_call(tool_name, tool_args)
                    if fig:
                        chart_figures.append(fig)
                        if metadata:
                            chart_metadata_list.append(metadata)

            file_path, content = _process_tool_message(msg)
            if file_path:
                report_file_path = file_path
            if content:
                report_content = content

    return chart_figures, chart_metadata_list, report_file_path, report_content


def _generate_chart_from_tool_call(tool_name: str, tool_args: dict) -> tuple[Figure | None, dict | None]:
    """Generate a chart Figure from a tool call and extract metadata."""
    try:
        df = load_srag_data()
        location_col, location_value = determine_location_filter(
            tool_args.get("uf"), tool_args.get("city_code")
        )
        title = tool_args.get("title")
        x_axis_label = tool_args.get("x_axis_label")
        y_axis_label = tool_args.get("y_axis_label")

        if tool_name == "get_daily_chart_json":
            fig, metadata = _generate_daily_chart_with_metadata(
                df, location_col, location_value, tool_args.get("days", 30),
                title, x_axis_label, y_axis_label
            )
            return fig, metadata
        elif tool_name == "get_monthly_chart_json":
            fig, metadata = _generate_monthly_chart_with_metadata(
                df, location_col, location_value, tool_args.get("months", 12),
                title, x_axis_label, y_axis_label
            )
            return fig, metadata
    except Exception:
        pass
    return None, None


def _generate_daily_chart_with_metadata(
    df: pd.DataFrame,
    location_col: str | None,
    location_value: str | None,
    days: int,
    title: str | None,
    x_axis_label: str | None,
    y_axis_label: str | None,
) -> tuple[Figure, dict]:
    """Generate daily chart and extract date range and statistics."""
    from datetime import timedelta
    from charts.charts import _create_line_chart, _build_title, _create_empty_chart
    
    date_col = "DT_SIN_PRI"
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    
    if location_col and location_value:
        df = df.dropna(subset=[date_col, location_col])
        df = df[df[location_col] == location_value]
    else:
        df = df.dropna(subset=[date_col])
    
    end_date = df[date_col].max()
    if pd.isna(end_date):
        default_title = title or f"Casos Diários - Últimos {days} Dias"
        return _create_empty_chart(default_title, location_value), None
    
    start_date = end_date - timedelta(days=days)
    df_filtered = df[(df[date_col] >= start_date) & (df[date_col] <= end_date)].copy()
    
    daily_counts = df_filtered.groupby(date_col).size().reset_index(name="casos")
    daily_counts = daily_counts.sort_values(date_col)
    
    # Extract actual date range from data
    actual_start = daily_counts[date_col].min()
    actual_end = daily_counts[date_col].max()
    
    # Calculate statistics
    total_cases = daily_counts["casos"].sum()
    avg_daily = daily_counts["casos"].mean()
    max_daily = daily_counts["casos"].max()
    max_date = daily_counts.loc[daily_counts["casos"].idxmax(), date_col] if len(daily_counts) > 0 else None
    min_daily = daily_counts["casos"].min()
    
    # Calculate trend (comparing first half vs second half)
    mid_point = len(daily_counts) // 2
    first_half_avg = daily_counts.iloc[:mid_point]["casos"].mean() if mid_point > 0 else avg_daily
    second_half_avg = daily_counts.iloc[mid_point:]["casos"].mean() if mid_point < len(daily_counts) else avg_daily
    trend_direction = "increasing" if second_half_avg > first_half_avg else "decreasing" if second_half_avg < first_half_avg else "stable"
    trend_percentage = abs((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
    
    # Create chart
    chart_title = title or f"Casos Diários - Últimos {days} Dias"
    chart_title = _build_title(chart_title, location_value)
    fig = _create_line_chart(daily_counts, date_col, "casos", chart_title, x_axis_label, y_axis_label)
    
    metadata = {
        "chart_type": "daily",
        "start_date": actual_start,
        "end_date": actual_end,
        "total_cases": int(total_cases),
        "avg_daily": float(avg_daily),
        "max_daily": int(max_daily),
        "max_date": max_date,
        "min_daily": int(min_daily),
        "trend_direction": trend_direction,
        "trend_percentage": float(trend_percentage),
        "location": location_value or "Brasil (nacional)",
    }
    
    return fig, metadata


def _generate_monthly_chart_with_metadata(
    df: pd.DataFrame,
    location_col: str | None,
    location_value: str | None,
    months: int,
    title: str | None,
    x_axis_label: str | None,
    y_axis_label: str | None,
) -> tuple[Figure, dict]:
    """Generate monthly chart and extract date range and statistics."""
    from charts.charts import _create_bar_chart, _build_title, _create_empty_chart
    
    date_col = "DT_SIN_PRI"
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    
    if location_col and location_value:
        df = df.dropna(subset=[date_col, location_col])
        df = df[df[location_col] == location_value]
    else:
        df = df.dropna(subset=[date_col])
    
    end_date = df[date_col].max()
    if pd.isna(end_date):
        default_title = title or f"Casos Mensais - Últimos {months} Meses"
        return _create_empty_chart(default_title, location_value), None
    
    # Find the minimum date available in the dataset
    data_min_date = df[date_col].min()
    
    # Calculate desired period: last N months from the maximum available date
    desired_start_date = end_date - pd.DateOffset(months=months)
    
    # Adjust start_date if dataset doesn't have enough months
    # Use the maximum of desired_start and actual min_date to ensure we use all available data
    start_date = max(desired_start_date, data_min_date)
    
    df_filtered = df[(df[date_col] >= start_date) & (df[date_col] <= end_date)].copy()
    
    df_filtered["ano_mes"] = df_filtered[date_col].dt.to_period("M")
    monthly_counts = df_filtered.groupby("ano_mes").size().reset_index(name="casos")
    monthly_counts["ano_mes"] = monthly_counts["ano_mes"].dt.to_timestamp()
    monthly_counts = monthly_counts.sort_values("ano_mes")
    
    # Extract actual date range from data
    actual_start = monthly_counts["ano_mes"].min()
    actual_end = monthly_counts["ano_mes"].max()
    
    # Calculate actual number of months available
    actual_months = len(monthly_counts)
    period_limited_by_data = actual_months < months or start_date > desired_start_date
    
    # Calculate statistics
    total_cases = monthly_counts["casos"].sum()
    avg_monthly = monthly_counts["casos"].mean()
    max_monthly = monthly_counts["casos"].max()
    max_date = monthly_counts.loc[monthly_counts["casos"].idxmax(), "ano_mes"] if len(monthly_counts) > 0 else None
    min_monthly = monthly_counts["casos"].min()
    
    # Calculate trend
    if len(monthly_counts) >= 2:
        first_half_avg = monthly_counts.iloc[:len(monthly_counts)//2]["casos"].mean()
        second_half_avg = monthly_counts.iloc[len(monthly_counts)//2:]["casos"].mean()
        trend_direction = "increasing" if second_half_avg > first_half_avg else "decreasing" if second_half_avg < first_half_avg else "stable"
        trend_percentage = abs((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
    else:
        trend_direction = "stable"
        trend_percentage = 0.0
    
    # Create chart
    chart_title = title or f"Casos Mensais - Últimos {months} Meses"
    chart_title = _build_title(chart_title, location_value)
    fig = _create_bar_chart(monthly_counts, "ano_mes", "casos", chart_title, x_axis_label, y_axis_label)
    
    metadata = {
        "chart_type": "monthly",
        "start_date": actual_start,
        "end_date": actual_end,
        "total_cases": int(total_cases),
        "avg_monthly": float(avg_monthly),
        "max_monthly": int(max_monthly),
        "max_date": max_date,
        "min_monthly": int(min_monthly),
        "trend_direction": trend_direction,
        "trend_percentage": float(trend_percentage),
        "location": location_value or "Brasil (nacional)",
    }
    
    # Add information about period limitation
    if period_limited_by_data:
        metadata["period_limited_by_data"] = True
        metadata["requested_months"] = months
        metadata["actual_months"] = actual_months
        metadata["data_max_date"] = end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date)
        metadata["data_min_date"] = data_min_date.isoformat() if hasattr(data_min_date, 'isoformat') else str(data_min_date)
    
    return fig, metadata


def _parse_tool_content(content: str | dict) -> dict | None:
    """Parse tool message content to dict."""
    if isinstance(content, dict):
        return content

    if not isinstance(content, str):
        return None

    content_stripped = content.strip()

    # Try JSON parsing first
    try:
        parsed = json.loads(content_stripped)
        return parsed if isinstance(parsed, dict) else None
    except (json.JSONDecodeError, TypeError):
        pass

    # Fallback to Python literal eval
    try:
        result = ast.literal_eval(content_stripped)
        return result if isinstance(result, dict) else None
    except (ValueError, SyntaxError):
        return None
