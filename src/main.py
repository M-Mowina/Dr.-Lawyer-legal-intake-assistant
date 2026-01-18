from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv(".env")

from routes import base, start_intake, optimize_offer

app = FastAPI()

app.include_router(start_intake.start_intake_router)
app.include_router(optimize_offer.offer_router)
app.include_router(base.base_router)