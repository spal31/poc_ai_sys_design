
from schemas import FraudAssessment


def make_policy_decision(assessment: FraudAssessment) -> dict:
    """
    Example POC policy for transactions already routed to review.

    Only low-risk, low-uncertainty assessments may become candidates
    for approval. Everything else requires review.

    Production approval also requires checks against authoritative
    rules, payment status, and any mandatory business controls.
    """
    if (
        assessment.risk_level == "LOW"
        and assessment.uncertainty == "LOW"
        and assessment.recommendation == "APPROVE_CANDIDATE"
    ):
        return {
            "decision": "APPROVE",
            "decision_source": "LLM_POLICY",
            "reason_codes": assessment.reason_codes,
            "agent_status": "VALIDATED",
        }

    return {
        "decision": "REVIEW",
        "decision_source": "LLM_POLICY",
        "reason_codes": assessment.reason_codes,
        "agent_status": "VALIDATED",
    }
