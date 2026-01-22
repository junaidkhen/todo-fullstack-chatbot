# Feature Specification: Gemini Function Calling Tools Definition (Chunk-3)

**Feature Branch**: `004-gemini-function-tools`
**Created**: 2026-01-16
**Status**: Draft
**Input**: User description: "Chunk 3: Gemini Function Calling Tools Definition - Define the exact tool/function declarations that will be passed to Gemini model for native function calling"

## Overview

This specification defines the exact tool/function declarations that will be passed to the Gemini model for native function calling. These tools replace the original MCP tools concept and enable the AI chatbot to execute task management operations through natural language conversation.

The Gemini function calling schema uses a JSON-like format similar to OpenAI function calling, with specific adaptations for the google-generativeai SDK.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add a New Task via Chat (Priority: P1)

A user types a natural language message like "Add a task to buy groceries" in the chat. The AI interprets this as an intent to create a task, calls the `add_task` function with the appropriate parameters, and confirms the task creation in a friendly response.

**Why this priority**: Task creation is the most fundamental operation. Users cannot manage tasks if they cannot create them first.

**Independent Test**: Can be fully tested by sending a chat message requesting task creation and verifying the task appears in the database with correct user ownership.

**Acceptance Scenarios**:

1. **Given** an authenticated user with no tasks, **When** the user says "Add a task: Buy milk", **Then** the AI calls `add_task` with the user's ID and title "Buy milk", and responds with confirmation including the new task ID.
2. **Given** an authenticated user, **When** the user says "Create a task to finish report with details: Complete quarterly analysis by Friday", **Then** the AI calls `add_task` with title and description parameters populated correctly.
3. **Given** an authenticated user, **When** the AI receives a function call result with `{"status": "created", "task_id": 5, "title": "Buy milk"}`, **Then** the AI responds with a friendly confirmation message.

---

### User Story 2 - List Tasks via Chat (Priority: P1)

A user asks to see their tasks through natural language like "Show me my tasks" or "What's on my todo list?". The AI calls the `list_tasks` function and presents the results in a readable format.

**Why this priority**: Users need visibility into their existing tasks to manage them effectively. This is essential for all other operations (complete, update, delete).

**Independent Test**: Can be fully tested by sending a chat message requesting task list and verifying the response shows the correct tasks for that user only.

**Acceptance Scenarios**:

1. **Given** an authenticated user with 3 pending tasks, **When** the user says "Show my tasks", **Then** the AI calls `list_tasks` with the user's ID and returns all tasks.
2. **Given** an authenticated user with pending and completed tasks, **When** the user says "Show me my completed tasks", **Then** the AI calls `list_tasks` with status="completed" filter.
3. **Given** an authenticated user with no tasks, **When** the user says "What's on my list?", **Then** the AI responds with a friendly message indicating no tasks exist.

---

### User Story 3 - Complete a Task via Chat (Priority: P2)

A user indicates they've finished a task through natural language like "Mark 'Buy groceries' as done" or "I completed task 3". The AI identifies the task and calls the `complete_task` function.

**Why this priority**: Task completion is a core workflow action but requires tasks to exist first (depends on P1 scenarios).

**Independent Test**: Can be fully tested by creating a task, then sending a chat message to complete it, and verifying the task status changes in the database.

**Acceptance Scenarios**:

1. **Given** an authenticated user with task ID 5 titled "Buy groceries", **When** the user says "Mark task 5 as complete", **Then** the AI calls `complete_task` with task_id=5.
2. **Given** an authenticated user referencing a task by title, **When** the user says "I finished buying groceries", **Then** the AI may first call `list_tasks` to identify the task ID, then call `complete_task`.
3. **Given** an authenticated user, **When** the user tries to complete a non-existent task, **Then** the AI receives an error response and communicates failure gracefully.

---

### User Story 4 - Delete a Task via Chat (Priority: P2)

A user wants to remove a task from their list through natural language like "Delete task 5" or "Remove the groceries task".

**Why this priority**: Task deletion is important for list management but less frequent than creation or completion.

**Independent Test**: Can be fully tested by creating a task, then sending a chat message to delete it, and verifying the task is removed from the database.

**Acceptance Scenarios**:

1. **Given** an authenticated user with task ID 5, **When** the user says "Delete task 5", **Then** the AI calls `delete_task` with task_id=5 and confirms deletion.
2. **Given** an authenticated user, **When** the user references a task ambiguously (e.g., "delete the meeting"), **Then** the AI first calls `list_tasks` to clarify which task before proceeding.
3. **Given** an authenticated user attempting to delete another user's task, **When** the function executes, **Then** it returns an error and no data is deleted.

---

### User Story 5 - Update a Task via Chat (Priority: P3)

A user wants to modify an existing task's title or description through natural language like "Rename task 3 to 'Buy organic groceries'" or "Update the description of my report task".

**Why this priority**: Task updates are less common than other operations but still necessary for complete task management.

**Independent Test**: Can be fully tested by creating a task, sending a chat message to update it, and verifying the changes persist in the database.

**Acceptance Scenarios**:

1. **Given** an authenticated user with task ID 3 titled "Buy groceries", **When** the user says "Rename task 3 to 'Buy organic groceries'", **Then** the AI calls `update_task` with the new title.
2. **Given** an authenticated user with task ID 3, **When** the user says "Add a note to task 3: Remember to check expiry dates", **Then** the AI calls `update_task` with the new description.
3. **Given** an authenticated user, **When** the user provides both new title and description, **Then** both fields are updated in a single function call.

---

### Edge Cases

- **Ambiguous task reference**: When user says "delete my task" but has multiple tasks, AI should call `list_tasks` first and ask for clarification.
- **Non-matching intent**: When user sends general chat (e.g., "Hello, how are you?"), no function should be called; AI responds conversationally.
- **Rate limit hit**: When Gemini API rate limit is reached, the system should gracefully degrade and inform the user.
- **Invalid task ID**: When user references a task ID that doesn't exist, the function returns an error and AI communicates this naturally.
- **User isolation violation attempt**: If function receives a user_id that doesn't match the authenticated user, the operation must fail.
- **Empty task title**: If user asks to create a task without a title, AI should ask for clarification rather than calling the function.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST declare exactly 5 tools for Gemini function calling: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`.
- **FR-002**: Every tool MUST include `user_id` as a required string parameter for ownership validation.
- **FR-003**: Tool declarations MUST use the Gemini SDK's supported function declaration format with name, description, and parameters schema.
- **FR-004**: Each tool's parameters schema MUST define type as "object" with explicit properties and required array.
- **FR-005**: Tool descriptions MUST clearly state when to use each tool in natural language.
- **FR-006**: All tool return values MUST be JSON dictionaries with a "status" field indicating outcome.
- **FR-007**: Success statuses MUST use specific values: "created", "listed", "completed", "deleted", "updated".
- **FR-008**: Error responses MUST include "status": "error" and a human-readable "message" field.
- **FR-009**: The `list_tasks` tool MUST support optional status filtering with enum values: "all", "pending", "completed".
- **FR-010**: The `add_task` tool MUST accept optional description parameter for task details.
- **FR-011**: The `update_task` tool MUST allow updating title and/or description independently (both optional, but task_id required).
- **FR-012**: Task ID parameters MUST be typed as integers for `complete_task`, `delete_task`, and `update_task`.
- **FR-013**: When no tool matches user intent, the AI MUST respond conversationally without calling any function.
- **FR-014**: For ambiguous requests, the AI SHOULD call `list_tasks` first to gather context before other operations.

### Key Entities

- **Tool Declaration**: A structured definition containing name, description, and parameters schema that tells Gemini what functions are available.
- **Function Call**: The response from Gemini when it decides to invoke a tool, containing function name and arguments.
- **Function Result**: The JSON response returned after executing the tool operation, fed back to Gemini for natural language response generation.

---

## Tool Definitions *(mandatory)*

### General Notes

Tools are declared in Gemini SDK using this structure:
```
tools = [
  {
    "name": "tool_name",
    "description": "When to use this tool",
    "parameters": {
      "type": "object",
      "properties": { ... },
      "required": [ ... ]
    }
  }
]
```

All parameters are JSON serializable. Returns are always JSON dictionaries.

---

### Tool 1: add_task

- **Name**: `add_task`
- **Description**: Use this to create a new todo task for the user. Call when user wants to add, create, or make a new task.
- **Parameters Schema**:
  ```json
  {
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
  ```
- **Expected Return (Success)**:
  ```json
  {"status": "created", "task_id": 5, "title": "Buy groceries"}
  ```
- **Expected Return (Error)**:
  ```json
  {"status": "error", "message": "Failed to create task"}
  ```

---

### Tool 2: list_tasks

- **Name**: `list_tasks`
- **Description**: Retrieve the user's tasks. Use when user wants to see, view, show, or list their tasks. Supports filtering by status.
- **Parameters Schema**:
  ```json
  {
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
  ```
- **Expected Return (Success)**:
  ```json
  {
    "status": "listed",
    "tasks": [
      {"id": 1, "title": "Buy groceries", "completed": false, "description": null},
      {"id": 2, "title": "Finish report", "completed": true, "description": "Q4 analysis"}
    ]
  }
  ```
- **Expected Return (Empty)**:
  ```json
  {"status": "listed", "tasks": []}
  ```
- **Expected Return (Error)**:
  ```json
  {"status": "error", "message": "Failed to retrieve tasks"}
  ```

---

### Tool 3: complete_task

- **Name**: `complete_task`
- **Description**: Mark a task as completed. Use when user says they finished, completed, or done with a task.
- **Parameters Schema**:
  ```json
  {
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
  ```
- **Expected Return (Success)**:
  ```json
  {"status": "completed", "task_id": 5, "title": "Buy groceries"}
  ```
- **Expected Return (Error - Not Found)**:
  ```json
  {"status": "error", "message": "Task not found or does not belong to user"}
  ```

---

### Tool 4: delete_task

- **Name**: `delete_task`
- **Description**: Delete a task permanently. Use when user wants to remove, delete, or get rid of a task.
- **Parameters Schema**:
  ```json
  {
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
  ```
- **Expected Return (Success)**:
  ```json
  {"status": "deleted", "task_id": 5, "title": "Buy groceries"}
  ```
- **Expected Return (Error - Not Found)**:
  ```json
  {"status": "error", "message": "Task not found or does not belong to user"}
  ```

---

### Tool 5: update_task

- **Name**: `update_task`
- **Description**: Change the title and/or description of an existing task. Use when user wants to edit, rename, update, or modify a task.
- **Parameters Schema**:
  ```json
  {
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
  ```
- **Expected Return (Success)**:
  ```json
  {"status": "updated", "task_id": 5, "title": "Buy organic groceries"}
  ```
- **Expected Return (Error - Not Found)**:
  ```json
  {"status": "error", "message": "Task not found or does not belong to user"}
  ```
- **Expected Return (Error - No Changes)**:
  ```json
  {"status": "error", "message": "No fields provided to update"}
  ```

---

## AI Behavior Guidelines *(mandatory)*

### When to Call Tools

| User Intent | Tool to Call | Notes |
| ----------- | ------------ | ----- |
| Create/add/make new task | `add_task` | Extract title from message |
| Show/list/view tasks | `list_tasks` | Check for status filter keywords |
| Mark done/complete/finish | `complete_task` | May need `list_tasks` first for ID |
| Remove/delete task | `delete_task` | May need `list_tasks` first for ID |
| Edit/rename/update task | `update_task` | May need `list_tasks` first for ID |
| General conversation | None | Respond naturally |
| Unclear/ambiguous | `list_tasks` | Gather context first |

### Disambiguation Strategy

1. If user references task by ID explicitly (e.g., "task 5"), use that ID directly.
2. If user references task by title (e.g., "the groceries task"), call `list_tasks` first to find matching ID.
3. If multiple tasks match, ask user for clarification before proceeding.
4. If no tasks match, inform user the task was not found.

### Error Communication

All error responses MUST be communicated naturally and friendly. Examples:
- "Task nahi mila bhai" (Task not found, bro)
- "Oops! I couldn't find that task. Want me to show you your list?"
- "That task doesn't seem to exist. Maybe it was already deleted?"

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 5 tool declarations conform to Gemini SDK function calling schema and are accepted without validation errors.
- **SC-002**: 100% of tool calls include user_id parameter for ownership validation.
- **SC-003**: AI correctly identifies user intent and calls appropriate tool in 95%+ of standard requests.
- **SC-004**: Error responses always include both "status": "error" and a descriptive "message" field.
- **SC-005**: Task operations (create, list, complete, delete, update) return consistent JSON structure across all scenarios.
- **SC-006**: User isolation is enforced on every tool execution - no cross-user data access possible.
- **SC-007**: Ambiguous requests result in clarification behavior rather than incorrect operations.
- **SC-008**: Non-task-related chat messages do not trigger any function calls.

---

## Assumptions

- The google-generativeai SDK version supports the simple dict-based tool declaration format (not requiring protobuf).
- User authentication is handled at the API layer before tool execution; user_id is always available.
- Task IDs are integers auto-generated by the database.
- The Gemini model (gemini-1.5-flash or gemini-2.5-flash) supports function calling.
- Natural language processing for intent detection is handled by Gemini, not custom code.

---

## Dependencies

- **Phase III Constitution**: This specification follows Phase III architectural principles.
- **Database Schema (Chunk 2)**: Tasks table must exist with user_id foreign key for ownership.
- **Gemini API**: Free tier with function calling support required.
- **Better Auth**: User authentication provides the user_id for all operations.

---

## Out of Scope

- Tool execution logic (covered in separate implementation spec)
- Conversation history management
- Rate limit handling implementation
- Frontend chat UI
- Gemini prompt engineering and system instructions
- Database connection and ORM setup
