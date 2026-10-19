
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class FraudReviewEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: str = Field(min_length=1, max_length=128)
    correlation_id: str = Field(min_length=1, max_length=128)

    amount: float = Field(gt=0, le=100_000_000)
    currency: str = Field(min_length=3, max_length=3)

    customer_id: str = Field(min_length=1, max_length=128)
    rule_outcome: Literal["REVIEW_REQUIRED"]
    matched_rules: list[str] = Field(max_length=20)

    # Optional signals should be included only if available
    recent_failed_attempts: int = Field(default=0, ge=0, le=1000)
    new_device: bool | None = None


class FraudAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_level: Literal["LOW", "MEDIUM", "HIGH"]

    recommendation: Literal[
        "APPROVE_CANDIDATE",
        "REVIEW",
        "DECLINE_CANDIDATE",
    ]

    reason_codes: list[str] = Field(max_length=10)
    evidence: list[str] = Field(max_length=10)

    uncertainty: Literal["LOW", "MEDIUM", "HIGH"]


class FraudDecisionEvent(BaseModel):
    transaction_id: str
    correlation_id: str

    decision: Literal[
        "APPROVE",
        "DECLINE",
        "REVIEW",
    ]

    decision_source: Literal[
        "RULE_ENGINE",
        "LLM_POLICY",
        "FALLBACK",
    ]

    reason_codes: list[str]
    agent_status: str
