from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional
from src.auth.jwt import get_current_user
from src.database import get_session
from src.models.task import User
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import hashlib
import os
import jwt
from datetime import datetime, timedelta

router = APIRouter()

class AuthRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    user_id: str
    email: str
    token: str
    message: str

# Secret key for JWT generation (should match the one used for validation)
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "default-secret-key-change-in-production")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Simple password hashing for demo purposes."""
    return hashlib.sha256(password.encode()).hexdigest()


@router.post("/signup")
async def signup(
    auth_request: AuthRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Signup endpoint - creates a new user in the database and returns a JWT token.
    """
    # Check if user already exists
    query = select(User).where(User.email == auth_request.email)
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Create user ID
    user_id = f"user_{auth_request.email.split('@')[0]}_{int(datetime.utcnow().timestamp())}"

    # Create user in database
    user = User(
        id=user_id,
        email=auth_request.email,
        password_hash=hash_password(auth_request.password)
    )
    session.add(user)
    await session.commit()

    # Create JWT token
    token_data = {
        "sub": user_id,  # Subject (user ID)
        "email": auth_request.email,
        "exp": datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
        "iat": datetime.utcnow(),  # Issued at
    }

    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "user_id": user_id,
        "email": auth_request.email,
        "token": token,
        "message": "Account created successfully"
    }


@router.post("/signin")
async def signin(
    auth_request: AuthRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Signin endpoint - authenticates user and returns a JWT token.
    Creates user if not exists for easy development/testing.
    """
    if len(auth_request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Look up user by email
    query = select(User).where(User.email == auth_request.email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user:
        # User exists - verify password
        if user.password_hash != hash_password(auth_request.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        user_id = user.id
    else:
        # User doesn't exist - create for easy development
        user_id = f"user_{auth_request.email.split('@')[0]}_{int(datetime.utcnow().timestamp())}"
        new_user = User(
            id=user_id,
            email=auth_request.email,
            password_hash=hash_password(auth_request.password)
        )
        session.add(new_user)
        await session.commit()

    # Create JWT token
    token_data = {
        "sub": user_id,  # Subject (user ID)
        "email": auth_request.email,
        "exp": datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
        "iat": datetime.utcnow(),  # Issued at
    }

    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "user_id": user_id,
        "email": auth_request.email,
        "token": token,
        "message": "Signed in successfully"
    }

@router.post("/signout")
async def signout():
    """
    Signout endpoint - in a real implementation, this might invalidate tokens.
    """
    return {"message": "Signed out successfully"}

@router.get("/session")
async def get_session(current_user_id: str = Depends(get_current_user)):
    """
    Get current session information using JWT validation.
    """
    return {
        "user_id": current_user_id,
        "message": "Valid session"
    }