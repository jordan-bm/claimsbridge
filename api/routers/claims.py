# api/routers/claims.py

import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from api.models.hl7 import HL7Claim
from api.models.fhir import FHIRClaim
from api.services.transformer import hl7_to_fhir, fhir_to_hl7
from api.services.db import insert_claim
from api.services.sqs import publish_claim_event
import logging

logger = logging.getLogger(__name__)

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
            content = f.read().strip()
        if not content:
            continue
        records = json.loads(content)
        for record in records:
            try:
                hl7_claim = HL7Claim(**record)
                fhir_claim = hl7_to_fhir(hl7_claim)
                claims.append(fhir_claim)
            except Exception:
                continue
    return claims


@router.get("/")
async def list_claims():
    return load_all_claims()


@router.get("/{claim_id}")
async def get_claim(claim_id: str):
    all_claims = load_all_claims()
    for claim in all_claims:
        if claim.id == claim_id:
            return claim
    raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")


@router.post("/")
async def create_claim(claim: FHIRClaim):
    # Step 1 — write to legacy flat file (unchanged)
    hl7_claim = fhir_to_hl7(claim)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"claim_{claim.id}_{timestamp}.json"
    filepath = os.path.join(PROCESSED_DIR, filename)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump([hl7_claim.model_dump()], f, indent=2)

    # Step 2 — write to PostgreSQL
    await insert_claim(claim)

    # Step 3 — publish event to SQS
    message_id = publish_claim_event(
        claim_id=claim.id,
        patient_id=claim.patient.id,
        insurer=claim.insurance.insurer,
        total_charge=claim.totalCharge,
    )

    if message_id:
        logger.info(f"Claim {claim.id} processed — SQS message_id={message_id}")
    else:
        logger.warning(f"Claim {claim.id} processed — SQS publish skipped or failed")

    return claim
