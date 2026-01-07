from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.session import Session as SessionModel
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


async def get_session_by_id(session_id: UUID, db: AsyncSession = Depends(get_db)) -> SessionModel:
    """
    Dependency to get a session by ID, with error handling.
    """
    session = await db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found"
        )
    return session