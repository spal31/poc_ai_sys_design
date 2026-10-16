from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Protocol
from shared.errors.exceptions import PermanentProcessingError


class ValidationErrorDetail:
    def __init__(self, field: str, message: str, code: str):
        self.field = field
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return f"[{self.code}] {self.field}: {self.message}"


class PaymentRule(Protocol):
    def validate(self, payment: Dict[str, Any]) -> List[ValidationErrorDetail]:
        ...


class RequiredFieldsRule:
    def __init__(self, fields: List[str]):
        self.fields = fields

    def validate(self, payment: Dict[str, Any]) -> List[ValidationErrorDetail]:
        errors = []
        for field in self.fields:
            val = payment.get(field)
            if val is None or (isinstance(val, str) and not val.strip()):
                errors.append(
                    ValidationErrorDetail(
                        field=field,
                        message=f"{field} is missing or empty",
                        code="VAL_MISSING_FIELD",
                    )
                )
        return errors


class PositiveAmountRule:
    def validate(self, payment: Dict[str, Any]) -> List[ValidationErrorDetail]:
        if "amount" not in payment or payment["amount"] is None:
            return []
        try:
            val = Decimal(str(payment["amount"]))
            if val <= Decimal("0"):
                return [
                    ValidationErrorDetail(
                        field="amount",
                        message="amount must be greater than zero",
                        code="VAL_INVALID_AMOUNT",
                    )
                ]
        except (InvalidOperation, ValueError, TypeError):
            return [
                ValidationErrorDetail(
                    field="amount",
                    message="amount must be a valid numeric value",
                    code="VAL_NOT_A_NUMBER",
                )
            ]
        return []


class MethodSpecificRule:
    """Example extension for payment-method specific checks (e.g., card or UPI)."""
    def __init__(self, method_name: str, required_subfields: List[str]):
        self.method_name = method_name
        self.required_subfields = required_subfields

    def validate(self, payment: Dict[str, Any]) -> List[ValidationErrorDetail]:
        if payment.get("payment_method") != self.method_name:
            return []
        
        details = payment.get("payment_details", {})
        if not isinstance(details, dict):
            return [
                ValidationErrorDetail(
                    field="payment_details",
                    message="payment_details must be a dictionary",
                    code="VAL_INVALID_DETAILS_STRUCT",
                )
            ]

        errors = []
        for sf in self.required_subfields:
            if sf not in details or details[sf] is None:
                errors.append(
                    ValidationErrorDetail(
                        field=f"payment_details.{sf}",
                        message=f"{sf} is missing for {self.method_name}",
                        code="VAL_MISSING_METHOD_FIELD",
                    )
                )
        return errors


class Validation:
    def __init__(self, rules: List[PaymentRule] | None = None):
        self.rules: List[PaymentRule] = rules if rules is not None else [
            RequiredFieldsRule(["transaction_id", "customer_id", "amount"]),
            PositiveAmountRule(),
        ]

    def add_rule(self, rule: PaymentRule) -> "Validation":
        self.rules.append(rule)
        return self

    def validate(self, payment: Dict[str, Any]) -> None:
        all_errors: List[ValidationErrorDetail] = []
        for rule in self.rules:
            all_errors.extend(rule.validate(payment))

        if all_errors:
            error_summary = "; ".join(str(e) for e in all_errors)
            raise PermanentProcessingError(error_summary)
