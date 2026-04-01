# legacy/processor.py

import os
import json
from datetime import datetime

INPUT_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "sample_data", "processed")


def parse_segment(segment: str) -> dict:
    """
    Parse a single HL7 segment into a dict with the segment name and its fields.
    Example: "MSH|^~\\&|LEGACY_SYS|..." → {"segment": "MSH", "fields": ["^~\\&", "LEGACY_SYS", ...]}
    """
    parts = segment.split("|")
    return {
        "segment": parts[0],
        "fields": parts[1:],
    }


def parse_hl7_record(raw: str) -> dict:
    """
    Parse a full multi-segment HL7 record (as a single string) into a structured dict.
    """
    segments = [line.strip() for line in raw.strip().splitlines() if line.strip()]
    parsed = {}

    for seg_str in segments:
        seg = parse_segment(seg_str)
        name = seg["segment"]
        fields = seg["fields"]

        if name == "MSH":
            parsed["message_id"] = fields[8] if len(fields) > 8 else None
            parsed["sending_facility"] = fields[2] if len(fields) > 2 else None
            parsed["timestamp"] = fields[6] if len(fields) > 6 else None
            parsed["payer_id"] = fields[4] if len(fields) > 4 else None

        elif name == "PID":
            parsed["patient_id"] = fields[2].split("^")[0] if len(fields) > 2 else None
            name_field = fields[4].split("^") if len(fields) > 4 else []
            parsed["patient_last"] = name_field[0] if len(name_field) > 0 else None
            parsed["patient_first"] = name_field[1] if len(name_field) > 1 else None
            parsed["dob"] = fields[6] if len(fields) > 6 else None
            parsed["gender"] = fields[7] if len(fields) > 7 else None

        elif name == "CLM":
            parsed["claim_amount"] = fields[1] if len(fields) > 1 else None
            parsed["place_of_service"] = fields[4].split(":")[0] if len(fields) > 4 else None

        elif name == "DG1":
            diag_field = fields[2].split("^") if len(fields) > 2 else []
            parsed["diagnosis_code"] = diag_field[0] if diag_field else None
            parsed["service_date"] = fields[4] if len(fields) > 4 else None

    return parsed


def validate_record(record: dict) -> list[str]:
    """
    Validate required fields. Returns a list of error strings (empty = valid).
    """
    errors = []
    required = ["message_id", "patient_id", "patient_last", "claim_amount", "diagnosis_code"]
    for field in required:
        if not record.get(field):
            errors.append(f"Missing required field: {field}")
    return errors


def process_file(filepath: str) -> dict:
    """
    Read a .hl7 flat file, parse and validate each record, and write a processed JSON output.
    Returns a summary dict.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(filepath, "r") as f:
        content = f.read()

    # Records are separated by blank lines
    raw_records = [r.strip() for r in content.strip().split("\n\n") if r.strip()]

    results = []
    accepted = 0
    rejected = 0

    for raw in raw_records:
        record = parse_hl7_record(raw)
        errors = validate_record(record)

        if errors:
            record["status"] = "REJECTED"
            record["errors"] = errors
            rejected += 1
        else:
            record["status"] = "ACCEPTED"
            record["errors"] = []
            accepted += 1

        results.append(record)

    # Write output file
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    output_filename = f"{base_name}_processed.json"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    summary = {
        "source_file": filepath,
        "output_file": output_path,
        "total": len(results),
        "accepted": accepted,
        "rejected": rejected,
        "processed_at": datetime.utcnow().isoformat(),
    }

    print(f"[processor] {summary}")
    return summary


def process_all():
    """
    Process all unprocessed .hl7 files in the sample_data/ directory.
    """
    files = [
        os.path.join(INPUT_DIR, f)
        for f in os.listdir(INPUT_DIR)
        if f.endswith(".hl7")
    ]

    if not files:
        print("[processor] No .hl7 files found.")
        return

    for filepath in files:
        process_file(filepath)


if __name__ == "__main__":
    process_all()