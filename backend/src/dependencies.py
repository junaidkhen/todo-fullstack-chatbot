"""FastAPI dependencies for request validation.

Provides:
- get_validated_user: Validates user_id exists in database
"""

import logging
from fastapi import Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.database import get_session
from src.models.task import User

logger = logging.getLogger(__name__)


async def get_validated_user(
    user_id: str,
    session: AsyncSession = Depends(get_session)
) -> str:
    """
    Validate that the user_id exists in the database.

    Args:
        user_id: User ID from path parameter
        session: Database session

    Returns:
        The validated user_id

    Raises:
        HTTPException 400: If user_id is empty
        HTTPException 401: If user_id does not exist in database
    """
    # T019: Validate non-empty user_id
    if not user_id or not user_id.strip():
        logger.warning(f"Empty user_id provided")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "bad_request",
                "message": "User ID cannot be empty",
                "details": None
            }
        )

    # T020: Check user exists in database
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "unauthorized",
                "message": "User not found",
                "details": None
            }
        )

    return user_id
