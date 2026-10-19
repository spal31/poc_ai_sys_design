from collections import defaultdict, deque
from datetime import datetime, timedelta

from rules.base import FraudRule, RuleResult

class VelocityRule(FraudRule):

    def __init__(self, redis_state):
        self.redis_state = redis_state
        self.window_seconds = 60

    @property
    def name(self) -> str:
        return "HIGH_VELOCITY"

    def evaluate(self, payment):

        count = self.redis_state.get_transaction_count(
            payment["customer_id"],
            window_seconds=self.window_seconds
        )


        return RuleResult(
                    rule_name=self.name,
        
                    triggered=count>=5,
        
                    score=30 if count>=5 else 0,
        
                    reason=(
                        f"{count} transactions in "
                        f"{self.window_seconds} seconds"
                    ),
        
                    metadata={
                        "transaction_count": count,
                        "window_seconds": self.window_seconds,
                    },
                )