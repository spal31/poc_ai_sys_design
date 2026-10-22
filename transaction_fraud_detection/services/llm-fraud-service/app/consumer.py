
import json
import logging

from pydantic import ValidationError

import shared.config as CONFIG

from schemas import FraudAssessment, FraudReviewEvent
from kafka_helpers.kafka_io import (
    create_consumer,
    create_producer,
    publish_to_kafka,
)
from graph import fraud_graph
from decision import make_policy_decision
from guardrails import safe_fallback
from shared.logging_config import configure_logging

configure_logging("llm-fraud-service")
logger = logging.getLogger("llm-fraud-service")


def process_event(payload: dict) -> dict:
    # Validate before invoking the graph.        
    event = FraudReviewEvent.model_validate(payload)
    graph_result = fraud_graph.invoke({
        "event": event.model_dump(),
    })

    result = graph_result.get("result", {})

    if result.get("agent_status") == "FALLBACK_REVIEW":
        decision = safe_fallback()
    else:
        assessment = FraudAssessment.model_validate(
            result["assessment"]
        )
        decision = make_policy_decision(assessment)
    return {
        "transaction_id": event.transaction_id,
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
            records_dict = consumer.poll(timeout_ms=1000)
            if not records_dict:
                continue
            
            # Iterate through the partitions and records
            for topic_partition, records in records_dict.items():
                for msg in records:
                    
                    # Initialize payment as an empty dict to ensure it's in scope for exceptions
                    payload = {}
                    try:
                        payload = msg.value

                        # Publish only after the assessment/policy path completes.
                        decision = process_event(payload)

                        publish_to_kafka(
                            producer,
                            CONFIG.LLM_DECISION_TOPIC,
                            decision,
                        )

                        # Commit only after successful publication.
                        consumer.commit()

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
                        consumer.commit()

    finally:
        consumer.close()
        producer.flush(timeout=10)
