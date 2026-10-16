from rules.base import FraudRule, RuleResult


class HighAmountRule(FraudRule):

    def __init__(self, threshold: float = 500):
        self.threshold = threshold

    @property
    def name(self) -> str:
        return "HIGH_AMOUNT"

    def evaluate(self, payment: dict) -> RuleResult:

        amount = float(payment["amount"])

        triggered = amount > self.threshold

        return RuleResult(
            rule_name=self.name,

            triggered=triggered,

            score=40 if triggered else 0,

            reason=(
                f"Amount {amount} exceeds "
                f"threshold {self.threshold}"
            ),

            metadata={
                "amount": amount,
                "threshold": self.threshold,
            },
        )