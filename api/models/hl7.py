# api/models/hl7.py

from pydantic import BaseModel
from typing import Optional

class HL7Claim(BaseModel):
    message_id: str
    sending_facility: Optional[str] = None
    timestamp: Optional[str] = None
    payer_id: Optional[str] = None
    patient_id: str
    patient_last: str
    patient_first: str
    dob: str
    gender: Optional[str] = None
    claim_amount: str
    place_of_service: Optional[str] = None
    diagnosis_code: str
    service_date: str
    status: Optional[str] = None
    errors: Optional[list] = []