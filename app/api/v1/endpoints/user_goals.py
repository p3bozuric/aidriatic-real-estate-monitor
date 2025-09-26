from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
import pandas as pd

from app.api.deps import get_db, get_current_user, CommonQueryParams
from app.database.control import DatabaseControl
from app.api.v1.models import (
    UserGoalCreate,
    UserGoalUpdate,
    UserGoalResponse
)

router = APIRouter()

# Insert User goals
@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_user_goal(
    goal_data: UserGoalCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: DatabaseControl = Depends(get_db)
):
    """
    Create a new user goal.
    """
    try:
        # Prepare data for database
        user_goal_data = {
            "user_id": current_user["id"],
            "transaction_type": goal_data.transaction_type,
            "property_types": goal_data.property_types,
            "min_price": goal_data.min_price,
            "max_price": goal_data.max_price,
            "min_m2": goal_data.min_m2,
            "max_m2": goal_data.max_m2,
            "location_counties": goal_data.location_counties,
            "cities": goal_data.cities,
            "description": goal_data.description
        }

        success = db.insert_user_goal(user_goal_data)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user goal"
            )

        return {
            "message": "User goal created successfully",
            "user_id": current_user["id"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user goal: {str(e)}"
        )

# Update User goals
@router.put("/{goal_id}", response_model=Dict[str, Any])
async def update_user_goal(
    goal_id: int,
    goal_data: UserGoalUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: DatabaseControl = Depends(get_db)
):
    """
    Update an existing user goal.
    """
    try:
        # Verify goal belongs to current user
        user_goals_df = db.get_user_goals_dataframe(current_user["id"])
        if user_goals_df.empty or goal_id not in user_goals_df['id'].values:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User goal not found or doesn't belong to current user"
            )

        # Prepare update data (only include non-None values)
        update_data = {}
        for field, value in goal_data.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )

        success = db.update_user_goal(goal_id, update_data)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user goal"
            )

        return {
            "message": "User goal updated successfully",
            "goal_id": goal_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user goal: {str(e)}"
        )

# Get User goals
@router.get("/", response_model=List[UserGoalResponse])
async def get_user_goals(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: DatabaseControl = Depends(get_db),
    common: CommonQueryParams = Depends()
):
    """
    Get all user goals for the current user.
    """
    try:
        user_goals_df = db.get_user_goals_dataframe(current_user["id"])

        if user_goals_df.empty:
            return []

        # Convert DataFrame to list of dictionaries
        goals_list = user_goals_df.to_dict('records')

        # Apply pagination
        start_idx = common.skip
        end_idx = start_idx + common.limit
        paginated_goals = goals_list[start_idx:end_idx]

        # Convert timestamps to strings and ensure proper formatting
        for goal in paginated_goals:
            goal['created_at'] = str(goal.get('created_at', ''))
            goal['updated_at'] = str(goal.get('updated_at', ''))

        return paginated_goals

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user goals: {str(e)}"
        )

@router.get("/{goal_id}", response_model=UserGoalResponse)
async def get_user_goal(
    goal_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: DatabaseControl = Depends(get_db)
):
    """
    Get a specific user goal by ID.
    """
    try:
        user_goals_df = db.get_user_goals_dataframe(current_user["id"])

        if user_goals_df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User goal not found"
            )

        # Filter for specific goal
        goal_row = user_goals_df[user_goals_df['id'] == goal_id]

        if goal_row.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User goal not found"
            )

        goal_dict = goal_row.iloc[0].to_dict()
        goal_dict['created_at'] = str(goal_dict.get('created_at', ''))
        goal_dict['updated_at'] = str(goal_dict.get('updated_at', ''))

        return goal_dict

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user goal: {str(e)}"
        )

# Delete User goals
@router.delete("/{goal_id}", response_model=Dict[str, Any])
async def delete_user_goal(
    goal_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: DatabaseControl = Depends(get_db)
):
    """
    Delete a specific user goal.
    """
    try:
        # Verify goal belongs to current user
        user_goals_df = db.get_user_goals_dataframe(current_user["id"])
        if user_goals_df.empty or goal_id not in user_goals_df['id'].values:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User goal not found or doesn't belong to current user"
            )

        success = db.remove_user_goal(goal_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user goal"
            )

        return {
            "message": "User goal deleted successfully",
            "goal_id": goal_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user goal: {str(e)}"
        )