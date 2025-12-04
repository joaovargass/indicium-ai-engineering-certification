"""Tools module for SRAG agent."""

from tools.chart_tools import get_daily_chart_json, get_monthly_chart_json
from tools.metric_tools import (
    get_case_increase_rate,
    get_icu_occupancy_rate,
    get_mortality_rate,
    get_vaccination_rate,
)
from tools.news import search_srag_news_tool
from tools.reports import generate_chat_report, generate_download_report

ALL_TOOLS = [
    get_case_increase_rate,
    get_mortality_rate,
    get_icu_occupancy_rate,
    get_vaccination_rate,
    get_daily_chart_json,
    get_monthly_chart_json,
    generate_download_report,
    generate_chat_report,
    search_srag_news_tool,
]

__all__ = [
    "ALL_TOOLS",
    "get_case_increase_rate",
    "get_mortality_rate",
    "get_icu_occupancy_rate",
    "get_vaccination_rate",
    "get_daily_chart_json",
    "get_monthly_chart_json",
    "generate_download_report",
    "generate_chat_report",
    "search_srag_news_tool",
]
