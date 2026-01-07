from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from uuid import UUID
import json
from app.database import get_db
from app.models.session import Session as SessionModel
from app.schemas.session import CreateSessionRequest, CreateSessionResponse, SubmitResponseRequest, SubmitResponseResponse
from app.workflow.graph import create_workflow
from app.workflow.state import AgentState
from langchain_core.messages import HumanMessage
from app.config import settings

router = APIRouter()


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest, db: AsyncSession = Depends(get_db)):
    """
    Create a new legal intake session with the initial description.
    The AI will ask initial clarifying questions.
    """
    # Create the initial state for the workflow
    initial_state: AgentState = {
        "messages": [HumanMessage(content=request.initial_description)],
        "current_questions": [],
        "is_complete": False,
        "final_description": None,
        "answers_so_far": {},
        "iteration_count": 0,
        "initial_description": request.initial_description
    }
    
    # Create the workflow
    workflow = create_workflow()
    
    # Run the workflow to get initial questions
    result = await workflow.ainvoke(initial_state)
    
    # Create a new session record in the database
    db_session = SessionModel(
        initial_description=request.initial_description,
        history=[{"type": "human", "content": request.initial_description}],
        current_questions=result.get("current_questions", []),
        answers_so_far={},
        is_complete=1 if result.get("is_complete", False) else 0,
        final_description=result.get("final_description"),
        iteration_count=result.get("iteration_count", 0)
    )
    
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    
    return CreateSessionResponse(
        session_id=db_session.id,
        questions=result.get("current_questions", []),
        is_complete=result.get("is_complete", False)
    )


@router.post("/sessions/{session_id}/responses", response_model=SubmitResponseResponse)
async def submit_response(session_id: UUID, request: SubmitResponseRequest, db: AsyncSession = Depends(get_db)):
    """
    Submit answers to the AI's questions and receive follow-up questions or final description.
    """
    # Retrieve the existing session from the database
    result = await db.get(SessionModel, session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Reconstruct the state from the database
    answers_so_far = result.answers_so_far or {}
    answers_so_far.update(request.answers)
    
    # Update history with user's answers
    history = result.history or []
    for question, answer in request.answers.items():
        history.append({"type": "human", "content": f"Q: {question}", "answer": answer})
    
    # Create the state for the workflow
    state: AgentState = {
        "messages": [],  # We'll reconstruct this from history if needed
        "current_questions": result.current_questions or [],
        "is_complete": result.is_complete == 1,
        "final_description": result.final_description,
        "answers_so_far": answers_so_far,
        "iteration_count": result.iteration_count,
        "initial_description": result.initial_description
    }
    
    # If the session is already complete, return the final description
    if result.is_complete == 1 and result.final_description:
        return SubmitResponseResponse(
            session_id=result.id,
            questions=[],
            is_complete=True,
            final_description=result.final_description
        )
    
    # Create the workflow
    workflow = create_workflow()
    
    # Continue the workflow with the new answers
    # We need to update the state with the new answers and continue
    updated_state = state.copy()
    updated_state["answers_so_far"] = answers_so_far
    
    # Run the workflow from the current state
    result_state = await workflow.ainvoke(updated_state)
    
    # Update the database record
    result.current_questions = result_state.get("current_questions", [])
    result.answers_so_far = result_state.get("answers_so_far", {})
    result.is_complete = 1 if result_state.get("is_complete", False) else 0
    result.final_description = result_state.get("final_description")
    result.iteration_count = result_state.get("iteration_count", 0)
    result.history = history  # Update with new history
    
    await db.commit()
    await db.refresh(result)
    
    return SubmitResponseResponse(
        session_id=result.id,
        questions=result_state.get("current_questions", []),
        is_complete=result_state.get("is_complete", False),
        final_description=result_state.get("final_description")
    )


@router.get("/sessions/{session_id}", response_model=SubmitResponseResponse)
async def get_session_status(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Get the current status of a session (questions, completion status, final description).
    """
    result = await db.get(SessionModel, session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SubmitResponseResponse(
        session_id=result.id,
        questions=result.current_questions or [],
        is_complete=result.is_complete == 1,
        final_description=result.final_description
    )