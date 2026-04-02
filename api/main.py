# api/main.py

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI
from api.routers import claims, health
from api.services.db import create_tables, database
from api.middleware.auth import APIKeyMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    create_tables()
    yield
    await database.disconnect()


app = FastAPI(title="ClaimsBridge API", lifespan=lifespan)

app.add_middleware(APIKeyMiddleware)

app.include_router(health.router)
app.include_router(claims.router)