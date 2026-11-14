from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class HealthData(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: str
    env: str
