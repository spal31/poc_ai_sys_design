from collections import defaultdict, deque
from datetime import datetime, timedelta

from rules.base import FraudRule, RuleResult


class VelocityRule(FraudRule):

    def __init__(
        self,
        window_seconds: int = 60,
        max_transactions: int = 5,
    ):

        self.window_seconds = window_seconds

        self.max_transactions = max_transactions

        self.customer_transactions = defaultdict(
            deque
        )

    @property
    def name(self) -> str:
        return "HIGH_VELOCITY"

    def evaluate(self, payment: dict) -> RuleResult:

        customer_id = payment["customer_id"]

        timestamp = datetime.fromisoformat(
            payment["timestamp"]
        )

        transactions = self.customer_transactions[
            customer_id
        ]

        cutoff = timestamp - timedelta(
            seconds=self.window_seconds
        )

        while (
            transactions
            and transactions[0] < cutoff
        ):
            transactions.popleft()

        transactions.append(timestamp)

        count = len(transactions)

        triggered = (
            count > self.max_transactions
        )

        return RuleResult(
            rule_name=self.name,

            triggered=triggered,

            score=30 if triggered else 0,

            reason=(
                f"{count} transactions in "
                f"{self.window_seconds} seconds"
            ),

            metadata={
                "transaction_count": count,
                "window_seconds":
                    self.window_seconds,
            },
        )