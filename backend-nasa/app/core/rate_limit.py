"""Global per-client rate limiting as a pure ASGI middleware (library: `limits`).

slowapi's middleware cannot see routes registered through FastAPI's included routers
(FastAPI >= 0.16x wraps them), so default limits silently never applied; this replaces it.

The key is the client IP from the ASGI scope. Behind a reverse proxy, run uvicorn with
--proxy-headers and set FORWARDED_ALLOW_IPS to the proxy address so the scope holds the
real client IP instead of the proxy's.
"""

from __future__ import annotations

import math
import time

from fastapi.responses import JSONResponse
from limits import RateLimitItem, parse
from limits.storage import MemoryStorage
from limits.strategies import MovingWindowRateLimiter
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.schemas import fail

UNKNOWN_CLIENT = "unknown"


class RateLimitMiddleware:
    def __init__(self, app: ASGIApp, limit: str, exempt_paths: frozenset[str] = frozenset()):
        self.app = app
        self.item: RateLimitItem = parse(limit)
        self.limiter = MovingWindowRateLimiter(MemoryStorage())
        self.exempt_paths = exempt_paths

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope.get("path") in self.exempt_paths:
            await self.app(scope, receive, send)
            return
        client = scope.get("client")
        key = client[0] if client else UNKNOWN_CLIENT
        if self.limiter.hit(self.item, key):
            await self.app(scope, receive, send)
            return
        reset = self.limiter.get_window_stats(self.item, key).reset_time
        retry_after = max(1, math.ceil(reset - time.time()))
        response = JSONResponse(
            status_code=429,
            content=fail("rate_limited", f"Rate limit exceeded: {self.item}"),
            headers={"Retry-After": str(retry_after)},
        )
        await response(scope, receive, send)
