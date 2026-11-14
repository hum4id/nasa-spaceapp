"""Liveness endpoint used by Docker healthchecks."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.schemas import ApiResponse, ok
from app.features.health.schemas import HealthData

router = APIRouter(tags=["health"])


@router.get("/health", response_model=ApiResponse[HealthData])
async def health() -> ApiResponse[HealthData]:
    return ok(HealthData(status="ok", env=get_settings().app_env))
