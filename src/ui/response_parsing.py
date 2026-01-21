"""
Agent response parsing for UI display.

This module handles the conversion of LangGraph agent responses into
displayable UI components, extracting:
- Text content from AI messages
- Chart figures from tool outputs
- Report file paths from download tool results
- Metadata about whether this was an explicit report generation

Response format expected:
- result["messages"]: List of LangChain message objects
- AIMessage: Contains text and tool_calls
- ToolMessage: Contains tool execution results (JSON strings)

"""

import json
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage
from plotly.graph_objects import Figure

from common.logging import logger
from ui.chart_render import render_tool_chart
from ui.constants import CHART_TOOL_NAMES
from ui.tool_parsing import extract_report_info, parse_tool_content


def parse_agent_response(
    result: dict[str, Any],
) -> tuple[str, list[Figure], str | None, bool]:
    """
    Parse agent response to extract text, charts, report path, and generation flag.

    Args:
        result: Agent result dict containing "messages" list

    Returns:
        Tuple of:
        - text_content: Text to display (from AI message or report summary)
        - chart_figures: List of Plotly Figure objects to render
        - report_file_path: Path to downloadable report file or None
        - is_explicit_generation: True if generate_download_report was called

    """
    messages = result.get("messages", [])
    if not messages:
        return "Nenhuma resposta do agente.", [], None, False

    ai_messages = [m for m in messages if isinstance(m, AIMessage)]
    if not ai_messages:
        return "Erro no formato da resposta do agente.", [], None, False

    text_content = getattr(ai_messages[-1], "content", "")
    tools_called = _extract_tool_names(ai_messages)
    is_explicit_generation = "generate_download_report" in tools_called

    chart_figures, chart_metadata, report_path, report_content, chart_warnings = (
        _extract_tool_outputs(messages)
    )

    if report_content:
        text_content = report_content
    if chart_warnings:
        text_content = text_content + "\n\n" + " ".join(chart_warnings)

    return text_content, chart_figures, report_path, is_explicit_generation


def _extract_tool_names(ai_messages: list[AIMessage]) -> set[str]:
    """
    Extract unique tool names from AI messages with tool calls.

    Args:
        ai_messages: List of AIMessage objects

    Returns:
        Set of tool names that were called

    """
    tools: set[str] = set()
    for msg in ai_messages:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                name = (
                    tc.get("name")
                    if isinstance(tc, dict)
                    else getattr(tc, "name", None)
                )
                if name:
                    tools.add(name)
    return tools


def _extract_tool_outputs(  # noqa: C901
    messages: list,
) -> tuple[list[Figure], list[dict], str | None, str | None, list[str]]:
    """
    Extract charts and report info from tool messages.

    Processes ToolMessage objects to:
    - Generate Plotly figures from chart tool results
    - Extract report file paths and summaries from report tool results

    Args:
        messages: List of all messages from agent response

    Returns:
        Tuple of:
        - chart_figures: List of generated Figure objects
        - chart_metadata: List of chart statistics dicts
        - report_path: Report file path or None
        - report_content: Report summary text or None
        - chart_warnings: List of warning strings for chart failures

    """
    chart_figures = []
    chart_metadata = []
    report_path = None
    report_content = None
    chart_warnings: set[str] = set()

    tool_call_map = _build_tool_call_map(messages)

    for msg in messages:
        if not isinstance(msg, ToolMessage):
            continue

        tool_call_id = getattr(msg, "tool_call_id", None)

        # Process chart tools
        if tool_call_id and tool_call_id in tool_call_map:
            tool_name, tool_args = tool_call_map[tool_call_id]
            if tool_name in CHART_TOOL_NAMES:
                fig, metadata = render_tool_chart(tool_name, tool_args)
                if fig:
                    chart_figures.append(fig)
                    if metadata:
                        chart_metadata.append(metadata)
                else:
                    chart_warnings.add("Um gráfico não pôde ser gerado.")

        # Process report tools
        path, content = _extract_report_from_message(msg)
        if path:
            report_path = path
        if content:
            report_content = content

        # Extract charts from generate_chat_report output
        parsed = parse_tool_content(msg.content)
        if parsed and "daily_chart_json" in parsed:
            daily_json = parsed.get("daily_chart_json")
            monthly_json = parsed.get("monthly_chart_json")
            if daily_json:
                try:
                    daily_dict = (
                        json.loads(daily_json)
                        if isinstance(daily_json, str)
                        else daily_json
                    )
                    chart_figures.append(Figure(daily_dict))
                except Exception as e:
                    logger.warning("Failed to parse daily chart from report: %s", e)
                    chart_warnings.add(
                        "Gráfico do relatório não pôde ser interpretado."
                    )
            if monthly_json:
                try:
                    monthly_dict = (
                        json.loads(monthly_json)
                        if isinstance(monthly_json, str)
                        else monthly_json
                    )
                    chart_figures.append(Figure(monthly_dict))
                except Exception as e:
                    logger.warning("Failed to parse monthly chart from report: %s", e)
                    chart_warnings.add(
                        "Gráfico do relatório não pôde ser interpretado."
                    )

    return (
        chart_figures,
        chart_metadata,
        report_path,
        report_content,
        list(chart_warnings),
    )


def _build_tool_call_map(messages: list) -> dict[str, tuple[str, dict]]:
    """
    Build mapping from tool_call_id to (tool_name, tool_args).

    This is needed to match ToolMessage results back to their original
    tool calls, which contain the tool name and arguments.

    Args:
        messages: List of all messages from agent response

    Returns:
        Dict mapping tool_call_id to (tool_name, args_dict)

    """
    tool_map = {}
    for msg in messages:
        if not isinstance(msg, AIMessage):
            continue
        if not hasattr(msg, "tool_calls") or not msg.tool_calls:
            continue

        for tc in msg.tool_calls:
            if isinstance(tc, dict):
                tc_id, tc_name, tc_args = (
                    tc.get("id"),
                    tc.get("name"),
                    tc.get("args", {}),
                )
            else:
                tc_id = getattr(tc, "id", None)
                tc_name = getattr(tc, "name", None)
                tc_args = getattr(tc, "args", {})

            if tc_id and tc_name:
                tool_map[tc_id] = (tc_name, tc_args)

    return tool_map


def _extract_report_from_message(msg: ToolMessage) -> tuple[str | None, str | None]:
    """
    Extract report file path and content from a tool message.

    Args:
        msg: ToolMessage object

    Returns:
        Tuple of (file_path, report_content) - either may be None

    """
    if not hasattr(msg, "content"):
        return None, None

    parsed = parse_tool_content(msg.content)
    if not parsed:
        return None, None

    return extract_report_info(parsed)
