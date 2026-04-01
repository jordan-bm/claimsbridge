# api/routers/claims.py

import os
import json
from fastapi import APIRouter, HTTPException
from api.models.hl7 import HL7Claim
from api.models.fhir import FHIRClaim
from api.services.transformer import hl7_to_fhir

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
            except Exception as e:
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