"""Message model and MessageRole enum for conversation history."""
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text, Index
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .conversation import Conversation


class MessageRole(str, Enum):
    """Enum for message roles in conversation."""
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """Message entity representing a single message in a conversation."""
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(nullable=False)
    conversation_id: int = Field(
        foreign_key="conversations.id",
        nullable=False
    )
    role: MessageRole = Field(nullable=False)
    content: str = Field(sa_column=Column(Text, nullable=False))
    tool_calls: Optional[str] = Field(default=None)  # JSON-serialized tool calls
    created_at: datetime = Field(
        default=None,
        sa_column_kwargs={"server_default": func.now()}
    )

    # Relationship to conversation - disabled for async compatibility
    # conversation: Optional["Conversation"] = Relationship(back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conversation_id_created_at", "conversation_id", "created_at"),
    )
