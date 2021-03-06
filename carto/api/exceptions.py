"""
Exceptions which are specific to this particular application
"""
import logging
from typing import Any, Optional, Dict, List
from fastapi import HTTPException, status

# init logger
logger = logging.getLogger(__name__)

# http error 400 (bad request)
class BadRequestHTTPException(HTTPException):
    """
    class NotFoundHTTPException(fastapi.HTTPException)
    
    -  Subclass HTTPException: this will cover common-usage cases (e.g. 404 errors) with default 
       status codes & messages.
    """
    def __init__(self, message: Optional[str]="Request was badly formed. Please resend.") -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

# http error 403 (forbidden)
class ForbiddenAccessHTTPException(HTTPException):
    """
    class ForbiddenAccessHTTPException(fastapi.HTTPException)
    
    -  Subclass HTTPException: this will cover common-usage cases (e.g. 404 errors) with default 
       status codes & messages.
    """
    def __init__(self, message: Optional[str]="Access to the resource you requested is forbidden.") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)
        

# http error 404 (resource not found)
class NotFoundHTTPException(HTTPException):
    """
    class NotFoundHTTPException(fastapi.HTTPException)
    
    -  Subclass HTTPException: this will cover common-usage cases (e.g. 404 errors) with default 
       status codes & messages.
    """
    def __init__(self, message: Optional[str]="Requested resource was not found, regrettably.") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        
        