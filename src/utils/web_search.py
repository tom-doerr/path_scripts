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
        # Use DuckDuckGo's Instant Answer API
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1,
                "no_redirect": 1,
            },
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()

        # Extract relevant results
        results = []
        if "RelatedTopics" in data:
            for topic in data["RelatedTopics"]:
                if "FirstURL" in topic and "Text" in topic:
                    results.append(
                        {
                            "title": topic.get("Text", "").split(" - ")[0],
                            "link": topic["FirstURL"],
                            "snippet": topic.get("Text", ""),
                        }
                    )

        return results[:5]  # Return top 5 results

    except requests.RequestException as e:
        print(f"Web search error: {str(e)}")
        return []
