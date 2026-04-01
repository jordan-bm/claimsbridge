# api/services/transformer.py

from api.models.hl7 import HL7Claim
from api.models.fhir import FHIRClaim, FHIRPatient, FHIRInsurance, FHIRDiagnosis

def hl7_to_fhir(claim: HL7Claim) -> FHIRClaim:
    return FHIRClaim(
        id=claim.claim_id,
        status="active" if claim.status == "ACCEPTED" else "cancelled",
        patient=FHIRPatient(
            id=claim.patient_id,
            name=claim.patient_name,
            birthDate=claim.date_of_birth,
        ),
        insurance=FHIRInsurance(
            memberId=claim.member_id,
            insurer=claim.insurance_company,
        ),
        diagnosis=FHIRDiagnosis(
            code=claim.diagnosis_code,
            description=claim.diagnosis_description,
        ),
        totalCharge=claim.total_charge,
        admissionDate=claim.admission_date,
        sourceMessageId=claim.message_id,
    )