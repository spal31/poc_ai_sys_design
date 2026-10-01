from datetime import datetime
import uuid


def create_audit_event(
    event_type: str,
    payment: dict,
    details: dict,
) -> dict:

    return {
        "event_type": "PAYMENT_AUDIT",

        "audit_id": str(uuid.uuid4()),

        "source_event_id":
            payment["event_id"],

        "transaction_id":
            payment["transaction_id"],

        "customer_id":
            payment["customer_id"],

        "audit_type":
            event_type,

        "details":
            details,

        "created_at":
            datetime.now().astimezone().isoformat(),
    }