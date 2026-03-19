import statistics
import time
from dataclasses import dataclass

import requests
from requests.exceptions import RequestException


@dataclass
class Result:
    label: str
    avg_ms: float
    p95_ms: float
    min_ms: float
    max_ms: float
    success_rate: float


def benchmark(label: str, url: str, requests_count: int = 50) -> Result:
    durations = []
    ok_count = 0

    for _ in range(requests_count):
        start = time.perf_counter()
        response = requests.get(url, timeout=10)
        end = time.perf_counter()
        durations.append((end - start) * 1000)
        if response.ok:
            ok_count += 1

    durations_sorted = sorted(durations)
    p95_index = max(0, int(len(durations_sorted) * 0.95) - 1)
    return Result(
        label=label,
        avg_ms=statistics.mean(durations_sorted),
        p95_ms=durations_sorted[p95_index],
        min_ms=durations_sorted[0],
        max_ms=durations_sorted[-1],
        success_rate=(ok_count / requests_count) * 100,
    )


def is_service_up(url: str) -> bool:
    try:
        response = requests.get(url, timeout=3)
        return response.ok
    except RequestException:
        return False


def print_result(result: Result) -> None:
    print(f"\n{result.label}")
    print(f"  avg: {result.avg_ms:.2f} ms")
    print(f"  p95: {result.p95_ms:.2f} ms")
    print(f"  min: {result.min_ms:.2f} ms")
    print(f"  max: {result.max_ms:.2f} ms")
    print(f"  success: {result.success_rate:.1f}%")


if __name__ == "__main__":
    django_url = "http://127.0.0.1:8000/api/health/"
    fastapi_url = "http://127.0.0.1:8001/health"

    print("Running benchmark against local services...")
    django_up = is_service_up(django_url)
    fastapi_up = is_service_up(fastapi_url)

    if not django_up:
        print("Django health endpoint is not reachable at http://127.0.0.1:8000/api/health/")
        print("Start Django: python manage.py runserver 8000")

    if not fastapi_up:
        print("FastAPI health endpoint is not reachable at http://127.0.0.1:8001/health")
        print("Start FastAPI: python -m uvicorn fastapi_app.main:app --host 127.0.0.1 --port 8001 --reload")

    if not django_up and not fastapi_up:
        raise SystemExit(1)

    if django_up:
        django_result = benchmark("Django health endpoint", django_url)
        print_result(django_result)

    if fastapi_up:
        fastapi_result = benchmark("FastAPI health endpoint", fastapi_url)
        print_result(fastapi_result)
