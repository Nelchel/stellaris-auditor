from pydantic import BaseModel
from typing import Any


class HealthResponse(BaseModel):
    status: str
    version: str


class AuditResponse(BaseModel):
    mode: str
    data: dict[str, Any]
