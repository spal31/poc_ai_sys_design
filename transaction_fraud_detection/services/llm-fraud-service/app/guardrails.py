
from pydantic import ValidationError

from schemas import FraudReviewEvent, FraudAssessment

from typing import Any, Dict, List, Literal


ALLOWED_REASON_CODES = {
    "NEW_DEVICE",
    "UNUSUAL_AMOUNT",
    "REPEATED_FAILURES",
    "VELOCITY_ANOMALY",
    "CONTEXT_MISMATCH",
    "INSUFFICIENT_EVIDENCE",
}


def validate_review_event(payload: Any) -> FraudReviewEvent:
    """Reject malformed or unexpected Kafka events with exact structure and business logic checks."""
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary")

    try:
        event = FraudReviewEvent.model_validate(payload)
        
        # Cross-field Integrity Check
        if event.risk_score > 80 and not event.llm_review_required:
            raise ValueError(f"Consistency conflict: risk_score is high ({event.risk_score}) but llm_review_required is False.")
            
        return event

    except (ValidationError, ValueError) as e:
        raise


def validate_assessment(payload: Any) -> FraudAssessment | Dict[str, Any]:
    """Validate model output before downstream evaluation. Falls back gracefully on failure."""

    try:
        assessment = FraudAssessment.model_validate(payload)
        
        # 1. Strict Reason Code Enforcement against Allowed Set
        invalid_codes = set(assessment.reason_codes) - ALLOWED_REASON_CODES
        if invalid_codes:
            raise ValueError(f"Unauthorized reason codes detected: {invalid_codes}")

        # 2. Risk Matrix Alignment (Preventing hallucinated contradictions)
        if assessment.risk_level == "HIGH" and assessment.recommendation == "APPROVE_CANDIDATE":
            raise ValueError("Critical Policy Conflict: Model attempted to APPROVE a HIGH risk assessment.")

        if assessment.risk_level == "LOW" and assessment.recommendation == "DECLINE_CANDIDATE":
            raise ValueError("Consistency Conflict: Model attempted to DECLINE a LOW risk assessment.")

        return assessment

    except (ValidationError, ValueError) as e:
        raise


def safe_fallback() -> dict:
    """Return a non-approving result for the caller's policy layer."""
    return {
        "decision": "REVIEW",
        "decision_source": "FALLBACK",
        "reason_codes": ["INSUFFICIENT_EVIDENCE"],
        "agent_status": "FALLBACK_REVIEW",
    }
