from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    password: str = Field(..., min_length=6, description="Password")

class UserLogin(BaseModel):
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Last name")
    old_password: Optional[str] = Field(None, description="Current password (required for password change)")
    new_password: Optional[str] = Field(None, min_length=6, description="New password")

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    email_verified: bool
    created_at: str
    updated_at: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class MessageResponse(BaseModel):
    message: str