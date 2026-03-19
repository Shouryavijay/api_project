# Notes API

JWT-authenticated backend project with Django REST Framework and a FastAPI service.

## Quick Start

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py test --keepdb
python manage.py createsuperuser
python manage.py runserver
```

## Environment Variables

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG` (`true`/`false`)
- `DJANGO_ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`
- `MYSQL_DATABASE` (default: `notes_api`)
- `MYSQL_USER` (default: `notes_user`)
- `MYSQL_PASSWORD` (default: `notes_pass_123`)
- `MYSQL_HOST` (default: `localhost`)
- `MYSQL_PORT` (default: `3306`)
- `REDIS_URL` (default: `redis://127.0.0.1:6379/1`)
- `FASTAPI_DATABASE_URL` (optional override)
- `FASTAPI_JWT_SECRET_KEY`

## Django API

- `POST /api/register/`
- `POST /api/token/`
- `POST /api/token/refresh/`
- `GET /api/me/`
- `GET/POST /api/notes/`
- `GET/PUT/DELETE /api/notes/{id}/`
- `GET/POST /api/products/`
- `GET/PUT/DELETE /api/products/{id}/`
- `GET/POST /api/orders/`
- `GET/PUT/DELETE /api/orders/{id}/`

## FastAPI (Phase 2)

```powershell
python -m uvicorn fastapi_app.main:app --host 127.0.0.1 --port 8001 --reload
```

- Docs: `http://127.0.0.1:8001/docs`

## Scraper (Phase 3)

- `POST /scraper/run?limit=30` (JWT required)
- `GET /scraper/items` (JWT required)

CLI:

```powershell
python scripts\run_scraper_once.py
```

## Performance (Phase 4)

See `docs/performance.md`.

## Docker (Phase 5)

```powershell
docker compose up --build
```

## Capstone (Phase 6)

Run Celery worker:

```powershell
celery -A backend worker -l info
```

Run Celery beat:

```powershell
celery -A backend beat -l info
```

Trigger scrape task:

```powershell
python manage.py shell -c "from api.tasks import run_scraper_task; print(run_scraper_task.delay(30))"
```
