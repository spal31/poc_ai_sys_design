from rules.base import FraudRule, RuleResult


class NewCountryRule(FraudRule):

    def __init__(self):
        self.last_country = {}

    @property
    def name(self) -> str:
        return "NEW_COUNTRY"

    def evaluate(self, payment: dict) -> RuleResult:

        customer_id = payment["customer_id"]

        current_country = payment["country"]

        previous_country = self.last_country.get(
            customer_id
        )

        self.last_country[
            customer_id
        ] = current_country

        triggered = (
            previous_country is not None
            and previous_country != current_country
        )

        return RuleResult(
            rule_name=self.name,

            triggered=triggered,

            score=20 if triggered else 0,

            reason=(
                f"Country changed from "
                f"{previous_country} to "
                f"{current_country}"
            ),

            metadata={
                "previous_country":
                    previous_country,

                "current_country":
                    current_country,
            },
        )