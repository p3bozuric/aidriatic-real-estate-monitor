from typing import List, Optional
from pydantic import BaseModel, Field

class UserGoalCreate(BaseModel):
    transaction_type: str = Field(..., description="Type of transaction (buy, rent)")
    property_types: List[str] = Field(default=[], description="List of property types")
    min_price: Optional[int] = Field(default=0, ge=0, description="Minimum price")
    max_price: Optional[int] = Field(default=0, ge=0, description="Maximum price")
    min_m2: Optional[int] = Field(default=0, ge=0, description="Minimum area in m²")
    max_m2: Optional[int] = Field(default=0, ge=0, description="Maximum area in m²")
    location_counties: List[str] = Field(default=[], description="List of counties")
    cities: List[str] = Field(default=[], description="List of cities")
    description: Optional[str] = Field(default="", description="Goal description")

class UserGoalUpdate(BaseModel):
    transaction_type: Optional[str] = Field(None, description="Type of transaction")
    property_types: Optional[List[str]] = Field(None, description="List of property types")
    min_price: Optional[int] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[int] = Field(None, ge=0, description="Maximum price")
    min_m2: Optional[int] = Field(None, ge=0, description="Minimum area in m²")
    max_m2: Optional[int] = Field(None, ge=0, description="Maximum area in m²")
    location_counties: Optional[List[str]] = Field(None, description="List of counties")
    cities: Optional[List[str]] = Field(None, description="List of cities")
    description: Optional[str] = Field(None, description="Goal description")

class UserGoalResponse(BaseModel):
    id: int
    user_id: int
    transaction_type: str
    property_types: List[str]
    min_price: int
    max_price: int
    min_m2: int
    max_m2: int
    location_counties: List[str]
    cities: List[str]
    description: str
    created_at: str
    updated_at: str