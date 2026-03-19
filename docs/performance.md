# Performance Optimization Notes

## Phase 4 Changes

- Added database indexes for frequently filtered and ordered fields.
- Added `select_related('product')` for order queries to reduce N+1 queries.
- Added Redis caching for note and product list endpoints (30s TTL).

## How To Measure

1. Run Django server:

```powershell
python manage.py runserver 8000
```

2. Run FastAPI server:

```powershell
python -m uvicorn fastapi_app.main:app --host 127.0.0.1 --port 8001 --reload
```

3. Run benchmark:

```powershell
python scripts\benchmark_phase2.py
```

## Notes

- Cache invalidation happens on create/update/delete for notes and products.
- Redis must be running on `REDIS_URL` (default `redis://127.0.0.1:6379/1`).
