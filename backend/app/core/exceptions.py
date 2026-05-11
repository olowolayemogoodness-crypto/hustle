class MLModelError(Exception):
    """Raised when the machine learning model cannot be used."""


class PredictionError(Exception):
    """Raised when a prediction operation fails."""


class ValidationError(Exception):
    """Raised when request or feature validation fails."""
