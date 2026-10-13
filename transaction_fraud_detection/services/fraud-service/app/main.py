from consumer import FraudConsumer
from service import FraudService
from rules.rule_registry import create_rule_manager

rule_manager = create_rule_manager()

fraud_service = FraudService(rule_manager=rule_manager)

consumer = FraudConsumer(fraud_service=fraud_service)
consumer.run()