from fastapi import APIRouter, HTTPException
import random
import time
import logging
import uuid

from telemetry import (
    payment_success_counter,
    payment_failed_counter,
    payment_latency,
    http_500_counter
)

router = APIRouter()
logger = logging.getLogger("payment-service")

@router.get("/payment")
def payment():

    start = time.perf_counter()

    payment_id = str(uuid.uuid4())[:8]
    amount = random.randint(100, 5000)

    logger.info(
        "Payment request received",
        extra={
            "payment_id": payment_id,
            "amount": amount,
            "endpoint": "/payment"
        }
    )

    time.sleep(random.uniform(1.1, 3.2))

    # Simulate failure
    if random.randint(1, 2) == 2:

        payment_failed_counter.add(1, {"endpoint": "/payment"})
        http_500_counter.add(1, {"endpoint": "/payment"})

        logger.error(
            "Payment failed",
            extra={
                "payment_id": payment_id,
                "amount": amount,
                "endpoint": "/payment",
                "http_status": 500,
                "reason": "Insufficient balance"
            }
        )

        raise HTTPException(
            status_code=500,
            detail="Payment failed"
        )

    duration = time.perf_counter() - start

    payment_success_counter.add(1, {"endpoint": "/payment"})
    payment_latency.record(duration, {"endpoint": "/payment"})

    logger.info(
        "Payment successful",
        extra={
            "payment_id": payment_id,
            "amount": amount,
            "endpoint": "/payment",
            "latency_ms": round(duration * 1000, 2)
        }
    )

    return {
        "status": "success",
        "payment_id": payment_id,
        "amount": amount
    }