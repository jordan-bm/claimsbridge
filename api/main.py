# api/main.py

from fastapi import FastAPI
from api.routers import health, claims

app = FastAPI(
    title="ClaimsBridge API",
    description="HL7 v2 legacy claims system wrapped in a FHIR-compliant REST API",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(claims.router)