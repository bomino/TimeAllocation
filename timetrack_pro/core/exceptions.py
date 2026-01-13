"""
Custom exception handling for TimeTrack Pro API.
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status


class BusinessLogicError(APIException):
    """Base exception for business logic violations."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A business logic error occurred.'
    default_code = 'business_error'

    def __init__(self, detail=None, code=None):
        super().__init__(detail, code)
        self.error_code = code or self.default_code


class AuthenticationError(APIException):
    """Authentication-related errors."""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication failed.'
    default_code = 'AUTH_001'


class AuthorizationError(APIException):
    """Authorization-related errors."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'AUTH_003'


class ValidationError(APIException):
    """Validation errors with structured details."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Validation failed.'
    default_code = 'VAL_001'

    def __init__(self, detail=None, code=None, field_errors=None):
        super().__init__(detail, code)
        self.error_code = code or self.default_code
        self.field_errors = field_errors or []


class TimesheetLockedError(BusinessLogicError):
    """Cannot modify a locked timesheet."""
    default_detail = 'Cannot modify a locked timesheet.'
    default_code = 'BIZ_001'


class ArchivedProjectError(BusinessLogicError):
    """Cannot log time to an archived project."""
    default_detail = 'Cannot log time to an archived project.'
    default_code = 'BIZ_002'


class DailyHourLimitError(BusinessLogicError):
    """Cannot exceed 24 hours per day."""
    default_detail = 'Cannot exceed 24 hours per day.'
    default_code = 'BIZ_003'


class EmptyTimesheetError(BusinessLogicError):
    """Cannot submit an empty timesheet."""
    default_detail = 'Cannot submit an empty timesheet.'
    default_code = 'BIZ_004'


class TimerActiveError(BusinessLogicError):
    """Cannot start a new timer while one is active."""
    default_detail = 'A timer is already running. Stop it before starting a new one.'
    default_code = 'BIZ_005'


def custom_exception_handler(exc, context):
    """
    Custom exception handler that formats errors consistently.

    Response format:
    {
        "success": false,
        "error": {
            "code": "ERROR_CODE",
            "message": "Human readable message",
            "details": [...]  // Optional field-level errors
        }
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_code = getattr(exc, 'error_code', getattr(exc, 'default_code', 'UNKNOWN'))

        if isinstance(exc, ValidationError) and exc.field_errors:
            details = exc.field_errors
        elif isinstance(response.data, dict) and 'detail' not in response.data:
            details = [
                {'field': field, 'message': msgs[0] if isinstance(msgs, list) else msgs}
                for field, msgs in response.data.items()
            ]
        else:
            details = []

        message = str(exc.detail) if hasattr(exc, 'detail') else str(exc)

        response.data = {
            'success': False,
            'error': {
                'code': error_code,
                'message': message,
                'details': details,
            }
        }

    return response
