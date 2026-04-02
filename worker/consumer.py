# worker/consumer.py

import boto3
import json
import os
import sys
import time
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
root = logging.getLogger()
root.setLevel(logging.INFO)
root.handlers = []
root.addHandler(handler)

logger = logging.getLogger(__name__)


def get_sqs_client():
    return boto3.client(
        "sqs",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )


def process_message(message: dict):
    body = json.loads(message["Body"])
    claim_id = body.get("claim_id", "unknown")
    patient_id = body.get("patient_id", "unknown")
    insurer = body.get("insurer", "unknown")
    total_charge = body.get("total_charge", 0)
    published_at = body.get("published_at", "unknown")

    logger.info(
        f"[CONSUMER] Processing event — "
        f"claim_id={claim_id} "
        f"patient_id={patient_id} "
        f"insurer={insurer} "
        f"total_charge={total_charge} "
        f"published_at={published_at}"
    )
    time.sleep(0.5)
    logger.info(f"[CONSUMER] claim_id={claim_id} processed successfully")


def delete_message(client, queue_url: str, receipt_handle: str):
    client.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle,
    )


def poll(queue_url: str):
    client = get_sqs_client()
    logger.info(f"[CONSUMER] Starting — polling {queue_url}")

    while True:
        response = client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20,
        )
        messages = response.get("Messages", [])
        if not messages:
            logger.info("[CONSUMER] No messages — waiting...")
            continue

        for message in messages:
            try:
                process_message(message)
                delete_message(client, queue_url, message["ReceiptHandle"])
            except Exception as e:
                logger.error(f"[CONSUMER] Failed to process message — {e}")


if __name__ == "__main__":
    queue_url = os.getenv("SQS_QUEUE_URL")
    if not queue_url:
        raise ValueError("SQS_QUEUE_URL not set")
    poll(queue_url)
