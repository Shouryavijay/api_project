from fastapi_app.database import SessionLocal
from fastapi_app.scraper import SOURCE_NAME, run_hn_scrape


def main() -> None:
    db = SessionLocal()
    try:
        fetched, inserted = run_hn_scrape(db, limit=30)
        print(f"source={SOURCE_NAME} fetched={fetched} inserted={inserted}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
