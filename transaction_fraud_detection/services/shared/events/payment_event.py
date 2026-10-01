from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class PaymentEvent:
    event_id: str
    transaction_id: str

    customer_id: str

    amount: Decimal
    currency: str

    merchant_id: str

    payment_method: str

    country: str

    ip_address: str

    device_id: str

    timestamp: datetime

    status: str = "INITIATED"

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "transaction_id": self.transaction_id,
            "customer_id": self.customer_id,
            "amount": str(self.amount),
            "currency": self.currency,
            "merchant_id": self.merchant_id,
            "payment_method": self.payment_method,
            "country": self.country,
            "ip_address": self.ip_address,
            "device_id": self.device_id,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
        }