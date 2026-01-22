# Quickstart: FastAPI Chat Endpoint (Chunk 4)

**Feature**: 005-fastapi-chat-endpoint
**Date**: 2026-01-17

## Prerequisites

- Python 3.12+
- Existing backend setup from Phase II
- Gemini API key (free tier)

## Setup

### 1. Add Dependencies

```bash
cd backend
pip install google-generativeai>=0.8.0 google-api-core>=2.0.0
```

Or add to `requirements.txt`:
```text
google-generativeai>=0.8.0
google-api-core>=2.0.0
```

### 2. Environment Variables

Create or update `.env` in backend/:
```bash
# Required
GEMINI_API_KEY=your-api-key-here

# Optional (defaults shown)
GEMINI_MODEL=gemini-1.5-flash
FRONTEND_ORIGIN=http://localhost:3000
MAX_TOOL_ITERATIONS=5
HISTORY_MESSAGE_LIMIT=20
```

### 3. Verify Database Models

Ensure Conversation and Message models from Chunk 2 exist:
```bash
# Check if models exist
ls backend/src/models/conversation.py
```

If missing, create them per specs/003-db-models-schema/data-model.md.

## Run

### Start the Server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Test the Endpoint

```bash
# Create a test user first (if not exists)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'

# Get user ID from response, then test chat
curl -X POST http://localhost:8000/api/user-id-here/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, what can you do?"}'
```

### Expected Response (with stub agent)

```json
{
  "conversation_id": 1,
  "response": "Echo: Hello, what can you do?",
  "tool_calls": null
}
```

## Development Sequence

### Step 1: Configuration
Create `backend/src/config.py`:
```python
import os

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")
MAX_TOOL_ITERATIONS = int(os.environ.get("MAX_TOOL_ITERATIONS", "5"))
HISTORY_MESSAGE_LIMIT = int(os.environ.get("HISTORY_MESSAGE_LIMIT", "20"))
```

### Step 2: Schemas
Create `backend/src/schemas/chat.py` with models from data-model.md.

### Step 3: Dependencies
Create `backend/src/dependencies.py`:
```python
from fastapi import Depends, HTTPException, Path
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.database import get_session
from src.models.task import User

async def get_validated_user(
    user_id: str = Path(...),
    session: AsyncSession = Depends(get_session)
) -> str:
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=401, detail="User not found")
    return user_id
```

### Step 4: Conversation Service
Create `backend/src/services/conversation.py`:
```python
# See plan.md for full implementation
```

### Step 5: Agent Stub
Create `backend/src/services/agent.py`:
```python
from dataclasses import dataclass

@dataclass
class ToolCallRecord:
    name: str
    arguments: dict
    result: dict

@dataclass
class AgentResponse:
    text: str
    tool_calls: list[ToolCallRecord]

async def run_gemini_agent_safe(
    user_id: str,
    history: list[dict],
    new_message: str,
    db_session
) -> AgentResponse:
    """Stub - replace with Chunk 5 implementation."""
    return AgentResponse(
        text=f"Echo: {new_message}",
        tool_calls=[]
    )
```

### Step 6: Chat Router
Create `backend/src/api/chat.py`:
```python
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database import get_session
from src.dependencies import get_validated_user
from src.schemas.chat import ChatRequest, ChatResponse
from src.services.conversation import get_or_create_conversation, add_message, get_conversation_history
from src.services.agent import run_gemini_agent_safe

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_validated_user),
    session: AsyncSession = Depends(get_session)
):
    # Implementation per plan.md
    pass
```

### Step 7: Main App Integration
Update `backend/main.py`:
```python
from src.api import chat
from src.config import FRONTEND_ORIGIN

# Update CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    ...
)

# Add chat router
app.include_router(chat.router, prefix="/api/{user_id}", tags=["chat"])
```

## Testing

### Run Tests
```bash
cd backend
pytest tests/unit/test_chat_schemas.py -v
pytest tests/integration/test_chat_endpoint.py -v
```

### Manual Testing with cURL

```bash
# Start new conversation
curl -X POST http://localhost:8000/api/test-user-123/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task: Buy milk"}'

# Continue conversation
curl -X POST http://localhost:8000/api/test-user-123/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my tasks", "conversation_id": 1}'
```

## Next Steps

1. **Chunk 3/4**: Implement tool declarations and handlers
2. **Chunk 5**: Replace agent stub with Gemini integration
3. **Chunk 6/7**: Add agent behavior rules

## Troubleshooting

### Common Issues

**"User not found" (401)**
- Ensure test user exists in database
- Check user_id matches registered user

**CORS errors**
- Verify FRONTEND_ORIGIN matches your frontend URL
- Check browser console for specific error

**Import errors**
- Run from backend/ directory
- Ensure all __init__.py files exist

**Database errors**
- Run `python -c "from src.init_db import init_db; import asyncio; asyncio.run(init_db())"`

## References

- [Plan](./plan.md)
- [Research](./research.md)
- [Data Model](./data-model.md)
- [OpenAPI Contract](./contracts/chat-api.yaml)
- [Feature Spec](./spec.md)
