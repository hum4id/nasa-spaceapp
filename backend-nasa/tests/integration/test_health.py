from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.anyio
async def test_health_returns_envelope(client: AsyncClient) -> None:
    response = await client.get("/health")
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["status"] == "ok"
    assert body["error"] is None


@pytest.mark.integration
@pytest.mark.anyio
async def test_unknown_route_returns_error_envelope(client: AsyncClient) -> None:
    response = await client.get("/api/v1/does-not-exist")
    body = response.json()
    assert response.status_code == 404
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "not_found"


@pytest.mark.integration
@pytest.mark.anyio
async def test_wrong_method_returns_error_envelope(client: AsyncClient) -> None:
    response = await client.post("/health")
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "method_not_allowed"
