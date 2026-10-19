
from dataclasses import dataclass


@dataclass
class LLMRoutingResult:
    required: bool
    reason: str


# These are routing thresholds, not final fraud thresholds.
LLM_MIN_SCORE = 20

LLM_MAX_SCORE_EXCLUSIVE = 40

# Rules that may benefit from additional contextual evidence.
CONTEXTUAL_RULES = {
    "NEW_COUNTRY",
    "HIGH_VELOCITY",
    "HIGH_AMOUNT"
}


def should_route_to_llm(
    risk_score: int,
    triggered_rules: list[str]
) -> LLMRoutingResult:
    """
    Decide whether an unresolved transaction warrants LLM analysis.

    Existing fraud rules remain authoritative.
    This function never changes the final fraud decision.
    """

    # Existing deterministic fraud threshold remains authoritative.
    if risk_score >= 40:
        return LLMRoutingResult(
            required=False,
            reason="DETERMINISTIC_FRAUD_THRESHOLD_REACHED",
        )

    # No meaningful risk signals: no need for LLM analysis.
    if risk_score < LLM_MIN_SCORE:
        return LLMRoutingResult(
            required=False,
            reason="LOW_RISK_SKIP_LLM",
        )

    # Only consider contextual analysis for the ambiguous score band.
    if risk_score < LLM_MAX_SCORE_EXCLUSIVE:
        contextual_matches = (
            set(triggered_rules) & CONTEXTUAL_RULES
        )

        if len(triggered_rules) >= 2:
            return LLMRoutingResult(
                required=True,
                reason="MULTIPLE_RISK_SIGNALS",
            )

        if contextual_matches:
            return LLMRoutingResult(
                required=True,
                reason="CONTEXTUAL_SIGNAL_REQUIRES_ANALYSIS",
            )

    return LLMRoutingResult(
        required=False,
        reason="NO_LLM_ROUTING_CRITERIA_MET",
    )
