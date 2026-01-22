---
id: 0002
title: Conversation Persistence Implementation Plan
stage: plan
date: 2026-01-17
surface: agent
model: claude-opus-4-5-20251101
feature: 008-conversation-persistence
branch: 010-deliverables-repo-structure
user: user
command: /sp.plan
labels: ["planning", "persistence", "database", "async", "conversation"]
links:
  spec: specs/008-conversation-persistence/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/008-conversation-persistence/research.md
  - specs/008-conversation-persistence/data-model.md
  - specs/008-conversation-persistence/contracts/persistence-api.md
  - specs/008-conversation-persistence/plan.md
  - specs/008-conversation-persistence/quickstart.md
  - CLAUDE.md
tests:
  - N/A (planning phase - no code written)
---

## Prompt

chunk-7
You are strictly following the Constitution of Phase-III

And spec: [# Feature Specification: Conversation Persistence Logic (Chunk 7)

**Feature Branch**: `008-conversation-persistence`
**Created**: 2026-01-16
**Status**: Draft
**Input**: Define DB operations for creating/fetching/storing conversation history in stateless way.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Get or Create Conversation (Priority: P1)

As a chat endpoint handler, I need to retrieve an existing conversation or create a new one so that user messages are always associated with a valid conversation context.

**Why this priority**: This is the entry point for all conversation operations. Without the ability to get or create conversations, no messages can be stored or retrieved.

**Independent Test**: Can be fully tested by calling `get_or_create_conversation` with a user_id and no conversation_id, verifying a new conversation is created, then calling again with the returned conversation_id to verify the existing conversation is retrieved.

... [full spec content] ...

, + reference Chunk 2]

Generate PLAN for Chunk 7: Conversation Persistence

Output:
# Chunk 7 Implementation Plan

1. Create persistence.py or db_ops.py
2. Implement get_or_create_conversation
3. Implement fetch_history (limit messages)
4. Implement store_user_message / store_assistant_response
5. Integrate with agent runner (Chunk 5) and endpoint (Chunk 4)
6. Test: Simulate full chat cycle (create conv -> store msgs -> fetch)

## Response snapshot

Generated comprehensive implementation plan for Chunk 7 (Conversation Persistence Logic) following the Phase III constitution and spec-driven development workflow.

**Key deliverables created:**

1. **research.md** - 9 research decisions documented:
   - Database models need to be created (not yet implemented)
   - Persistence module location: `backend/src/persistence.py`
   - Async session management via dependency injection
   - tool_calls stored as JSON string
   - User isolation enforced on ALL functions
   - fetch_history uses subquery for ordering
   - Graceful error handling (empty list for reads, ValueError for writes)
   - Server timestamps via SQLAlchemy func.now()
   - MessageRole enum with "user" and "assistant" values

2. **data-model.md** - Entity definitions:
   - MessageRole enum
   - Conversation model (id, user_id, created_at, updated_at, messages relationship)
   - Message model (id, conversation_id, user_id, role, content, tool_calls, created_at)
   - ERD and relationship documentation

3. **contracts/persistence-api.md** - Function contracts:
   - `get_or_create_conversation(session, user_id, conversation_id)` -> Conversation
   - `fetch_history(session, conversation_id, user_id, limit=30)` -> list[dict]
   - `store_user_message(session, conversation_id, user_id, content)` -> Message
   - `store_assistant_response(session, conversation_id, user_id, content, tool_calls)` -> Message

4. **plan.md** - Implementation plan:
   - Technical context (Python 3.11+, SQLModel, Neon PostgreSQL)
   - Constitution check (all gates passed)
   - 4 implementation components with acceptance criteria
   - Implementation order and dependencies
   - Risks and mitigations

5. **quickstart.md** - Ready-to-implement code:
   - Full model implementations
   - Complete persistence function code
   - Test file with all acceptance scenarios
   - Verification commands

6. **CLAUDE.md** - Updated agent context:
   - Added Chunk 7 to Active Technologies
   - Updated Recent Changes

## Outcome

- Impact: Complete planning artifacts for Chunk 7 implementation
- Tests: N/A (planning phase - code implementation pending)
- Files: 5 new spec files + 1 updated (CLAUDE.md)
- Next prompts: /sp.tasks to generate implementation tasks, then /sp.implement
- Reflection: Research phase identified that Conversation/Message models from Chunk 2 spec are NOT yet implemented in codebase - this is a prerequisite that must be done first

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully
- Graders run and results (PASS/FAIL): PASS - all constitution gates satisfied
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Implement models first, then persistence functions
