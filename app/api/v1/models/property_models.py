from typing import List, Dict, Any
from pydantic import BaseModel

class PropertyResponse(BaseModel):
    id_int: int
    property_type: str
    transaction_type: str
    county: str
    municipality: str
    place: str
    id: str
    price: int
    currency: str
    area: int
    number_of_rooms: int
    number_of_parking_spaces: int
    view: str
    garden: str
    number_of_bathrooms: int
    garage: str
    near_transport: str
    near_beach: str
    floor: int
    elevator: str
    croatian_description: str
    english_description: str
    german_description: str

class PropertyListResponse(BaseModel):
    properties: List[PropertyResponse]
    total_count: int
    page_info: Dict[str, Any]

class UserGoalMatchResponse(BaseModel):
    user_goals: List[Dict[str, Any]]
    matching_properties: Dict[str, PropertyResponse]
    total_matches: int