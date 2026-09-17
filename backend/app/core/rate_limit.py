"""A tiny in-process fixed-window rate limiter.

For a single-node local demo this is exactly enough and needs no Redis. If the
app were ever scaled horizontally, swap this for a shared store — the FastAPI
dependency below is the only integration point.
"""
from __future__ import annotations

import time
from threading import Lock

from fastapi import HTTPException, Request, status

from app.core.config import settings


class FixedWindowLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, list[float]] = {}
        self._lock = Lock()

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.monotonic()
        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None or now - bucket[0] >= window_seconds:
                self._buckets[key] = [now, 1.0]
                return True
            if bucket[1] >= limit:
                return False
            bucket[1] += 1
            return True

    def reset(self) -> None:
        with self._lock:
            self._buckets.clear()


limiter = FixedWindowLimiter()


def auth_rate_limit(request: Request) -> None:
    """Dependency guarding sensitive auth endpoints (login/register/refresh)."""
    client = request.client.host if request.client else "unknown"
    key = f"{client}:{request.url.path}"
    if not limiter.allow(key, settings.AUTH_RATE_LIMIT, settings.AUTH_RATE_WINDOW_SECONDS):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please slow down and try again shortly.",
        )
