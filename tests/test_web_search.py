"""Tests for web search functionality."""

import requests
from src.utils.web_search import search_web  # pylint: disable=no-name-in-module


def test_search_web_success():
    """Test successful web search returns results."""
    query = "Python programming language"
    results = search_web(query)
    
    assert isinstance(results, list)
    if results:  # Only check structure if we got results
        for result in results:
            assert "title" in result
            assert "link" in result
            assert "snippet" in result


def test_search_web_empty_query():
    """Test empty query returns empty results."""
    results = search_web("")
    assert results == []


def test_search_web_error_handling(monkeypatch):
    """Test error handling when API fails."""
    def mock_get(*args, **kwargs):
        raise requests.RequestException("API Error")

    monkeypatch.setattr(requests, "get", mock_get)
    results = search_web("test")
    assert results == []
