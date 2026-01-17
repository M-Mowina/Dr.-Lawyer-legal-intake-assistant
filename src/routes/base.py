from fastapi import FastAPI, APIRouter, Depends, Body
import os
from workflow.state import AgentState
from workflow.graph import graph, DB_URL
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

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
