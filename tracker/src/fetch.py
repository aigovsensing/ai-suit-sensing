from __future__ import annotations
import feedparser
from dataclasses import dataclass
from typing import List
from datetime import datetime, timezone
from .queries import NEWS_QUERIES
from .utils import debug_log, parse_dt

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"

@dataclass
class NewsItem:
    title: str
    url: str
    published_at: datetime | None
    source: str

def fetch_news() -> List[NewsItem]:
    items: List[NewsItem] = []
    seen: set[str] = set()

    for q in NEWS_QUERIES:
        debug_log(f"Fetching news for query: {q}")
        feed_url = GOOGLE_NEWS_RSS.format(q=q.replace(" ", "%20"))
        feed = feedparser.parse(feed_url)
        debug_log(f"Found {len(feed.entries)} entries for query: {q}")

        for e in feed.entries:
            title = getattr(e, "title", "").strip()
            link = getattr(e, "link", "").strip()
            published = parse_dt(getattr(e, "published", None))
            source = ""
            if hasattr(e, "source") and e.source:
                source = getattr(e.source, "title", "") or ""
            if not link or link in seen:
                continue
            seen.add(link)
            items.append(NewsItem(title=title, url=link, published_at=published, source=source))

    items.sort(key=lambda x: x.published_at or datetime(1970, 1, 1, tzinfo=timezone.utc), reverse=True)
    return items
