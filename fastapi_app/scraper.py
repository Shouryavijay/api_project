from collections.abc import Iterable
import hashlib

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from .models import ScrapedItem

HN_URL = "https://news.ycombinator.com/"
SOURCE_NAME = "hackernews"


def fetch_hn_items(limit: int = 30) -> list[dict[str, str]]:
    response = requests.get(HN_URL, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.select("span.titleline > a")

    items: list[dict[str, str]] = []
    for link in links[:limit]:
        title = link.get_text(strip=True)
        url = link.get("href", "").strip()
        if not title or not url:
            continue
        if url.startswith("item?id="):
            url = f"https://news.ycombinator.com/{url}"
        items.append({"source": SOURCE_NAME, "title": title, "url": url})
    return items


def persist_items(db: Session, items: Iterable[dict[str, str]]) -> int:
    inserted = 0
    for item in items:
        url_hash = hashlib.sha256(item["url"].encode("utf-8")).hexdigest()
        exists = db.query(ScrapedItem).filter(ScrapedItem.url_hash == url_hash).first()
        if exists:
            continue
        db_item = ScrapedItem(
            source=item["source"],
            title=item["title"],
            url=item["url"],
            url_hash=url_hash,
        )
        db.add(db_item)
        inserted += 1
    db.commit()
    return inserted


def run_hn_scrape(db: Session, limit: int = 30) -> tuple[int, int]:
    fetched_items = fetch_hn_items(limit=limit)
    inserted = persist_items(db, fetched_items)
    return len(fetched_items), inserted
