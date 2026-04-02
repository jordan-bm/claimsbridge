# api/services/db.py

import os
import databases

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/claimsbridge")

database = databases.Database(DATABASE_URL)


async def insert_claim(claim) -> None:
    query = """
        INSERT INTO claims (
            id, source_message_id, status, patient_id, patient_name,
            birth_date, member_id, insurer, diagnosis_code,
            total_charge, admission_date
        ) VALUES (
            :id, :source_message_id, :status, :patient_id, :patient_name,
            :birth_date, :member_id, :insurer, :diagnosis_code,
            :total_charge, :admission_date
        )
        ON CONFLICT (id) DO NOTHING;
    """
    values = {
        "id": claim.id,
        "source_message_id": claim.sourceMessageId,
        "status": claim.status,
        "patient_id": claim.patient.id,
        "patient_name": claim.patient.name,
        "birth_date": claim.patient.birthDate,
        "member_id": claim.insurance.memberId,
        "insurer": claim.insurance.insurer,
        "diagnosis_code": claim.diagnosis.code,
        "total_charge": claim.totalCharge,
        "admission_date": claim.admissionDate,
    }
    await database.execute(query=query, values=values)