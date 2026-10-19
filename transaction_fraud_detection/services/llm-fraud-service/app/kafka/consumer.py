
import json
import logging

from pydantic import ValidationError

import shared.config as CONFIG

from app.schemas import FraudAssessment, FraudReviewEvent
from kafka_io import (
    create_consumer,
    create_producer,
    publish_to_kafka,
)
from app.graph import fraud_graph
from app.decision import make_policy_decision
from app.guardrails import safe_fallback

logger = logging.getLogger("llm-fraud-service")


def process_event(payload: dict) -> dict:
    # Validate before invoking the graph.
    event = FraudReviewEvent.model_validate(payload)

    graph_result = fraud_graph.invoke({
        "event": event.model_dump(),
    })

    result = graph_result.get("result", {})

    if result.get("status") == "FALLBACK_REVIEW":
        decision = safe_fallback()
    else:
        assessment = FraudAssessment.model_validate(
            result["assessment"]
        )
        decision = make_policy_decision(assessment)

    return {
        "transaction_id": event.transaction_id,
        "correlation_id": event.correlation_id,
        **decision,
    }


def run_consumer() -> None:
    consumer = create_consumer()
    producer = create_producer()

    consumer.subscribe([CONFIG.LLM_REVIEW_TOPIC])

    logger.info(
        "LLM fraud consumer started topic=%s",
        CONFIG.LLM_REVIEW_TOPIC,
    )

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                logger.error("Kafka consumer error: %s", msg.error())
                continue

            try:
                payload = json.loads(msg.value().decode("utf-8"))

                # Publish only after the assessment/policy path completes.
                decision = process_event(payload)

                publish_to_kafka(
                    producer,
                    CONFIG.LLM_DECISION_TOPIC,
                    decision,
                )

                # Commit only after successful publication.
                consumer.commit(message=msg, asynchronous=False)

                logger.info(
                    "Fraud assessment completed transaction_id=%s status=%s",
                    decision.get("transaction_id", "unknown"),
                    decision.get("agent_status", "unknown"),
                )

            except Exception:
                # Do not commit. The event may be redelivered.
                # Add bounded retry/backoff and a durable retry policy.
                logger.exception(
                    "LLM fraud processing failed; message not committed"
                )
                consumer.commit(message=msg, asynchronous=False)

    finally:
        consumer.close()
        producer.flush(timeout=10)
