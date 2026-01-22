# Quickstart: Database Models & Schema (Chunk 2)

**Feature**: 003-db-models-schema
**Date**: 2026-01-16

## Prerequisites

- Python 3.12+
- PostgreSQL database (Neon or local)
- Virtual environment activated

## Quick Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Ensure requirements.txt includes:
```
sqlmodel==0.0.22
sqlalchemy==2.0.35
asyncpg==0.30.0
alembic==1.13.1
```

### 2. Set Environment Variable

```bash
# For Neon PostgreSQL
export DATABASE_URL="postgresql://user:password@host.neon.tech/dbname?sslmode=require"

# For local development (SQLite)
export DATABASE_URL="sqlite:///./todo_dev.db"
```

### 3. Initialize Alembic (First Time Only)

```bash
cd backend
alembic init alembic
```

Then configure `alembic/env.py` per the plan.

### 4. Run Migrations

```bash
cd backend
alembic upgrade head
```

### 5. Verify Tables Created

```bash
# For PostgreSQL
psql $DATABASE_URL -c "\dt"

# Expected output:
#  Schema |     Name      | Type  | Owner
# --------+---------------+-------+-------
#  public | conversations | table | user
#  public | messages      | table | user
#  public | tasks         | table | user
#  public | users         | table | user
```

## Quick Usage Examples

### Creating Models in Python

```python
import asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database import async_engine
from src.models import Task, Conversation, Message, MessageRole

async def main():
    async with AsyncSession(async_engine) as session:
        # Create a conversation
        conversation = Conversation(user_id="user-001")
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

        # Add messages
        user_msg = Message(
            user_id="user-001",
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content="Add a task to buy milk"
        )
        session.add(user_msg)

        assistant_msg = Message(
            user_id="user-001",
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content="I've added 'buy milk' to your tasks!"
        )
        session.add(assistant_msg)
        await session.commit()

        # Query messages
        await session.refresh(conversation)
        for msg in conversation.messages:
            print(f"{msg.role.value}: {msg.content}")

asyncio.run(main())
```

### Running Tests

```bash
cd backend
pytest tests/unit/test_models.py -v
```

## Common Commands

| Command | Description |
|---------|-------------|
| `alembic upgrade head` | Apply all migrations |
| `alembic downgrade -1` | Rollback one migration |
| `alembic revision --autogenerate -m "description"` | Generate new migration |
| `alembic current` | Show current migration version |
| `alembic history` | Show migration history |

## Troubleshooting

### Error: asyncpg not found
```bash
pip install asyncpg
```

### Error: Connection refused
Check DATABASE_URL format. For Neon, ensure `?sslmode=require` is present.

### Error: Alembic can't find models
Ensure all models are imported in `alembic/env.py`:
```python
from src.models import Task, User, Conversation, Message
```

### Error: "relation does not exist"
Run migrations:
```bash
alembic upgrade head
```
