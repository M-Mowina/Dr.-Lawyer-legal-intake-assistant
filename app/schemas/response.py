from pydantic import BaseModel
from typing import List, Optional


class ErrorResponse(BaseModel):
    detail: str


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str