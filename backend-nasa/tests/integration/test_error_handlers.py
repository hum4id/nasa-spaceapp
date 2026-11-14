from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

from app.core.config import Settings
from app.core.errors import NotFoundError
from app.main import create_app


class _Body(BaseModel):
    value: int


def _app_with_probe_routes(settings: Settings | None = None) -> FastAPI:
    app = create_app(settings)

    @app.get("/_probe/domain")
    async def domain_error() -> None:
        raise NotFoundError("thing not found")

    @app.get("/_probe/crash")
    async def crash() -> None:
        raise RuntimeError("secret internal detail")

    @app.post("/_probe/validate")
    async def validate(body: _Body) -> _Body:
        return body

    return app


@pytest.fixture
async def probe() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=_app_with_probe_routes(), raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.integration
@pytest.mark.anyio
async def test_domain_error_uses_envelope(probe: AsyncClient) -> None:
    r = await probe.get("/_probe/domain")
    assert r.status_code == 404
    assert r.json()["error"] == {"code": "not_found", "message": "thing not found", "details": None}


@pytest.mark.integration
@pytest.mark.anyio
async def test_unhandled_error_hides_internals(probe: AsyncClient) -> None:
    r = await probe.get("/_probe/crash")
    assert r.status_code == 500
    assert r.json()["error"]["code"] == "internal_error"
    assert "secret" not in r.text


@pytest.mark.integration
@pytest.mark.anyio
async def test_validation_error_lists_fields(probe: AsyncClient) -> None:
    r = await probe.post("/_probe/validate", json={"value": "not-a-number"})
    body = r.json()
    assert r.status_code == 422
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["details"][0]["loc"] == ["body", "value"]


@pytest.mark.integration
@pytest.mark.anyio
async def test_rate_limit_returns_envelope() -> None:
    app = _app_with_probe_routes(Settings(rate_limit_default="2/minute"))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        statuses = [(await c.get("/health")).status_code for _ in range(3)]
        last = await c.get("/health")
    assert statuses[:2] == [200, 200]
    assert last.status_code == 429
    assert last.json()["error"]["code"] == "rate_limited"
    assert int(last.headers["Retry-After"]) >= 1
