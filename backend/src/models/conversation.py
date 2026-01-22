"""Conversation model for chat session management."""
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .message import Message


class Conversation(SQLModel, table=True):
    """Conversation entity representing a chat session for a user."""
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(
        default=None,
        sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        default=None,
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": func.now()
        }
    )

    # Relationship to messages - disabled for async compatibility
    # messages: List["Message"] = Relationship(
    #     back_populates="conversation",
    #     sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    # )
