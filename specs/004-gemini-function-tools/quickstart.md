# Quickstart: Gemini Function Calling Tools

**Feature**: 004-gemini-function-tools | **Date**: 2026-01-16

## Prerequisites

- Python 3.11+
- Gemini API key (get from [Google AI Studio](https://aistudio.google.com/))
- Backend virtual environment active

## Installation

```bash
cd backend
pip install google-genai>=1.0.0
```

Or add to `requirements.txt`:
```
google-genai>=1.0.0
```

## Environment Setup

Add to `.env`:
```
GEMINI_API_KEY=your-api-key-here
```

## Quick Implementation

### Step 1: Create the tools module

Create `backend/src/gemini/__init__.py`:
```python
from .tools import get_task_tools

__all__ = ["get_task_tools"]
```

Create `backend/src/gemini/tools.py`:
```python
"""Gemini function calling tool declarations for task management."""

from google.genai import types


def get_task_tools() -> types.Tool:
    """
    Returns a Tool object containing all 5 task management function declarations.

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
```

### Step 2: Test the declarations

Create `backend/tests/unit/test_gemini_tools.py`:
```python
"""Unit tests for Gemini function calling tool declarations."""

import pytest
from src.gemini.tools import get_task_tools


class TestGeminiTools:
    """Test suite for Gemini tool declarations."""

    def test_get_task_tools_returns_tool(self):
        """Tool object should be returned."""
        tool = get_task_tools()
        assert tool is not None
        assert hasattr(tool, "function_declarations")

    def test_exactly_five_tools_declared(self):
        """Spec requires exactly 5 tools."""
        tool = get_task_tools()
        assert len(tool.function_declarations) == 5

    def test_tool_names(self):
        """All required tool names should be present."""
        tool = get_task_tools()
        names = {fd.name for fd in tool.function_declarations}
        expected = {"add_task", "list_tasks", "complete_task", "delete_task", "update_task"}
        assert names == expected

    def test_all_tools_have_user_id_required(self):
        """Every tool must require user_id parameter."""
        tool = get_task_tools()
        for fd in tool.function_declarations:
            schema = fd.parameters_json_schema
            assert "user_id" in schema["properties"], f"{fd.name} missing user_id"
            assert "user_id" in schema["required"], f"{fd.name} user_id not required"

    def test_add_task_parameters(self):
        """add_task should have correct parameters."""
        tool = get_task_tools()
        add_task = next(fd for fd in tool.function_declarations if fd.name == "add_task")
        schema = add_task.parameters_json_schema

        assert "title" in schema["properties"]
        assert "description" in schema["properties"]
        assert set(schema["required"]) == {"user_id", "title"}

    def test_list_tasks_status_enum(self):
        """list_tasks status should have correct enum values."""
        tool = get_task_tools()
        list_tasks = next(fd for fd in tool.function_declarations if fd.name == "list_tasks")
        schema = list_tasks.parameters_json_schema

        status_prop = schema["properties"]["status"]
        assert status_prop["enum"] == ["all", "pending", "completed"]

    def test_task_id_is_integer(self):
        """task_id should be typed as integer for complete, delete, update."""
        tool = get_task_tools()

        for name in ["complete_task", "delete_task", "update_task"]:
            fd = next(f for f in tool.function_declarations if f.name == name)
            schema = fd.parameters_json_schema
            assert schema["properties"]["task_id"]["type"] == "integer", f"{name} task_id should be integer"

    def test_update_task_optional_fields(self):
        """update_task should allow optional title and description."""
        tool = get_task_tools()
        update_task = next(fd for fd in tool.function_declarations if fd.name == "update_task")
        schema = update_task.parameters_json_schema

        # title and description should be in properties but not required
        assert "title" in schema["properties"]
        assert "description" in schema["properties"]
        assert "title" not in schema["required"]
        assert "description" not in schema["required"]
```

### Step 3: Run tests

```bash
cd backend
pytest tests/unit/test_gemini_tools.py -v
```

### Step 4: Usage example

```python
import os
from google import genai
from google.genai import types
from src.gemini.tools import get_task_tools

# Initialize client
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Get tool declarations
tool = get_task_tools()

# Send message with manual function calling
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Add a task to buy groceries",
    config=types.GenerateContentConfig(
        tools=[tool],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        )
    )
)

# Check if model wants to call a function
if response.function_calls:
    for fc in response.function_calls:
        print(f"Function: {fc.name}")
        print(f"Args: {dict(fc.args)}")
else:
    print(f"Text: {response.text}")
```

## Verification Checklist

- [ ] `google-genai` installed in backend environment
- [ ] `GEMINI_API_KEY` set in `.env`
- [ ] `backend/src/gemini/__init__.py` created
- [ ] `backend/src/gemini/tools.py` created with all 5 tools
- [ ] Unit tests pass: `pytest tests/unit/test_gemini_tools.py -v`
- [ ] Example usage works with real API key

## Next Steps

After completing this quickstart:

1. Run `/sp.tasks` to generate implementation tasks
2. Implement tool execution handlers in `backend/src/services/task_tools.py`
3. Integrate with chat endpoint (Chunk 5)

## Troubleshooting

### Import Error: google.genai

```
ModuleNotFoundError: No module named 'google.genai'
```

**Fix**: Install the correct package:
```bash
pip install google-genai
```

Note: Do NOT install `google-generativeai` (deprecated).

### API Key Not Found

```
google.auth.exceptions.DefaultCredentialsError
```

**Fix**: Ensure `GEMINI_API_KEY` is set:
```bash
export GEMINI_API_KEY=your-key-here
```

### Rate Limit Exceeded

```
google.api_core.exceptions.ResourceExhausted: 429
```

**Fix**: Gemini free tier has 5-15 RPM limits. Wait and retry.
