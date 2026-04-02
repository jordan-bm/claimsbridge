# api/main.py

import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from api.services.logger import configure_logging
configure_logging()

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