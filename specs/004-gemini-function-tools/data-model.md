# Data Model: Gemini Function Calling Tools

**Feature**: 004-gemini-function-tools | **Date**: 2026-01-16

## Overview

This document defines the entities involved in Gemini function calling for the Todo AI Chatbot. These are not database entities but rather the data structures used for tool declarations and responses.

## Entities

### Entity 1: Tool Declaration

A structured definition that tells Gemini what functions are available.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Unique identifier for the tool (e.g., "add_task") |
| description | string | Yes | Natural language description of when to use this tool |
| parameters_json_schema | object | Yes | JSON Schema defining input parameters |

**SDK Class**: `google.genai.types.FunctionDeclaration`

### Entity 2: Tool Parameters Schema

JSON Schema structure for each tool's parameters.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | Always "object" for tool parameters |
| properties | object | Yes | Map of parameter name to schema |
| required | array | Yes | List of required parameter names |

### Entity 3: Function Call (from Gemini)

The response from Gemini when it decides to invoke a tool.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Name of the function to call |
| args | object | Yes | Dictionary of argument name to value |

**SDK Class**: `google.genai.types.FunctionCall`

### Entity 4: Function Response (to Gemini)

The result returned after executing a tool, fed back to Gemini.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Name of the function that was called |
| response | object | Yes | JSON response from the function |

**SDK Class**: `google.genai.types.FunctionResponse`

## Tool Definitions

### Tool 1: add_task

**Purpose**: Create a new todo task for the user.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | The authenticated user's unique ID |
| title | string | Yes | Short title of the task |
| description | string | No | Optional longer details or notes |

**Returns (Success)**:
```json
{
  "status": "created",
  "task_id": 5,
  "title": "Buy groceries"
}
```

**Returns (Error)**:
```json
{
  "status": "error",
  "message": "Failed to create task"
}
```

### Tool 2: list_tasks

**Purpose**: Retrieve the user's tasks with optional status filtering.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | The authenticated user's unique ID |
| status | string (enum) | No | Filter: "all", "pending", or "completed" |

**Enum Values for status**:
- `all` (default)
- `pending`
- `completed`

**Returns (Success)**:
```json
{
  "status": "listed",
  "tasks": [
    {"id": 1, "title": "Buy groceries", "completed": false, "description": null},
    {"id": 2, "title": "Finish report", "completed": true, "description": "Q4 analysis"}
  ]
}
```

**Returns (Empty)**:
```json
{
  "status": "listed",
  "tasks": []
}
```

**Returns (Error)**:
```json
{
  "status": "error",
  "message": "Failed to retrieve tasks"
}
```

### Tool 3: complete_task

**Purpose**: Mark a task as completed.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | The authenticated user's unique ID |
| task_id | integer | Yes | The ID of the task to mark as completed |

**Returns (Success)**:
```json
{
  "status": "completed",
  "task_id": 5,
  "title": "Buy groceries"
}
```

**Returns (Error)**:
```json
{
  "status": "error",
  "message": "Task not found or does not belong to user"
}
```

### Tool 4: delete_task

**Purpose**: Delete a task permanently.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | The authenticated user's unique ID |
| task_id | integer | Yes | The ID of the task to delete |

**Returns (Success)**:
```json
{
  "status": "deleted",
  "task_id": 5,
  "title": "Buy groceries"
}
```

**Returns (Error)**:
```json
{
  "status": "error",
  "message": "Task not found or does not belong to user"
}
```

### Tool 5: update_task

**Purpose**: Change the title and/or description of an existing task.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | The authenticated user's unique ID |
| task_id | integer | Yes | The ID of the task to update |
| title | string | No | New title for the task |
| description | string | No | New description for the task |

**Validation**: At least one of `title` or `description` must be provided.

**Returns (Success)**:
```json
{
  "status": "updated",
  "task_id": 5,
  "title": "Buy organic groceries"
}
```

**Returns (Error - Not Found)**:
```json
{
  "status": "error",
  "message": "Task not found or does not belong to user"
}
```

**Returns (Error - No Changes)**:
```json
{
  "status": "error",
  "message": "No fields provided to update"
}
```

## Response Status Values

All tool responses use consistent status values:

| Status | Operation | Meaning |
|--------|-----------|---------|
| created | add_task | Task successfully created |
| listed | list_tasks | Tasks successfully retrieved |
| completed | complete_task | Task marked as complete |
| deleted | delete_task | Task permanently removed |
| updated | update_task | Task successfully modified |
| error | Any | Operation failed |

## Type Definitions (Python)

```python
from typing import TypedDict, Optional, List

class TaskItem(TypedDict):
    id: int
    title: str
    completed: bool
    description: Optional[str]

class AddTaskResult(TypedDict):
    status: str  # "created" | "error"
    task_id: int  # Only on success
    title: str    # Only on success
    message: str  # Only on error

class ListTasksResult(TypedDict):
    status: str  # "listed" | "error"
    tasks: List[TaskItem]  # Only on success
    message: str  # Only on error

class CompleteTaskResult(TypedDict):
    status: str  # "completed" | "error"
    task_id: int  # Only on success
    title: str    # Only on success
    message: str  # Only on error

class DeleteTaskResult(TypedDict):
    status: str  # "deleted" | "error"
    task_id: int  # Only on success
    title: str    # Only on success
    message: str  # Only on error

class UpdateTaskResult(TypedDict):
    status: str  # "updated" | "error"
    task_id: int  # Only on success
    title: str    # Only on success
    message: str  # Only on error
```

## Relationship to Database Model

The tool parameters and responses map to the existing `Task` model:

| Tool Parameter | Task Model Field |
|----------------|------------------|
| user_id | user_id (FK to users) |
| task_id | id (PK) |
| title | title |
| description | description |
| (implicit) | completed |

The `completed` field is implicitly managed:
- `add_task` creates tasks with `completed=False`
- `complete_task` sets `completed=True`
- `list_tasks` can filter by `completed` status
