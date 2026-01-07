from pydantic import BaseModel
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime


class CreateSessionRequest(BaseModel):
    initial_description: str


class CreateSessionResponse(BaseModel):
    session_id: UUID
    questions: List[str]
    is_complete: bool


class SubmitResponseRequest(BaseModel):
    answers: Dict[str, str]


class SubmitResponseResponse(BaseModel):
    session_id: UUID
    questions: List[str]
    is_complete: bool
    final_description: Optional[str] = None