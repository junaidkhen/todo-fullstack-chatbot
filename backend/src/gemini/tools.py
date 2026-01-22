"""Gemini function calling tool declarations for task management.

This module defines the 5 Gemini function calling tools for the Todo AI Chatbot:
- add_task: Create a new task
- list_tasks: Retrieve user's tasks with optional filtering
- complete_task: Mark a task as completed
- delete_task: Delete a task permanently
- update_task: Modify task title/description

All tools require user_id for user isolation per Phase III Constitution.
"""

from google.genai import types


def get_task_tools() -> types.Tool:
    """
    Returns a Tool object containing all 5 task management function declarations.

    All tools are designed with:
    - user_id as required parameter for user isolation
    - Clear descriptions for Gemini intent detection
    - JSON schema parameters for type safety

    Returns:
        types.Tool: Tool object to pass to Gemini generate_content config
    """
    add_task = types.FunctionDeclaration(
        name="add_task",
        description="Use this to create a new todo task for the user. Call when user wants to add, create, or make a new task.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The authenticated user's unique ID"
                },
                "title": {
                    "type": "string",
                    "description": "Short title of the task (required)"
                },
                "description": {
                    "type": "string",
                    "description": "Optional longer details or notes about the task"
                }
            },
            "required": ["user_id", "title"]
        }
    )

    list_tasks = types.FunctionDeclaration(
        name="list_tasks",
        description="Retrieve the user's tasks. Use when user wants to see, view, show, or list their tasks. Supports filtering by status.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The authenticated user's unique ID"
                },
                "status": {
                    "type": "string",
                    "enum": ["all", "pending", "completed"],
                    "description": "Filter tasks by status. Defaults to 'all' if not specified."
                }
            },
            "required": ["user_id"]
        }
    )

    complete_task = types.FunctionDeclaration(
        name="complete_task",
        description="Mark a task as completed. Use when user says they finished, completed, or done with a task.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The authenticated user's unique ID"
                },
                "task_id": {
                    "type": "integer",
                    "description": "The ID of the task to mark as completed"
                }
            },
            "required": ["user_id", "task_id"]
        }
    )

    delete_task = types.FunctionDeclaration(
        name="delete_task",
        description="Delete a task permanently. Use when user wants to remove, delete, or get rid of a task.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The authenticated user's unique ID"
                },
                "task_id": {
                    "type": "integer",
                    "description": "The ID of the task to delete"
                }
            },
            "required": ["user_id", "task_id"]
        }
    )

    update_task = types.FunctionDeclaration(
        name="update_task",
        description="Change the title and/or description of an existing task. Use when user wants to edit, rename, update, or modify a task.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The authenticated user's unique ID"
                },
                "task_id": {
                    "type": "integer",
                    "description": "The ID of the task to update"
                },
                "title": {
                    "type": "string",
                    "description": "New title for the task (optional)"
                },
                "description": {
                    "type": "string",
                    "description": "New description for the task (optional)"
                }
            },
            "required": ["user_id", "task_id"]
        }
    )

    return types.Tool(
        function_declarations=[
            add_task,
            list_tasks,
            complete_task,
            delete_task,
            update_task
        ]
    )
