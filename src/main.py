from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv(".env")

from routes import base, start_intake, optimize_offer, optimize_case_description, upload_parser

app = FastAPI()

origins = [
    "http://localhost:3000",       # React dev server (common)
    "http://localhost:5173",       # Vite dev server (very common 2025–2026)
    "http://localhost:4200",       # Angular dev
    "http://127.0.0.1:3000",       # sometimes people use 127 instead of localhost
    #"https://your-frontend-domain.com",          # ← production frontend
    #"https://staging.your-app.com",              # if you have staging
    # "https://*.your-vercel-domain.app",        # if needed (better with regex below)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],              # ← or ["*"] for dev only (see warning below)
    allow_credentials=True,             # ← set True if using cookies / Authorization header
    allow_methods=["*"],                # allows GET, POST, PUT, DELETE, OPTIONS, etc.
    allow_headers=["*"],                # allows Content-Type, Authorization, etc.
)

app.include_router(start_intake.start_intake_router)
app.include_router(upload_parser.upload_router)
app.include_router(optimize_case_description.refine_router)
app.include_router(optimize_offer.offer_router)
app.include_router(base.base_router)