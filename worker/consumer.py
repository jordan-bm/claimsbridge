# worker/consumer.py

import boto3
import json
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_sqs_client():
    return boto3.client(
        "sqs",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )


def process_message(message: dict):
    """
    Handle a single claim.received event.
    In a real system this might trigger downstream enrichment,
    notify a payer, update a reporting DB, etc.
    For now we log the event and acknowledge it was received.
    """
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

    # Simulate processing work
    time.sleep(0.5)

    logger.info(f"[CONSUMER] claim_id={claim_id} processed successfully")


def delete_message(client, queue_url: str, receipt_handle: str):
    """
    Delete the message from the queue after successful processing.
    If we don't delete it, SQS will re-deliver it after the visibility timeout.
    This is the acknowledgement pattern - only delete on success.
    """
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
            WaitTimeSeconds=20,  # long polling — waits up to 20s for messages
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
                # Don't delete — SQS will re-deliver after visibility timeout


if __name__ == "__main__":
    queue_url = os.getenv("SQS_QUEUE_URL")
    if not queue_url:
        raise ValueError("SQS_QUEUE_URL not set")
    poll(queue_url)