"""News retrieval using Tavily API."""

import os
from typing import Any

from dotenv import load_dotenv
from tavily import TavilyClient

from common.config import BRAZILIAN_STATES, HEALTH_KEYWORDS_EN, HEALTH_KEYWORDS_PT

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not found. Set it in .env file.")

STATE_NAME_PATTERNS = [
    "são paulo",
    "rio de janeiro",
    "rio grande do sul",
    "minas gerais",
    "santa catarina",
    "paraná",
    "bahia",
    "goiás",
    "ceará",
    "pernambuco",
    "pará",
    "amazonas",
    "espírito santo",
    "mato grosso",
    "rio grande do norte",
    "alagoas",
    "piauí",
    "maranhão",
    "paraíba",
    "distrito federal",
    "rondônia",
    "acre",
    "amapá",
    "roraima",
    "sergipe",
    "tocantins",
    "mato grosso do sul",
]


def _enhance_query(query: str) -> str:
    """Add health keywords and Brazil context to search query."""
    query_lower = query.lower()

    state_mentioned = any(
        code.lower() in query_lower for code in BRAZILIAN_STATES
    ) or any(pattern in query_lower for pattern in STATE_NAME_PATTERNS)

    enhanced = query
    if state_mentioned and "brasil" not in query_lower and "brazil" not in query_lower:
        enhanced = f"{query} Brasil"

    all_keywords = HEALTH_KEYWORDS_PT + HEALTH_KEYWORDS_EN
    if not any(kw.lower() in query_lower for kw in all_keywords):
        enhanced = f"{enhanced} saúde SRAG"

    return enhanced


def search_srag_news(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """
    Search for SRAG/health news in Brazil using Tavily API.

    Args:
        query: Search topic.
        max_results: Max results (1-20, default: 5).

    Returns:
        List of dicts with title, url, content, date. Empty on error.

    """
    if not query or not query.strip():
        return []

    max_results = max(1, min(20, max_results))

    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(
            query=_enhance_query(query),
            search_depth="advanced",
            max_results=max_results,
            include_answer=False,
        )

        articles = []
        for result in response.get("results", [])[:max_results]:
            title = result.get("title", "").strip()
            url = result.get("url", "").strip()
            if title and url:
                articles.append(
                    {
                        "title": title,
                        "url": url,
                        "content": result.get(
                            "content", result.get("snippet", "")
                        ).strip(),
                        "date": result.get("published_date", "").strip(),
                    }
                )
        return articles

    except Exception as e:
        print(f"Error fetching news: {e}")
        return []
