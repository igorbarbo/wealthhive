"""
Custom exceptions for the application
"""


class WealthHiveException(Exception):
    """Base exception"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(WealthHiveException):
    """Resource not found"""
    def __init__(self, resource: str, identifier: str = None):
        msg = f"{resource} not found"
        if identifier:
            msg += f": {identifier}"
        super().__init__(msg, status_code=404)


class ValidationException(WealthHiveException):
    """Validation error"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class AuthenticationException(WealthHiveException):
    """Authentication failed"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationException(WealthHiveException):
    """Not authorized"""
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status_code=403)


class ExternalAPIException(WealthHiveException):
    """External API error"""
    def __init__(self, service: str, message: str):
        super().__init__(f"External API error ({service}): {message}", status_code=502)


class MLModelException(WealthHiveException):
    """ML model error"""
    def __init__(self, model_id: str, message: str):
        super().__init__(f"ML model error ({model_id}): {message}", status_code=500)
