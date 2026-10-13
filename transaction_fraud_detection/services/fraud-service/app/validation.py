from errors.exceptions import (
    PermanentProcessingError,
    TransientProcessingError
)


class Validation:

    def validate(self, payment):

        if "transaction_id" not in payment:
            raise PermanentProcessingError(
                "transaction_id is missing"
            )

        if "customer_id" not in payment:
            raise PermanentProcessingError(
                "customer_id is missing"
            )

        if "amount" not in payment:
            raise PermanentProcessingError(
                "amount is missing"
            )

        if float(payment["amount"]) <= 0:
            raise PermanentProcessingError(
                "amount must be greater than zero"
            )