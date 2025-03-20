"""Web search functionality using DuckDuckGo API."""

import requests
from typing import List, Dict


def search_web(query: str) -> List[Dict[str, str]]:
    """
    Perform a web search using DuckDuckGo Instant Answer API.

    Args:
        query: Search query string

    Returns:
        List of search results with title, link and snippet
    """
    if not query.strip():
        return []

    try:
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1,
            },
            timeout=5,
        )
        response.raise_for_status()

        data = response.json()
        results = []
        
        # Extract basic results from RelatedTopics
        for topic in data.get("RelatedTopics", []):
            if "FirstURL" in topic and "Text" in topic:
                results.append({
                    "title": topic["Text"].split(" - ")[0],
                    "link": topic["FirstURL"],
                    "snippet": topic["Text"]
                })

        return results[:3]  # Return top 3 results to keep it simple

    except requests.RequestException:
        return []  # Fail silently for now
