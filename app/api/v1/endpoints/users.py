from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from app.api.deps import get_db, get_current_user
from app.database.control import DatabaseControl, PasswordService
from app.api.v1.models import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    LoginResponse,
    MessageResponse
)

load_dotenv()

router = APIRouter()
security = HTTPBearer(auto_error=False)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY", "your-secret-key"), algorithm="HS256")
    return encoded_jwt

# Registration of user
@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: DatabaseControl = Depends(get_db)
):
    """
    Register a new user.
    """
    try:
        # Check if user already exists
        existing_user = db.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Prepare user data for database
        user_dict = {
            "email": user_data.email,
            "username": user_data.username,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "password": user_data.password
        }

        success = db.insert_user(user_dict)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )

        return MessageResponse(message="User registered successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}"
        )

# Login user
@router.post("/login", response_model=LoginResponse)
async def login_user(
    user_credentials: UserLogin,
    db: DatabaseControl = Depends(get_db)
):
    """
    Login user and return JWT token.
    """
    try:
        # Get user from database
        user = db.get_user_by_username(user_credentials.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        # Verify password
        password_service = PasswordService()
        if not password_service.verify_password(user_credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated"
            )

        # Create access token
        access_token_expires = timedelta(hours=24)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )

        # Prepare user response
        user_response = UserResponse(
            id=user["id"],
            email=user["email"],
            username=user["username"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            is_active=user["is_active"],
            email_verified=user["email_verified"],
            created_at=str(user.get("created_at", "")),
            updated_at=str(user.get("updated_at", ""))
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging in: {str(e)}"
        )

# Get user details
@router.get("/me", response_model=UserResponse)
async def get_current_user_details(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get current authenticated user details.
    """
    try:
        user_response = UserResponse(
            id=current_user["id"],
            email=current_user["email"],
            username=current_user["username"],
            first_name=current_user["first_name"],
            last_name=current_user["last_name"],
            is_active=current_user["is_active"],
            email_verified=current_user["email_verified"],
            created_at=str(current_user.get("created_at", "")),
            updated_at=str(current_user.get("updated_at", ""))
        )

        return user_response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user details: {str(e)}"
        )

# Update user
@router.put("/me", response_model=MessageResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: DatabaseControl = Depends(get_db)
):
    """
    Update current authenticated user details.
    """
    try:
        # Prepare update data (only include non-None values)
        update_data = {}
        for field, value in user_data.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )

        # Handle password change validation
        if "new_password" in update_data:
            if "old_password" not in update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password required for password change"
                )

        success = db.update_user(current_user["username"], update_data)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )

        return MessageResponse(message="User updated successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )

# Remove user
@router.delete("/me", response_model=MessageResponse)
async def delete_current_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: DatabaseControl = Depends(get_db)
):
    """
    Delete current authenticated user account.
    """
    try:
        success = db.remove_user(current_user["username"])

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )

        return MessageResponse(message="User account deleted successfully")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )

# Verify user email
@router.post("/verify-email", response_model=MessageResponse)
async def verify_user_email(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: DatabaseControl = Depends(get_db)
):
    """
    Verify current user's email address.
    """
    try:
        success = db.verify_user_email(current_user["username"])

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify email"
            )

        return MessageResponse(message="Email verified successfully")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying email: {str(e)}"
        )

# Logout user
@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Logout user (client-side token invalidation).
    Note: JWT tokens are stateless, so logout is primarily handled client-side.
    In production, consider implementing a token blacklist.
    """
    return MessageResponse(message="Successfully logged out. Please remove the token from client storage.")

# Additional endpoint to check if username exists
@router.get("/check-username/{username}", response_model=Dict[str, bool])
async def check_username_availability(
    username: str,
    db: DatabaseControl = Depends(get_db)
):
    """
    Check if username is available for registration.
    """
    try:
        existing_user = db.get_user_by_username(username)
        return {"available": not bool(existing_user)}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking username: {str(e)}"
        )