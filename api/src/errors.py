from fastapi import status, HTTPException
from pydantic.dataclasses import dataclass



class MGlyphApiError(Exception):
    """Base class for all MGlyph API errors."""

    http_code : int = status.HTTP_500_INTERNAL_SERVER_ERROR
    https_response_description : str = "Internal Server Error"

    def __init__(self, message: str, http_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.http_code = http_code
        super().__init__(message)

    @dataclass
    class ErrorResponseModel:
        """Model for custom error responses."""
        detail: str

    class HTTPException(HTTPException):
        """Custom HTTPException that includes the MGlyphApiError details."""
        def __init__(self, error: 'MGlyphApiError'):
            super().__init__(status_code=error.http_code, detail=str(error))

    @classmethod
    def response_dict(cls) -> dict:
        """Utility method to create a dictionary used in specifying possible FastAPI route responses."""
        return {
            "description": cls.https_response_description,
            "model": cls.ErrorResponseModel
        }





class NotFoundError(MGlyphApiError):
    """Raised when a requested resource is not found."""

    http_code : int = status.HTTP_404_NOT_FOUND
    https_response_description : str = "Not Found"

    def __init__(self, resource_info: str):
        super().__init__(f"{resource_info} not found.", http_code=self.http_code)




