from sqlalchemy import Column, String, DateTime, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    initial_description = Column(String, nullable=False)
    history = Column(JSON, nullable=False)  # Stores conversation history as JSON
    current_questions = Column(JSON, nullable=True)  # Current questions to ask
    answers_so_far = Column(JSON, nullable=True)  # Collected answers
    is_complete = Column(Integer, default=0)  # 0 = not complete, 1 = complete
    final_description = Column(String, nullable=True)  # Final AI-generated description
    iteration_count = Column(Integer, default=0)  # Number of question rounds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())