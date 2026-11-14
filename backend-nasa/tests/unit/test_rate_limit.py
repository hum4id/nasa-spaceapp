from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.rate_limit import RateLimitMiddleware


def _app(limit: str, exempt: frozenset[str] = frozenset()) -> FastAPI:
    app = FastAPI()

    @app.get("/ping")
    async def ping() -> dict[str, str]:
        return {"pong": "ok"}

    app.add_middleware(RateLimitMiddleware, limit=limit, exempt_paths=exempt)
    return app


@pytest.mark.unit
@pytest.mark.anyio
async def test_exempt_path_is_never_limited() -> None:
    app = _app("1/minute", frozenset({"/ping"}))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        codes = [(await c.get("/ping")).status_code for _ in range(3)]
    assert codes == [200, 200, 200]


@pytest.mark.unit
@pytest.mark.anyio
async def test_clients_are_limited_independently() -> None:
    app = _app("1/minute")
    a = ASGITransport(app=app, client=("10.0.0.1", 1))
    b = ASGITransport(app=app, client=("10.0.0.2", 1))
    async with (
        AsyncClient(transport=a, base_url="http://t") as ca,
        AsyncClient(transport=b, base_url="http://t") as cb,
    ):
        assert (await ca.get("/ping")).status_code == 200
        assert (await ca.get("/ping")).status_code == 429
        assert (await cb.get("/ping")).status_code == 200
