
from typing import Literal, List

from pydantic import BaseModel, ConfigDict, Field


class FraudReviewEvent(BaseModel):
    # model_config = ConfigDict(extra="forbid")

    transaction_id: str = Field(min_length=1, max_length=128)

    risk_score: int = Field(gt=0, le=100)

    #amount: float = Field(gt=0, le=100_000_000)

    customer_id: str = Field(min_length=1, max_length=128)

    llm_review_required: bool

    triggered_rules: list[str] = Field(max_items=20)

    llm_routing_reason: str = Field(min_length=1, max_length=128)


class FraudAssessment(BaseModel):
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]

    recommendation: Literal[
        "APPROVE_CANDIDATE",
        "REVIEW",
        "DECLINE_CANDIDATE",
    ]

    reason_codes: List[str] = Field(..., max_items=10)
    evidence: List[str] = Field(..., max_items=10)

    uncertainty: Literal["LOW", "MEDIUM", "HIGH"]



class FraudDecisionEvent(BaseModel):
    transaction_id: str

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
