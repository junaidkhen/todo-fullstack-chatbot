"""Business logic services for the Todo application."""

from .task_tools import (
    TaskItem,
    AddTaskResult,
    ListTasksResult,
    CompleteTaskResult,
    DeleteTaskResult,
    UpdateTaskResult,
    add_task_handler,
    list_tasks_handler,
    complete_task_handler,
    delete_task_handler,
    update_task_handler,
    dispatch_tool,
)

from .agent import (
    SYSTEM_PROMPT,
    ToolCallRecord,
    AgentResponse,
    AgentConfig,
    run_gemini_agent_safe,
    run_gemini_agent,
    build_contents_from_history,
    estimate_tokens,
    get_gemini_client,
    get_config,
)

from .conversation import (
    get_or_create_conversation,
    fetch_history,
    store_user_message,
    store_assistant_response,
)

__all__ = [
    # Task tool types
    "TaskItem",
    "AddTaskResult",
    "ListTasksResult",
    "CompleteTaskResult",
    "DeleteTaskResult",
    "UpdateTaskResult",
    # Task tool handlers
    "add_task_handler",
    "list_tasks_handler",
    "complete_task_handler",
    "delete_task_handler",
    "update_task_handler",
    "dispatch_tool",
    # Agent exports
    "SYSTEM_PROMPT",
    "ToolCallRecord",
    "AgentResponse",
    "AgentConfig",
    "run_gemini_agent_safe",
    "run_gemini_agent",
    "build_contents_from_history",
    "estimate_tokens",
    "get_gemini_client",
    "get_config",
    # Conversation service
    "get_or_create_conversation",
    "fetch_history",
    "store_user_message",
    "store_assistant_response",
]
