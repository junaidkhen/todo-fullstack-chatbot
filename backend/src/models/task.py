from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field as PydanticField
from sqlalchemy import Index
from sqlalchemy.sql import func


class User(SQLModel, table=True):
    """User entity managed by auth system."""
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, nullable=False, max_length=255)
    password_hash: str = Field(nullable=False)  # In real app, this would be from auth system
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Task(SQLModel, table=True):
    """Task entity with user ownership and validation."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, nullable=False)
    title: str = Field(min_length=1, max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=5000)
    completed: bool = Field(default=False, nullable=False)
    priority: Optional[str] = Field(default="Medium", max_length=20)  # Low, Medium, High
    category: Optional[str] = Field(default=None, max_length=50)  # Work, Health, Shopping, etc.
    due_date: Optional[datetime] = Field(default=None)
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

    # Composite index for efficient user + completed queries
    __table_args__ = (
        Index("ix_tasks_user_id_completed", "user_id", "completed"),
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user-uuid-123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "priority": "Medium",
                "category": "Shopping",
                "due_date": "2024-12-30T00:00:00"
            }
        }

# Pydantic models for API requests/responses
class TaskCreate(BaseModel):
    title: str = PydanticField(min_length=1, max_length=200, description="Task title")
    description: Optional[str] = PydanticField(default=None, max_length=5000, description="Optional description")
    priority: Optional[str] = PydanticField(default="Medium", max_length=20, description="Task priority: Low, Medium, or High")
    category: Optional[str] = PydanticField(default=None, max_length=50, description="Task category")
    due_date: Optional[datetime] = PydanticField(default=None, description="Due date")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Call dentist",
                "description": "Schedule annual checkup",
                "priority": "Medium",
                "category": "Health",
                "due_date": "2024-12-30T00:00:00"
            }
        }

class TaskUpdate(BaseModel):
    title: Optional[str] = PydanticField(default=None, min_length=1, max_length=200)
    description: Optional[str] = PydanticField(default=None, max_length=5000)
    priority: Optional[str] = PydanticField(default=None, max_length=20)
    category: Optional[str] = PydanticField(default=None, max_length=50)
    due_date: Optional[datetime] = PydanticField(default=None)

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: Optional[str]
    category: Optional[str]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows creation from ORM models