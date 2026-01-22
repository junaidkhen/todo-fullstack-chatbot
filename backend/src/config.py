"""Configuration module for chat endpoint environment variables.

Loads and validates environment variables required for the chat endpoint:
- GEMINI_API_KEY: Required API key for Gemini AI
- GEMINI_MODEL: Model to use (default: gemini-2.0-flash)
- FRONTEND_ORIGIN: Allowed CORS origin for frontend
- MAX_TOOL_ITERATIONS: Maximum tool execution iterations (default: 5)
- HISTORY_MESSAGE_LIMIT: Maximum history messages to include (default: 20)
"""

import os
from dataclasses import dataclass


@dataclass
class ChatConfig:
    """Configuration for the chat endpoint."""
    gemini_api_key: str
    gemini_model: str
    frontend_origin: str
    max_tool_iterations: int
    history_message_limit: int
    debug: bool

    @classmethod
    def from_env(cls) -> "ChatConfig":
        """Load configuration from environment variables."""
        gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        return cls(
            gemini_api_key=gemini_api_key,
            gemini_model=os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"),
            frontend_origin=os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000"),
            max_tool_iterations=int(os.environ.get("MAX_TOOL_ITERATIONS", "5")),
            history_message_limit=int(os.environ.get("HISTORY_MESSAGE_LIMIT", "20")),
            debug=os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes"),
        )


# Singleton instance
_config: ChatConfig | None = None


def get_config() -> ChatConfig:
    """Get or create the configuration singleton."""
    global _config
    if _config is None:
        _config = ChatConfig.from_env()
    return _config


# Environment variable names for reference
ENV_GEMINI_API_KEY = "GEMINI_API_KEY"
ENV_GEMINI_MODEL = "GEMINI_MODEL"
ENV_FRONTEND_ORIGIN = "FRONTEND_ORIGIN"
ENV_MAX_TOOL_ITERATIONS = "MAX_TOOL_ITERATIONS"
ENV_HISTORY_MESSAGE_LIMIT = "HISTORY_MESSAGE_LIMIT"
ENV_DEBUG = "DEBUG"
