# api/main.py

from dotenv import load_dotenv
load_dotenv()
import logging
logging.basicConfig(level=logging.INFO)

import os
import databases
from fastapi import FastAPI
from api.routers import health, claims
from api.services import db

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/claimsbridge")

database = databases.Database(DATABASE_URL)

app = FastAPI(
    title="ClaimsBridge",
    description="HL7 v2 to FHIR claims modernization API",
    version="0.3.0",
)

@app.on_event("startup")
async def startup():
    await database.connect()
    await db.database.connect()
    print("Connected to PostgreSQL")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    await db.database.disconnect()
    print("Disconnected from PostgreSQL")

app.include_router(health.router)
app.include_router(claims.router)