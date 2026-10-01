from rules.base import FraudRule, RuleResult


class RuleManager:

    def __init__(self):

        self._rules: dict[str, FraudRule] = {}
        self._fraud_threshold = 40

    def register(self, rule: FraudRule) -> None:

        if rule.name in self._rules:
            raise ValueError(
                f"Rule already registered: "
                f"{rule.name}"
            )

        self._rules[rule.name] = rule

    def unregister(self, rule_name: str) -> None:

        self._rules.pop(rule_name, None)

    def evaluate(
        self,
        payment: dict,
    ) -> list[RuleResult]:

        results = []

        for rule in self._rules.values():

            result = rule.evaluate(payment)

            results.append(result)

        return results

    def get_rules(self) -> list[str]:

        return list(self._rules.keys())

    FRAUD_THRESHOLD = 40


    def is_fraudulent(self, rule_results: list[dict]) -> bool:

      risk_score = sum(
        rule.score
        for rule in rule_results
        if rule.triggered
       )

      return risk_score >= self._fraud_threshold