"""Tests for web search functionality."""

from src.utils.web_search import search_web

def test_search_web_success():
    """Test successful web search returns results."""
    query = "Python programming language"
    results = search_web(query)
    
    assert isinstance(results, list)
    assert len(results) > 0
    for result in results:
        assert "title" in result
        assert "link" in result
        assert "snippet" in result

def test_search_web_empty_query():
    """Test empty query returns empty results."""
    results = search_web("")
    assert results == []

def test_search_web_special_chars():
    """Test search with special characters."""
    query = "Python 3.11+ features"
    results = search_web(query)
    assert len(results) > 0

def test_search_web_long_query():
    """Test search with long query."""
    query = " ".join(["Python"] * 50)  # 50 words
    results = search_web(query)
    assert len(results) > 0
