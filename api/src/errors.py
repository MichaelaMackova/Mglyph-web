from fastapi import status, HTTPException
from pydantic.dataclasses import dataclass
from enum import IntEnum
from typing import Dict
from fastapi.responses import JSONResponse


class ErrorCode(IntEnum):
    """Enumeration of custom error codes for MGlyph API."""
    GENERIC_ERROR = 1000 # Default generic error code for unspecified errors
    # NOT FOUND errors (100-199)
    NOT_FOUND_BASE = 100 # Base code for not found errors
    NOT_FOUND_LOGGED_IN_USER = 101 # Specific code for not found error related to logged-in user
    NOT_FOUND_ID = 102 # Specific code for not found error related to a specific ID (e.g., user ID, challenge ID)
    NOT_FOUND_SEARCH_RESULT = 103 # Specific code for not found error related to search results
    # BAD REQUEST errors (200-399)
    BAD_REQUEST_BASE = 200 # Base code for bad request errors
    BAD_REQUEST_CREATE_USER_USERNAME_TAKEN = 201 # Specific code for bad request error when trying to create a user with a username that is already taken
    BAD_REQUEST_CREATE_USER_EMAIL_TAKEN = 202 # Specific code for bad request error when trying to create a user with an email that is already taken
    BAD_REQUEST_CREATE_USER_GOOGLE_SUB_TAKEN = 203 # Specific code for bad request error when trying to create a user with a Google sub that is already taken
    BAD_REQUEST_INVALID_CREDENTIALS = 204 # Specific code for bad request error when provided credentials are invalid
    BAD_REQUEST_CREATE_CHALLENGE_NAME_TAKEN = 205 # Specific code for bad request error when trying to create a challenge with a name that is already taken
    BAD_REQUEST_ALREADY_DONE = 206 # Specific code for bad request error when trying to perform an action that has already been done (e.g., adding a solver to a challenge when they are already a solver)
    BAD_REQUEST_DELETE_CONFLICT = 207 # Specific code for bad request error when trying to delete a resource that cannot be deleted due to existing dependencies (e.g., deleting a challenge that has assigned malleable glyphs)
    # UNAUTHORIZED errors (400-499)
    UNAUTHORIZED_BASE = 400 # Base code for unauthorized errors
    UNAUTHORIZED_INVALID_TOKEN = 401 # Specific code for unauthorized access due to invalid token
    UNAUTHORIZED_EXPIRED_TOKEN = 402 # Specific code for unauthorized access due to expired token
    UNAUTHORIZED_MISSING_TOKEN = 403 # Specific code for unauthorized access due to missing token
    # FORBIDDEN errors (500-599)
    FORBIDDEN_BASE = 500 # Base code for forbidden errors
    FORBIDDEN_NOT_ADMIN = 501 # Specific code for forbidden access due to lack of admin privileges




class MGlyphApiError(Exception):
    """Base class for all MGlyph API errors."""

    @dataclass
    class ErrorResponseModel:
        """Model for custom error responses."""
        err_code: int
        detail: str

    http_code : int = status.HTTP_500_INTERNAL_SERVER_ERROR
    https_response_description : str = "Internal Server Error"
    err_code : int = ErrorCode.GENERIC_ERROR

    def __init__(self, message: str, http_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, err_code: int = ErrorCode.GENERIC_ERROR):
        self.http_code = http_code
        self.err_code = err_code
        super().__init__(message)

    class HTTPException(HTTPException):
        """ Custom HTTPException that includes the MGlyphApiError details with custom response format.
        
        Note: If not using 'headers' parameter, acts the same as raising the MGlyphApiError directly."""
        def __init__(self, error: 'MGlyphApiError', headers: Dict[str, str] | None = None):
            super().__init__(
                status_code=error.http_code, 
                detail=error.ErrorResponseModel(err_code=error.err_code, detail=str(error)).__dict__,
                headers=headers
            )

    @classmethod
    def response_dict(cls) -> dict:
        """Utility method to create a dictionary used in specifying possible FastAPI route responses."""
        return {
            "description": cls.https_response_description,
            "model": cls.ErrorResponseModel
        }



async def MGlyphApiError_exception_handler(request, exc : MGlyphApiError):
    content = exc.ErrorResponseModel(err_code=exc.err_code, detail=str(exc)).__dict__
    return JSONResponse(content, status_code=exc.http_code)

async def MGlyphApiError_http_exception_handler(request, exc : MGlyphApiError.HTTPException):
    content = exc.detail
    return JSONResponse(content, status_code=exc.status_code, headers=exc.headers)




class NotFoundError(MGlyphApiError):
    """Raised when a requested resource is not found."""

    http_code : int = status.HTTP_404_NOT_FOUND
    https_response_description : str = "Not Found"
    err_code : int = ErrorCode.NOT_FOUND_BASE

    def __init__(self, resource_info: str, error_code: int = ErrorCode.NOT_FOUND_BASE):
        super().__init__(f"{resource_info} not found.", http_code=self.http_code, err_code=error_code)



class BadRequestError(MGlyphApiError):
    """Raised when the client sends a bad request."""

    http_code : int = status.HTTP_400_BAD_REQUEST
    https_response_description : str = "Bad Request"
    err_code : int = ErrorCode.BAD_REQUEST_BASE

    def __init__(self, message: str, error_code: int = ErrorCode.BAD_REQUEST_BASE):
        super().__init__(message, http_code=self.http_code, err_code=error_code)



class UnauthorizedError(MGlyphApiError):
    """Raised when the client is unauthorized to access a resource."""

    http_code : int = status.HTTP_401_UNAUTHORIZED
    https_response_description : str = "Unauthorized"
    err_code : int = ErrorCode.UNAUTHORIZED_BASE

    def __init__(self, message: str = "Unauthorized access.", error_code: int = ErrorCode.UNAUTHORIZED_BASE):
        super().__init__(message, http_code=self.http_code, err_code=error_code)



class ForbiddenError(MGlyphApiError):
    """Raised when the client is forbidden from accessing a resource."""

    http_code : int = status.HTTP_403_FORBIDDEN
    https_response_description : str = "Forbidden"
    err_code : int = ErrorCode.FORBIDDEN_BASE

    def __init__(self, message: str = "Forbidden access.", error_code: int = ErrorCode.FORBIDDEN_BASE):
        super().__init__(message, http_code=self.http_code, err_code=error_code)