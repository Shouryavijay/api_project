from celery import shared_task
from sqlalchemy.orm import Session

from fastapi_app.database import SessionLocal
from fastapi_app.scraper import SOURCE_NAME, run_hn_scrape


@shared_task
def run_scraper_task(limit: int = 30) -> dict[str, int | str]:
    db: Session = SessionLocal()
    try:
        fetched, inserted = run_hn_scrape(db, limit=limit)
        return {"source": SOURCE_NAME, "fetched": fetched, "inserted": inserted}
    finally:
        db.close()
