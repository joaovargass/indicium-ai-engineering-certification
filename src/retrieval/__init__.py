"""Retrieval module - data fetchers for ICU beds and news."""

from retrieval.icu_beds import get_icu_beds_data, get_location_icu_beds
from retrieval.news_fetcher import search_srag_news

__all__ = [
    "get_icu_beds_data",
    "get_location_icu_beds",
    "search_srag_news",
]
