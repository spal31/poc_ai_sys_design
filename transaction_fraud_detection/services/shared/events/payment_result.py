from datetime import datetime


def create_payment_result(
    payment: dict,
    status: str,
    reason: str | None = None,
) -> dict:

    return {
        "event_type": "PAYMENT_RESULT",

        "event_id": payment["event_id"],

        "transaction_id": payment["transaction_id"],

        "customer_id": payment["customer_id"],

        "amount": payment["amount"],

        "currency": payment["currency"],

        "status": status,

        "reason": reason,

        "processed_at": datetime.now().astimezone().isoformat(),
    }