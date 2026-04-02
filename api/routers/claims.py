# api/routers/claims.py

import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from api.models.hl7 import HL7Claim
from api.models.fhir import FHIRClaim
from api.services.transformer import hl7_to_fhir, fhir_to_hl7
from api.services.db import insert_claim

router = APIRouter(prefix="/claims", tags=["claims"])

PROCESSED_DIR = os.path.join("legacy", "sample_data", "processed")


def load_all_claims() -> list[FHIRClaim]:
    claims = []
    if not os.path.exists(PROCESSED_DIR):
        return claims
    for filename in os.listdir(PROCESSED_DIR):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(PROCESSED_DIR, filename)
        with open(filepath, "r") as f:
            records = json.load(f)
        for record in records:
            try:
                hl7_claim = HL7Claim(**record)
                fhir_claim = hl7_to_fhir(hl7_claim)
                claims.append(fhir_claim)
            except Exception:
                continue
    return claims


@router.get("/", response_model=list[FHIRClaim])
def get_claims():
    claims = load_all_claims()
    if not claims:
        raise HTTPException(status_code=404, detail="No claims found")
    return claims


@router.get("/{claim_id}", response_model=FHIRClaim)
def get_claim_by_id(claim_id: str):
    claims = load_all_claims()
    for claim in claims:
        if claim.id == claim_id:
            return claim
    raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")


@router.post("/", response_model=FHIRClaim, status_code=201)
async def create_claim(claim: FHIRClaim):
    # Write to legacy flat file
    hl7_claim = fhir_to_hl7(claim)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"api_claim_{timestamp}_{hl7_claim.message_id}.json"
    filepath = os.path.join(PROCESSED_DIR, filename)
    with open(filepath, "w") as f:
        json.dump([hl7_claim.model_dump()], f, indent=2)

    # Write to PostgreSQL
    await insert_claim(claim)

    return claim