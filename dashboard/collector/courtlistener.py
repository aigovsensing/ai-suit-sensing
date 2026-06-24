import requests
import logging

logger = logging.getLogger(__name__)

def fetch_cases(query="artificial intelligence", page_size=50):
    url = "https://www.courtlistener.com/api/rest/v3/dockets/"
    params = {"search": query, "page_size": page_size}
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        return res.json().get("results", [])
    except Exception as e:
        logger.error(f"Error fetching from CourtListener: {e}")
        return []
