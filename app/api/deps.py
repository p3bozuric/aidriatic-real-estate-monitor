from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Query, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import jwt
import os
from dotenv import load_dotenv

from database.control import DatabaseControl

load_dotenv()

# Security
security = HTTPBearer(auto_error=False)

# Database Dependency
def get_db() -> DatabaseControl:
    """
    Database dependency.
    Returns a DatabaseControl instance for database operations.
    """

    return DatabaseControl()

# Authentication Dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: DatabaseControl = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            os.getenv("SECRET_KEY", "your-secret-key"),
            algorithms=["HS256"]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    # Get user from database (you'll need to add this method to DatabaseControl)
    user = db.get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# Common Query Parameters
class CommonQueryParams:
    """
    Common query parameters for list endpoints with pagination.
    """
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of items to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    ):
        self.skip = skip
        self.limit = limit