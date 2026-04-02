# api/services/db.py

import os
import logging
import databases
import sqlalchemy

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/claimsbridge")

database = databases.Database(DATABASE_URL)

engine = sqlalchemy.create_engine(DATABASE_URL)

metadata = sqlalchemy.MetaData()

claims_table = sqlalchemy.Table(
    "claims",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("source_message_id", sqlalchemy.String),
    sqlalchemy.Column("status", sqlalchemy.String),
    sqlalchemy.Column("patient_id", sqlalchemy.String),
    sqlalchemy.Column("patient_name", sqlalchemy.String),
    sqlalchemy.Column("birth_date", sqlalchemy.String),
    sqlalchemy.Column("member_id", sqlalchemy.String),
    sqlalchemy.Column("insurer", sqlalchemy.String),
    sqlalchemy.Column("diagnosis_code", sqlalchemy.String),
    sqlalchemy.Column("total_charge", sqlalchemy.Float),
    sqlalchemy.Column("admission_date", sqlalchemy.String),
)


def create_tables() -> None:
    metadata.create_all(engine)
    logging.getLogger(__name__).info("DB tables verified/created")


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