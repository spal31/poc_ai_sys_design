
from pydantic import ValidationError

from app.schemas import FraudReviewEvent, FraudAssessment


ALLOWED_REASON_CODES = {
    "NEW_DEVICE",
    "UNUSUAL_AMOUNT",
    "REPEATED_FAILURES",
    "VELOCITY_ANOMALY",
    "CONTEXT_MISMATCH",
    "INSUFFICIENT_EVIDENCE",
}


def validate_review_event(payload: dict) -> FraudReviewEvent:
    """Reject malformed or unexpected Kafka events."""
    return FraudReviewEvent.model_validate(payload)


def validate_assessment(payload: dict) -> FraudAssessment:
    """Validate model output before downstream policy evaluation."""
    assessment = FraudAssessment.model_validate(payload)

    unknown_codes = set(assessment.reason_codes) - ALLOWED_REASON_CODES

    if unknown_codes:
        raise ValueError(
            f"Unsupported reason codes: {sorted(unknown_codes)}"
        )

    if not assessment.evidence and assessment.risk_level != "LOW":
        raise ValueError(
            "Non-low risk assessments must include evidence"
        )

    # High uncertainty cannot directly support an approval.
    if (
        assessment.uncertainty == "HIGH"
        and assessment.recommendation == "APPROVE_CANDIDATE"
    ):
        raise ValueError(
            "High-uncertainty assessment cannot recommend approval"
        )

    return assessment


def safe_fallback() -> dict:
    """Return a non-approving result for the caller's policy layer."""
    return {
        "decision": "REVIEW",
        "decision_source": "FALLBACK",
        "reason_codes": ["INSUFFICIENT_EVIDENCE"],
        "agent_status": "FALLBACK_REVIEW",
    }
