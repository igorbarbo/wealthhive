"""
User management endpoints
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db, require_admin
from infrastructure.database.repositories.user_repository import UserRepository

router = APIRouter()


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get current user info"""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(UUID(current_user["id"]))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


@router.put("/me", response_model=dict)
async def update_current_user(
    full_name: str = None,
    email: str = None,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update current user info"""
    user_repo = UserRepository(db)
    user = await user_repo.update(
        user_id=UUID(current_user["id"]),
        full_name=full_name,
        email=email,
    )
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "message": "User updated successfully",
    }


@router.get("/", response_model=List[dict])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List all users (admin only)"""
    user_repo = UserRepository(db)
    users = await user_repo.get_all(skip=skip, limit=limit)
    
    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
        }
        for user in users
    ]


@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: UUID,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get user by ID (admin only)"""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: UUID,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Delete user (admin only)"""
    user_repo = UserRepository(db)
    await user_repo.delete(user_id)
    
    return {"message": "User deleted successfully"}
