class DoctorLookupError(Exception):
    """Raised when both curated and dynamic doctor lookups fail unexpectedly."""


class RuleEngineError(Exception):
    """Raised on invalid input to the Rotterdam rule engine."""
