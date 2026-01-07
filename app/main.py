from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import sessions
from app.database import engine
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Dr. Lawyer Legal Intake Assistant",
    description="AI-powered legal case intake assistant that asks clarifying questions and generates professional case descriptions",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up legal intake assistant API...")
    # Initialize database connection
    async with engine.begin() as conn:
        # Create tables if they don't exist
        from app.models.session import Session  # Import here to ensure models are registered
        from app.database import Base
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down legal intake assistant API...")
    await engine.dispose()

@app.get("/")
def read_root():
    return {"message": "Dr. Lawyer Legal Intake Assistant API"}