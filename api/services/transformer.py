# api/services/transformer.py

from api.models.hl7 import HL7Claim
from api.models.fhir import FHIRClaim, FHIRPatient, FHIRInsurance, FHIRDiagnosis
import uuid

def hl7_to_fhir(claim: HL7Claim) -> FHIRClaim:
    return FHIRClaim(
        id=claim.message_id,
        status="active" if claim.status == "ACCEPTED" else "cancelled",
        patient=FHIRPatient(
            id=claim.patient_id,
            name=f"{claim.patient_first} {claim.patient_last}",
            birthDate=claim.dob,
        ),
        insurance=FHIRInsurance(
            memberId=claim.patient_id,
            insurer=claim.payer_id or "unknown",
        ),
        diagnosis=FHIRDiagnosis(
            code=claim.diagnosis_code,
            description=claim.diagnosis_code,
        ),
        totalCharge=float(claim.claim_amount),
        admissionDate=claim.service_date,
        sourceMessageId=claim.message_id,
    )

def fhir_to_hl7(claim: FHIRClaim) -> HL7Claim:
    name_parts = claim.patient.name.split(" ", 1)
    first = name_parts[0] if len(name_parts) > 0 else ""
    last = name_parts[1] if len(name_parts) > 1 else ""

    return HL7Claim(
        message_id=claim.sourceMessageId or str(uuid.uuid4()).replace("-", "").upper()[:20],
        sending_facility="CLAIMSBRIDGE_API",
        timestamp="",
        payer_id=claim.insurance.insurer,
        patient_id=claim.patient.id,
        patient_last=last,
        patient_first=first,
        dob=claim.patient.birthDate,
        gender="U",
        claim_amount=str(claim.totalCharge),
        place_of_service="21",
        diagnosis_code=claim.diagnosis.code,
        service_date=claim.admissionDate,
        status="ACCEPTED" if claim.status == "active" else "REJECTED",
        errors=[],
    )