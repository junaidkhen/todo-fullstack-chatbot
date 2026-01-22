import os
import logging
from contextlib import asynccontextmanager

# Load environment variables from .env file FIRST before any other imports
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable

from src.api import tasks, health, auth
from src.api import chat

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.environ.get("DEBUG", "false").lower() == "true" else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database when the app starts
    from src.init_db import init_db
    await init_db()
    logger.info("Database initialized")
    yield


app = FastAPI(
    title="Todo AI Chat API",
    description="AI-powered task management with natural language chat interface",
    version="1.0.0",
    lifespan=lifespan
)


# =============================================================================
# Exception Handlers (T026-T030, T035)
# =============================================================================

@app.exception_handler(ResourceExhausted)
async def handle_rate_limit(request: Request, exc: ResourceExhausted):
    """T026: Handle Gemini rate limit errors."""
    logger.warning(f"Rate limit hit: {exc}")
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limited",
            "message": "I'm a bit busy right now. Please try again in a moment!",
            "details": None
        }
    )


@app.exception_handler(ServiceUnavailable)
async def handle_service_unavailable(request: Request, exc: ServiceUnavailable):
    """T027: Handle Gemini service unavailable errors."""
    logger.error(f"Service unavailable: {exc}")
    return JSONResponse(
        status_code=503,
        content={
            "error": "service_unavailable",
            "message": "I'm having trouble connecting. Please try again shortly.",
            "details": None
        }
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    """T035: Handle request body validation errors with clear error messages."""
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": list(error.get("loc", [])),
            "msg": error.get("msg", "Validation error"),
            "type": error.get("type", "value_error")
        })
    logger.warning(f"Validation error: {errors}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "unprocessable_entity",
            "message": "Request body validation failed",
            "details": {"errors": errors}
        }
    )


@app.exception_handler(Exception)
async def handle_generic_exception(request: Request, exc: Exception):
    """T028: Handle all unhandled exceptions with user-friendly message."""
    # T030: Log the actual exception for debugging
    logger.exception(f"Unhandled exception: {exc}")
    # T028: Return friendly message without stack trace
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "Something went wrong on my end. Please try again.",
            "details": None
        }
    )


# =============================================================================
# CORS Middleware (T015)
# =============================================================================

# Get CORS origin from environment with fallback
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# API Routes (T014)
# =============================================================================

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])

# T014: Chat router with user_id path parameter
app.include_router(chat.router, prefix="/api/{user_id}", tags=["chat"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)