"""
Authentication routes with rate limiting
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from loguru import logger

from api.models.auth import UserCreate, UserLogin, UserResponse, Token
from api.models.database import User
from api.utils.database import get_db_session
from api.utils.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_admin
)
from api.utils.rate_limiter import limiter
from api.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("10/hour")
async def register(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db_session)
):
    """
    Register a new user (rate limited: 10/hour)
    """
    # Check if username exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        is_admin=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"New user registered: {db_user.username}")
    
    return db_user


@router.post("/login", response_model=Token)
@limiter.limit("20/hour")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session)
):
    """
    Login and get access token (rate limited: 20/hour)
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.Uaccess_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user.username}")
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
@limiter.limit("100/minute")
async def get_current_user_info(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information (rate limited: 100/minute)
    """
    return current_user


@router.put("/me", response_model=UserResponse)
@limiter.limit("30/hour")
async def update_current_user(
    request: Request,
    full_name: str = None,
    email: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Update current user profile (rate limited: 30/hour)
    """
    if full_name:
        current_user.full_name = full_name
    
    if email:
        # Check if email is already taken
        existing = db.query(User).filter(
            User.email == email,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        current_user.email = email
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/users", response_model=list[UserResponse])
@limiter.limit("50/minute")
async def list_users(
    request: Request,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db_session)
):
    """
    List all users (admin only, rate limited: 50/minute)
    """
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users


@router.put("/users/{user_id}/password")
@limiter.limit("10/hour")
async def reset_user_password(
    request: Request,
    user_id: int,
    new_password: str,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db_session)
):
    """
    Reset user password (admin only, rate limited: 10/hour)
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.hashed_password = get_password_hash(new_password)
    
    db.commit()
    
    logger.info(f"Admin {current_user.username} reset password for user {user.username}")
    
    return {"message": f"Password reset for user {user.username}"}
