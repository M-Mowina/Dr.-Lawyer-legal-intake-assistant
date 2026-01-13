from fastapi import FastAPI, APIRouter, Depends, Body
import os
from workflow.nodes import ask_questions_node

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)

# ----- Base Route -----
@base_router.get("/")
async def welcome():

    app_name = os.getenv("APP_NAME")
    app_version = os.getenv("APP_VERSION")

    return {
        "app_name": app_name,
        "app_version": app_version,
    }

# ----- Ask Question Route -----
@base_router.post("/ask-questions")
async def ask_questions_route(initial_description: str = Body(...), previous_answers: str = Body("")):
    """
    Endpoint to ask clarifying questions based on the initial description and previous answers.
    """
    try:
        # Dynamically import the function to avoid module loading issues
        
        result = await ask_questions_node(initial_description, previous_answers)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
