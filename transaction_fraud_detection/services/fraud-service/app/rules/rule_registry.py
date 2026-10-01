from rule_manager import RuleManager

from rules.high_amount import HighAmountRule
from rules.velocity import VelocityRule
from rules.new_country import NewCountryRule


def create_rule_manager() -> RuleManager:

    manager = RuleManager()

    manager.register(
        HighAmountRule(
            threshold=50_000
        )
    )

    manager.register(
        VelocityRule(
            window_seconds=60,
            max_transactions=5,
        )
    )

    manager.register(
        NewCountryRule()
    )

    return manager