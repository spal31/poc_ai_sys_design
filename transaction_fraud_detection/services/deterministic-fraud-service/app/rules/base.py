from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class RuleResult:
    rule_name: str
    triggered: bool
    score: int
    reason: str
    metadata: dict[str, Any]


class FraudRule(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def evaluate(self, payment: dict) -> RuleResult:
        pass