"""Tool implementations for Gemini function calling.

This module provides:
1. TypedDict definitions for tool return types
2. Async handler functions for each tool
3. Tool dispatcher for routing function calls

All handlers enforce user isolation by requiring user_id parameter.
"""

from typing import TypedDict, Optional, List, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.models.task import Task


# ============================================================================
# TypedDict definitions for tool responses (T005)
# ============================================================================

class TaskItem(TypedDict):
    """Individual task item in list responses."""
    id: int
    title: str
    completed: bool
    description: Optional[str]


class AddTaskResult(TypedDict, total=False):
    """Response from add_task tool."""
    status: str  # "created" | "error"
    task_id: int  # Only on success
    title: str    # Only on success
    message: str  # Only on error


class ListTasksResult(TypedDict, total=False):
    """Response from list_tasks tool."""
    status: str  # "listed" | "error"
    tasks: List[TaskItem]  # Only on success
    message: str  # Only on error


class CompleteTaskResult(TypedDict, total=False):
    """Response from complete_task tool."""
    status: str  # "completed" | "error"
    task_id: int  # Only on success
    title: str    # Only on success
    message: str  # Only on error


class DeleteTaskResult(TypedDict, total=False):
    """Response from delete_task tool."""
    status: str  # "deleted" | "error"
    task_id: int  # Only on success
    title: str    # Only on success
    message: str  # Only on error


class UpdateTaskResult(TypedDict, total=False):
    """Response from update_task tool."""
    status: str  # "updated" | "error"
    task_id: int  # Only on success
    title: str    # Only on success
    message: str  # Only on error


# ============================================================================
# Async handler functions for each tool (T008, T012, T016, T021, T026)
# ============================================================================

async def add_task_handler(
    session: AsyncSession,
    user_id: str,
    title: str,
    description: Optional[str] = None
) -> AddTaskResult:
    """
    Create a new task for the user.

    Args:
        session: Database session
        user_id: The authenticated user's unique ID
        title: Short title of the task
        description: Optional longer details or notes

    Returns:
        AddTaskResult with status "created" and task details, or "error" with message
    """
    try:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "status": "created",
            "task_id": task.id,
            "title": task.title
        }
    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "message": f"Failed to create task: {str(e)}"
        }


async def list_tasks_handler(
    session: AsyncSession,
    user_id: str,
    status: Optional[str] = None
) -> ListTasksResult:
    """
    Retrieve the user's tasks with optional status filtering.

    Args:
        session: Database session
        user_id: The authenticated user's unique ID
        status: Filter by "all", "pending", or "completed"

    Returns:
        ListTasksResult with status "listed" and tasks array, or "error" with message
    """
    try:
        # Build query with user isolation
        query = select(Task).where(Task.user_id == user_id)

        # Apply status filter
        if status == "pending":
            query = query.where(Task.completed == False)  # noqa: E712
        elif status == "completed":
            query = query.where(Task.completed == True)  # noqa: E712
        # "all" or None means no filter

        result = await session.execute(query)
        tasks = result.scalars().all()

        task_items: List[TaskItem] = [
            {
                "id": task.id,
                "title": task.title,
                "completed": task.completed,
                "description": task.description
            }
            for task in tasks
        ]

        return {
            "status": "listed",
            "tasks": task_items
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve tasks: {str(e)}"
        }


async def complete_task_handler(
    session: AsyncSession,
    user_id: str,
    task_id: int
) -> CompleteTaskResult:
    """
    Mark a task as completed.

    Args:
        session: Database session
        user_id: The authenticated user's unique ID
        task_id: The ID of the task to mark as completed

    Returns:
        CompleteTaskResult with status "completed" and task details, or "error" with message
    """
    try:
        # Ownership validation: task must belong to user_id
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            return {
                "status": "error",
                "message": "Task not found or does not belong to user"
            }

        task.completed = True
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "status": "completed",
            "task_id": task.id,
            "title": task.title
        }
    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "message": f"Failed to complete task: {str(e)}"
        }


async def delete_task_handler(
    session: AsyncSession,
    user_id: str,
    task_id: int
) -> DeleteTaskResult:
    """
    Delete a task permanently.

    Args:
        session: Database session
        user_id: The authenticated user's unique ID
        task_id: The ID of the task to delete

    Returns:
        DeleteTaskResult with status "deleted" and task details, or "error" with message
    """
    try:
        # Ownership validation: task must belong to user_id
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            return {
                "status": "error",
                "message": "Task not found or does not belong to user"
            }

        # Capture info before deletion
        deleted_task_id = task.id
        deleted_title = task.title

        await session.delete(task)
        await session.commit()

        return {
            "status": "deleted",
            "task_id": deleted_task_id,
            "title": deleted_title
        }
    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "message": f"Failed to delete task: {str(e)}"
        }


async def update_task_handler(
    session: AsyncSession,
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> UpdateTaskResult:
    """
    Update task title and/or description.

    Args:
        session: Database session
        user_id: The authenticated user's unique ID
        task_id: The ID of the task to update
        title: New title for the task (optional)
        description: New description for the task (optional)

    Returns:
        UpdateTaskResult with status "updated" and task details, or "error" with message
    """
    try:
        # Validate at least one field is provided
        if title is None and description is None:
            return {
                "status": "error",
                "message": "No fields provided to update"
            }

        # Ownership validation: task must belong to user_id
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            return {
                "status": "error",
                "message": "Task not found or does not belong to user"
            }

        # Update only provided fields
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description

        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "status": "updated",
            "task_id": task.id,
            "title": task.title
        }
    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "message": f"Failed to update task: {str(e)}"
        }


# ============================================================================
# Tool Dispatcher (T006, T032)
# ============================================================================

# Handler mapping for routing function calls
_TOOL_HANDLERS = {
    "add_task": add_task_handler,
    "list_tasks": list_tasks_handler,
    "complete_task": complete_task_handler,
    "delete_task": delete_task_handler,
    "update_task": update_task_handler,
}


async def dispatch_tool(
    session: AsyncSession,
    name: str,
    args: dict[str, Any]
) -> dict[str, Any]:
    """
    Route a function call to the appropriate handler.

    Args:
        session: Database session for handlers
        name: Name of the function to call
        args: Dictionary of argument name to value

    Returns:
        The result from the appropriate handler

    Raises:
        ValueError: If the function name is not recognized
    """
    handler = _TOOL_HANDLERS.get(name)
    if handler is None:
        return {
            "status": "error",
            "message": f"Unknown function: {name}"
        }

    # Call the handler with session and provided args
    return await handler(session, **args)
