"""News search tool for SRAG health news."""

from typing import Annotated

from langchain_core.tools import tool

from common.config import MAX_NEWS_ARTICLES
from retrieval.news_fetcher import search_srag_news


@tool
def search_srag_news_tool(
    query: Annotated[str, "Search topic (e.g., 'surto gripe RS')."],
    max_results: Annotated[
        int, f"Max results (default: {MAX_NEWS_ARTICLES})."
    ] = MAX_NEWS_ARTICLES,
) -> list[dict]:
    """Search news about SRAG/flu outbreaks. Use for context, explanations, 'why' questions."""
    return search_srag_news(query, max_results=max_results)
