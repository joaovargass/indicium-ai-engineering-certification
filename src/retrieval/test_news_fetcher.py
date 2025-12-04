"""
Test file for news_fetcher module.

This file will be deleted later - it's only for development testing.
"""

import sys
from pathlib import Path

# Add src to path for direct execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from retrieval.news_fetcher import search_srag_news


def test_basic_search() -> None:
    """Test basic news search functionality."""
    print("=" * 60)
    print("Test 1: Basic Search")
    print("=" * 60)
    test_query = "surto gripe aviária Rio Grande do Sul"
    print(f"Searching for: {test_query}\n")

    results = search_srag_news(test_query, max_results=3)

    if results:
        print(f"Found {len(results)} articles:\n")
        for i, article in enumerate(results, 1):
            print(f"{i}. {article['title']}")
            print(f"   URL: {article['url']}")
            print(f"   Date: {article['date'] or 'Not available'}")
            print(f"   Preview: {article['content'][:150]}...")
            print()
    else:
        print("No results found or error occurred.\n")


def test_state_query() -> None:
    """Test query with state code."""
    print("=" * 60)
    print("Test 2: State Code Query")
    print("=" * 60)
    test_query = "SRAG SP"
    print(f"Searching for: {test_query}\n")

    results = search_srag_news(test_query, max_results=2)

    if results:
        print(f"Found {len(results)} articles:\n")
        for i, article in enumerate(results, 1):
            print(f"{i}. {article['title']}")
            print(f"   URL: {article['url']}\n")
    else:
        print("No results found.\n")


def test_national_query() -> None:
    """Test query for national data."""
    print("=" * 60)
    print("Test 3: National Query")
    print("=" * 60)
    test_query = "mortes SRAG Brasil"
    print(f"Searching for: {test_query}\n")

    results = search_srag_news(test_query, max_results=2)

    if results:
        print(f"Found {len(results)} articles:\n")
        for i, article in enumerate(results, 1):
            print(f"{i}. {article['title']}")
            print(f"   URL: {article['url']}\n")
    else:
        print("No results found.\n")


def test_empty_query() -> None:
    """Test handling of empty query."""
    print("=" * 60)
    print("Test 4: Empty Query Handling")
    print("=" * 60)
    results = search_srag_news("")
    print(f"Results for empty query: {results}")
    print("Expected: Empty list []\n")


def test_invalid_max_results() -> None:
    """Test handling of invalid max_results parameter."""
    print("=" * 60)
    print("Test 5: Invalid max_results Parameter")
    print("=" * 60)
    # Test with max_results > 20 (should clamp to 20)
    results = search_srag_news("SRAG", max_results=50)
    print(f"Results with max_results=50: {len(results)} articles")
    print("Expected: Clamped to 20 max\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("NEWS FETCHER TEST SUITE")
    print("=" * 60 + "\n")

    try:
        test_basic_search()
        test_state_query()
        test_national_query()
        test_empty_query()
        test_invalid_max_results()

        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
