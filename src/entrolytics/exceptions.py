"""Custom exceptions for Entrolytics SDK."""


class EntrolyticsError(Exception):
    """Base exception for Entrolytics SDK."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(EntrolyticsError):
    """Raised when API key is invalid or missing."""

    def __init__(self, message: str = "Invalid or missing API key") -> None:
        super().__init__(message, status_code=401)


class ValidationError(EntrolyticsError):
    """Raised when request data is invalid."""

    def __init__(self, message: str = "Invalid request data") -> None:
        super().__init__(message, status_code=400)


class RateLimitError(EntrolyticsError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self, message: str = "Rate limit exceeded", retry_after: int | None = None
    ) -> None:
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class NetworkError(EntrolyticsError):
    """Raised when network request fails."""

    def __init__(self, message: str = "Network request failed") -> None:
        super().__init__(message)
