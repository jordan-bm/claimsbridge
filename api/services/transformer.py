# api/services/transformer.py

from api.models.hl7 import HL7Claim
from api.models.fhir import FHIRClaim, FHIRPatient, FHIRInsurance, FHIRDiagnosis

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