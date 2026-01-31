from fastapi import APIRouter
from workflow.nodes import llm
from workflow.prompts import EDIT_DESCRIPTION_PROMPT
from pydantic import BaseModel

refine_router = APIRouter(
    prefix="/api/v1",
    tags=["Utils"],
)

# ----- Optimize offer route -----
class RefineRequest(BaseModel):
    final_description: str
    comments: str

@refine_router.post("/refine_description")
async def refine_description(prompts: RefineRequest):
    """Refine the given description"""

    prompt = EDIT_DESCRIPTION_PROMPT.invoke({"final_description": prompts.final_description, "user_comment": prompts.comments}).messages[-1].content
    response = (await llm.ainvoke(prompt))

    return response.content
