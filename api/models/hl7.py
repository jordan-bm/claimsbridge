# api/models/hl7.py

from pydantic import BaseModel
from typing import Optional

class HL7Claim(BaseModel):
    message_id: str
    patient_id: str
    patient_name: str
    date_of_birth: str
    insurance_company: str
    member_id: str
    claim_id: str
    total_charge: float
    admission_date: str
    diagnosis_code: str
    diagnosis_description: str
    status: Optional[str] = None
    errors: Optional[list] = []