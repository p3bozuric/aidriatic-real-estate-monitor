from typing import List, Dict, Any, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status, Query
import pandas as pd

from app.api.deps import get_db, get_current_user, CommonQueryParams
from app.database.control import DatabaseControl
from app.api.v1.models import (
    PropertyResponse,
    PropertyListResponse,
    UserGoalMatchResponse
)

router = APIRouter()

# List properties
@router.get("/", response_model=PropertyListResponse)
async def list_properties(
    db: DatabaseControl = Depends(get_db),
    common: CommonQueryParams = Depends(),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    property_types: Optional[List[str]] = Query(None, description="Filter by property types"),
    counties: Optional[List[str]] = Query(None, description="Filter by counties"),
    min_price: Optional[int] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[int] = Query(None, ge=0, description="Maximum price"),
    min_area: Optional[int] = Query(None, ge=0, description="Minimum area"),
    max_area: Optional[int] = Query(None, ge=0, description="Maximum area"),
    min_id: Optional[int] = Query(None, ge=0, description="Minimum property ID for pagination")
):
    """
    List properties with optional filtering and pagination.
    """
    try:
        # Get filtered property IDs
        property_ids = db.filter_properties(
            transaction_type=transaction_type,
            property_types=property_types,
            counties=counties,
            min_price=min_price,
            max_price=max_price,
            min_area=min_area,
            max_area=max_area,
            min_id=min_id
        )

        total_count = len(property_ids)

        if not property_ids:
            return PropertyListResponse(
                properties=[],
                total_count=0,
                page_info={
                    "skip": common.skip,
                    "limit": common.limit,
                    "has_more": False
                }
            )

        # Apply pagination to IDs
        paginated_ids = property_ids[common.skip:common.skip + common.limit]

        # Get property details for paginated IDs
        properties_dict = db.get_properties_by_ids(paginated_ids)

        # Convert to list of PropertyResponse objects
        properties_list = []
        for prop_id in paginated_ids:
            if str(prop_id) in properties_dict:
                properties_list.append(properties_dict[str(prop_id)])

        return PropertyListResponse(
            properties=properties_list,
            total_count=total_count,
            page_info={
                "skip": common.skip,
                "limit": common.limit,
                "returned": len(properties_list),
                "has_more": common.skip + common.limit < total_count
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing properties: {str(e)}"
        )

# Get property details
@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property_details(
    property_id: Union[int, str],
    db: DatabaseControl = Depends(get_db)
):
    """
    Get detailed information about a specific property.
    """
    try:
        property_data = db.get_property_by_id(property_id)

        if not property_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )

        return property_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting property details: {str(e)}"
        )

# Display properties matching user goals or a specific goal
@router.get("/matches/my-goals", response_model=UserGoalMatchResponse)
async def get_properties_matching_user_goals(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: DatabaseControl = Depends(get_db),
    common: CommonQueryParams = Depends(),
    goal_id: Optional[int] = Query(None, description="Filter by specific goal ID")
):
    """
    Get properties that match the current user's goals or a specific goal.
    """
    try:
        user_id = current_user.get('id')
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID not found"
            )

        # Get user goals
        user_goals_df = db.get_user_goals_dataframe(user_id)
        if user_goals_df.empty:
            return UserGoalMatchResponse(
                user_goals=[],
                matching_properties={},
                total_matches=0
            )

        # Filter by specific goal if requested
        if goal_id:
            goal_row = user_goals_df[user_goals_df['id'] == goal_id]
            if goal_row.empty:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Goal not found or doesn't belong to current user"
                )
            user_goals_df = goal_row

        all_matching_properties = {}
        processed_property_ids = set()

        # For each user goal, find matching properties
        for _, goal in user_goals_df.iterrows():
            matching_ids = db.filter_properties(
                transaction_type=goal.get('transaction_type'),
                property_types=goal.get('property_types', []),
                counties=goal.get('location_counties', []),
                min_price=goal.get('min_price'),
                max_price=goal.get('max_price'),
                min_area=goal.get('min_m2'),
                max_area=goal.get('max_m2')
            )

            if matching_ids:
                # Only get new properties to avoid duplicates
                new_ids = [pid for pid in matching_ids if pid not in processed_property_ids]
                if new_ids:
                    goal_properties = db.get_properties_by_ids(new_ids)
                    all_matching_properties.update(goal_properties)
                    processed_property_ids.update(new_ids)

        # Apply pagination to matching properties
        property_items = list(all_matching_properties.items())
        paginated_items = property_items[common.skip:common.skip + common.limit]
        paginated_properties = dict(paginated_items)

        return UserGoalMatchResponse(
            user_goals=user_goals_df.to_dict('records'),
            matching_properties=paginated_properties,
            total_matches=len(all_matching_properties)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting matching properties: {str(e)}"
        )

@router.get("/matches/goal/{goal_id}", response_model=UserGoalMatchResponse)
async def get_properties_matching_specific_goal(
    goal_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: DatabaseControl = Depends(get_db),
    common: CommonQueryParams = Depends()
):
    """
    Get properties that match a specific user goal.
    """
    return await get_properties_matching_user_goals(
        current_user=current_user,
        db=db,
        common=common,
        goal_id=goal_id
    )

@router.post("/matches/refresh/{goal_id}")
async def refresh_goal_matches(
    goal_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: DatabaseControl = Depends(get_db)
):
    """
    Refresh and store matching properties for a specific user goal.
    This endpoint will find all properties matching the goal criteria
    and store them in the user_goal_criteria_met table.
    """
    try:
        user_id = current_user.get('id')
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID not found"
            )

        # Verify goal belongs to current user
        user_goals_df = db.get_user_goals_dataframe(user_id)
        if user_goals_df.empty or goal_id not in user_goals_df['id'].values:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found or doesn't belong to current user"
            )

        # Get the specific goal
        goal_row = user_goals_df[user_goals_df['id'] == goal_id].iloc[0]

        # Find matching properties
        matching_ids = db.filter_properties(
            transaction_type=goal_row.get('transaction_type'),
            property_types=goal_row.get('property_types', []),
            counties=goal_row.get('location_counties', []),
            min_price=goal_row.get('min_price'),
            max_price=goal_row.get('max_price'),
            min_area=goal_row.get('min_m2'),
            max_area=goal_row.get('max_m2')
        )

        if matching_ids:
            # Store matching properties in user_goal_criteria_met table
            success = db.add_user_goal_criteria_met(goal_id, matching_ids)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to store matching properties"
                )

        return {
            "message": "Goal matches refreshed successfully",
            "goal_id": goal_id,
            "matching_properties_count": len(matching_ids)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing goal matches: {str(e)}"
        )