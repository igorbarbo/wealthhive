"""
Authentication endpoints
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.dependencies import get_db
from infrastructure.database.repositories.user_repository import UserRepository

router = APIRouter()


@router.post("/register", response_model=dict)
async def register(
    email: str,
    password: str,
    full_name: str,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Any:
    """Register new user"""
    user_repo = UserRepository(db)
    
    # Check if user exists
    existing_user = await user_repo.get_by_email(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create user
    user = await user_repo.create(
        email=email,
        password=password,
        full_name=full_name,
    )
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "message": "User created successfully",
    }


@router.post("/login", response_model=dict)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Any:
    """Login user"""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        secret_key=settings.JWT_SECRET_KEY,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        secret_key=settings.JWT_SECRET_KEY,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_token: str,
    settings: Settings = Depends(get_settings),
) -> Any:
    """Refresh access token"""
    from app.core.security import verify_token
    
    try:
        payload = verify_token(refresh_token, settings.JWT_SECRET_KEY)
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role", "user")
        
        new_access_token = create_access_token(
            data={"sub": user_id, "email": email, "role": role},
            secret_key=settings.JWT_SECRET_KEY,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
    
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post("/logout", response_model=dict)
async def logout() -> Any:
    """Logout user (client should discard tokens)"""
    return {"message": "Successfully logged out"}
