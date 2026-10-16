class FraudProcessingError(Exception):
    """Base class for fraud processing errors."""
    pass


class PermanentProcessingError(FraudProcessingError):
    """
    Error that will not be fixed by retrying.
    """
    pass


class TransientProcessingError(FraudProcessingError):
    """
    Temporary failure that may succeed if retried.
    """
    pass