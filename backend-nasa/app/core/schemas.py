"""Shared API response envelope (ECC common-patterns: one consistent shape for every response).

Success: {"success": true,  "data": {...}, "error": null, "meta": null | {...}}
Failure: {"success": false, "data": null, "error": {"code": "...", "message": "..."}, "meta": null}
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ErrorInfo(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str = Field(description="Stable machine-readable error code")
    message: str = Field(description="Human-readable message, safe to show to users")
    details: list[dict[str, Any]] | None = Field(
        default=None, description="Field-level validation details"
    )


class PageMeta(BaseModel):
    model_config = ConfigDict(frozen=True)

    total: int = Field(ge=0)
    page: int = Field(ge=1)
    limit: int = Field(ge=1)


class ApiResponse[T](BaseModel):
    model_config = ConfigDict(frozen=True)

    success: bool
    data: T | None = None
    error: ErrorInfo | None = None
    meta: PageMeta | None = None


def ok[T](data: T, meta: PageMeta | None = None) -> ApiResponse[T]:
    return ApiResponse[T](success=True, data=data, meta=meta)


def fail(code: str, message: str, details: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Serialisable failure body (used by exception handlers)."""
    body = ApiResponse[None](
        success=False, error=ErrorInfo(code=code, message=message, details=details)
    )
    return body.model_dump(mode="json")
