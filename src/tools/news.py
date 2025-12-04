"""News search tool for SRAG health news."""

from langchain_core.tools import tool
from pydantic import Field

from retrieval.news_fetcher import search_srag_news


@tool
def search_srag_news_tool(
    query: str = Field(..., description="Search topic (e.g., 'surto gripe RS')."),
    max_results: int = Field(default=5, description="Max results (default: 5)."),
) -> list[dict]:
    """Search news about SRAG/flu outbreaks. Use for context, explanations, 'why' questions."""
    return search_srag_news(query, max_results=max_results)
