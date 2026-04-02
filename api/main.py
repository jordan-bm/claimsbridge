# api/main.py

import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from api.services.logger import configure_logging
configure_logging()

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
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


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title="ClaimsBridge API",
        version="1.0.0",
        description="FHIR-compliant REST API wrapping a legacy HL7 v2 claims processor.",
        routes=app.routes,
    )
    schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
        }
    }
    schema["security"] = [{"APIKeyHeader": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi