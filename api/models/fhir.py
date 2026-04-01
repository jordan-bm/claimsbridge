# api/models/fhir.py

from pydantic import BaseModel
from typing import Optional

class FHIRPatient(BaseModel):
    resourceType: str = "Patient"
    id: str
    name: str
    birthDate: str

class FHIRInsurance(BaseModel):
    memberId: str
    insurer: str

class FHIRDiagnosis(BaseModel):
    code: str
    description: str

class FHIRClaim(BaseModel):
    resourceType: str = "Claim"
    id: str
    status: str
    patient: FHIRPatient
    insurance: FHIRInsurance
    diagnosis: FHIRDiagnosis
    totalCharge: float
    admissionDate: str
    sourceMessageId: str