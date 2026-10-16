from rule_manager import RuleManager

from rules.high_amount import HighAmountRule
from rules.velocity import VelocityRule
from rules.new_country import NewCountryRule
from redis_state import RedisState

def create_rule_manager() -> RuleManager:
    redis_state = RedisState()

    manager = RuleManager()

    manager.register(
        HighAmountRule(
            threshold=500
        )
    )

    manager.register(
        VelocityRule(redis_state=redis_state)
    )

    manager.register(
        NewCountryRule(redis_state=redis_state)
    )

    return manager