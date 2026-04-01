# legacy/generator.py

import os
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "sample_data")


def generate_hl7_claim() -> str:
    """
    Generate a single HL7 v2.x-style claim record as a pipe-delimited flat string.

    Segments:
      MSH - Message Header
      PID - Patient Identification
      IN1 - Insurance / Payer Info
      CLM - Claim Information
      DG1 - Diagnosis
    """
    now = datetime.utcnow()
    msg_id = str(uuid.uuid4()).replace("-", "")[:20].upper()
    dob = fake.date_of_birth(minimum_age=18, maximum_age=85).strftime("%Y%m%d")
    service_date = (now - timedelta(days=random.randint(1, 30))).strftime("%Y%m%d")
    amount = round(random.uniform(100.0, 9999.99), 2)

    # ICD-10 diagnosis codes (small sample set)
    icd10_codes = ["J18.9", "I10", "E11.9", "Z00.00", "M54.5", "J06.9", "K21.0"]
    diag_code = random.choice(icd10_codes)

    # Place of service codes
    pos_codes = ["11", "21", "22", "23", "81"]
    pos = random.choice(pos_codes)

    patient_id = str(uuid.uuid4()).replace("-", "")[:10].upper()
    first = fake.first_name()
    last = fake.last_name()
    payer_id = random.choice(["BCBS01", "AETNA02", "UHC003", "CIGNA04", "HUMANA5"])

    segments = [
        # MSH - Message Header
        f"MSH|^~\\&|LEGACY_SYS|CLAIMS_DEPT|PAYER_GATEWAY|{payer_id}|{now.strftime('%Y%m%d%H%M%S')}||CLP^C01|{msg_id}|P|2.5",
        # PID - Patient Identification
        f"PID|1||{patient_id}^^^LEGACY_SYS||{last}^{first}||{dob}|{random.choice(['M', 'F'])}|||{fake.street_address().replace(',', '')}^^{fake.city()}^{fake.state_abbr()}^{fake.zipcode()}",
        # IN1 - Insurance
        f"IN1|1|{payer_id}|{payer_id}|{fake.company().replace('|', '-')}|||||||{fake.bothify(text='GRP-#####')}||||||{last}^{first}|SELF",
        # CLM - Claim
        f"CLM|{msg_id}|{amount}|||{pos}:B:1|Y|A|Y|I",
        # DG1 - Diagnosis
        f"DG1|1||{diag_code}^{diag_code}^I10|PRINCIPAL DIAGNOSIS|{service_date}|A",
    ]

    return "\n".join(segments)


def write_claims_file(num_claims: int = 10, filename: str = None) -> str:
    """
    Generate `num_claims` HL7 records and write them to a flat file in sample_data/.
    Each record is separated by a blank line.
    Returns the path to the written file.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if filename is None:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"claims_{timestamp}.hl7"

    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w") as f:
        for i in range(num_claims):
            f.write(generate_hl7_claim())
            f.write("\n\n")  # blank line between records

    print(f"[generator] Wrote {num_claims} claims to {filepath}")
    return filepath


if __name__ == "__main__":
    write_claims_file(num_claims=10)