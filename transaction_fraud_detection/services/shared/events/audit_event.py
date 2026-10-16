from datetime import datetime
import uuid
from datetime import datetime, timezone

def create_payment_audit_event(
    event_type: str,
    payment: dict,
    details: dict,
) -> dict:

    return {
    "event_type": event_type,

    "audit_id": str(uuid.uuid4()),

    "transaction_id":
        payment["transaction_id"],

    "customer_id":
        payment["customer_id"],

    "amount":
        payment["amount"],

     "@timestamp": 
     datetime.now(timezone.utc).isoformat()
    }

def create_fraud_audit_event(
    event_type: str,
    payment: dict,
    details: dict,
) -> dict:

    return {
    "event_type": event_type,

    "audit_id": str(uuid.uuid4()),

    "transaction_id":
        payment["transaction_id"],

    "customer_id":
        payment["customer_id"],

    "amount":
        payment["amount"],

    "country":
        payment["country"],

    "decision":
        details["fraud"],

    "fraud_score":
        details["risk_score"],

     "@timestamp": 
     datetime.now(timezone.utc).isoformat()
    }