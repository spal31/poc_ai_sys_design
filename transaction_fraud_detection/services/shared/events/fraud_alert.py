from datetime import datetime


def create_fraud_alert(
    payment: dict,
    rule_results: list[dict],
) -> dict:

    triggered_rules = [
        rule.rule_name
        for rule in rule_results
        if rule.triggered
    ]

    risk_score = sum(
        rule.score
        for rule in rule_results
        if rule.triggered
    )

    return {
        "event_type": "FRAUD_ALERT",

        "alert_id":
            f"alert-{payment['transaction_id']}",

        "transaction_id":
            payment["transaction_id"],

        "customer_id":
            payment["customer_id"],

        "amount":
            payment["amount"],

        "currency":
            payment["currency"],

        "risk_score":
            risk_score,

        "triggered_rules":
            triggered_rules,

        "created_at":
            datetime.now().astimezone().isoformat(),
    }