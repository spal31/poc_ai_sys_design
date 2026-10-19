from rules.base import FraudRule, RuleResult


class NewCountryRule(FraudRule):

    def __init__(self, redis_state):
        self.redis_state = redis_state

    @property
    def name(self) -> str:
      return "NEW_COUNTRY"

    def evaluate(self, payment):

        countries = self.redis_state.get_customer_countries(
            payment["customer_id"]
        )
        triggered = countries and payment["country"] not in countries

        return RuleResult(
            rule_name=self.name,
        
            triggered=triggered,
        
            score=20 if triggered else 0,
        
            reason=(
                        f"Country has changed "
                        f" to "
                        f"{payment["country"]}"
                    ),
        
                    metadata={
                        "previous_country":
                           "",
        
                        "current_country":
                           payment["country"],
                    },
                )