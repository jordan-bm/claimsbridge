import boto3
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# boto3 SQS client — created once at import time
_sqs_client = None

def get_sqs_client():
    global _sqs_client
    if _sqs_client is None:
        _sqs_client = boto3.client(
            "sqs",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
    return _sqs_client


def publish_claim_event(claim_id: str, patient_id: str, insurer: str, total_charge: float):
    """
    Publish a claim-received event to SQS.
    Called after every successful POST /claims/.
    Returns the SQS MessageId on success, None on failure.
    """
    queue_url = os.getenv("SQS_QUEUE_URL")
    if not queue_url:
        logger.warning("SQS_QUEUE_URL not set — skipping event publish")
        return None

    event = {
        "event_type": "claim.received",
        "claim_id": claim_id,
        "patient_id": patient_id,
        "insurer": insurer,
        "total_charge": total_charge,
        "published_at": datetime.utcnow().isoformat() + "Z",
    }

    try:
        client = get_sqs_client()
        response = client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(event),
        )
        message_id = response["MessageId"]
        logger.info(f"SQS event published — claim_id={claim_id} message_id={message_id}")
        return message_id
    except Exception as e:
        logger.error(f"SQS publish failed — claim_id={claim_id} error={e}")
        return None