# Implementation Plan: Gemini Agent Integration & Runner (Chunk 5)

**Branch**: `006-gemini-agent-runner` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-gemini-agent-runner/spec.md`

## Summary

Implement the Gemini AI agent integration layer that orchestrates AI-powered task management conversations. The agent handles model initialization with `google-generativeai` SDK, constructs prompts from conversation history, executes a multi-turn tool execution loop for function calling, and produces natural language responses. This is a stateless per-request design following Phase III constitutional principles.

## Technical Context

**Language/Version**: Python 3.11+ with type hints
**Primary Dependencies**: google-generativeai (Gemini SDK), FastAPI, SQLModel
**Storage**: AsyncSession from SQLModel for tool execution (existing database.py)
**Testing**: pytest with pytest-asyncio for async agent tests
**Target Platform**: Linux server (FastAPI ASGI application)
**Project Type**: web (backend)
**Performance Goals**: Agent processing under 5 seconds excluding Gemini API latency
**Constraints**: Gemini free tier (5-15 RPM), 100k token context window
**Scale/Scope**: Single-user at a time per request (stateless), conversation history up to 20 messages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase III Constitution Compliance

| Principle | Gate | Status | Evidence |
|-----------|------|--------|----------|
| I. Spec-Driven Development | Feature spec exists | ✅ PASS | `specs/006-gemini-agent-runner/spec.md` exists with full requirements |
| II. Stateless Backend | No in-memory session | ✅ PASS | Agent receives all context per request, no shared state |
| III. Gemini Free Tier | Uses gemini-1.5-flash | ✅ PASS | Configurable via GEMINI_MODEL env, default gemini-1.5-flash |
| IV. Friendly Conversational Interface | System prompt defined | ✅ PASS | TaskBot persona with confirmation/error messaging |
| V. Security Through User Isolation | user_id injected | ✅ PASS | FR-014: user_id injected into every tool call |
| VI. Type Safety | All functions typed | ✅ PASS | Spec defines typed dataclasses (ToolCallRecord, AgentResponse) |
| VII. Persistent Storage | Uses existing DB | ✅ PASS | Tool handlers use AsyncSession for DB operations |

### Universal Principles Compliance

| Principle | Gate | Status |
|-----------|------|--------|
| Type Safety (Python type hints) | All public functions typed | ✅ PASS |
| Clean Architecture | Single responsibility modules | ✅ PASS |
| Quality Standards (no hardcoded secrets) | GEMINI_API_KEY from env | ✅ PASS |

**Constitution Check Result**: ✅ ALL GATES PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/006-gemini-agent-runner/
├── plan.md              # This file
├── spec.md              # Feature specification (exists)
├── research.md          # Phase 0 output - Gemini SDK research
├── data-model.md        # Phase 1 output - Agent entities
├── contracts/           # Phase 1 output - Agent API contracts
│   └── agent-response.json
├── quickstart.md        # Phase 1 output - Implementation guide
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   └── task.py           # Existing: Task, User models
│   ├── services/
│   │   └── agent.py          # NEW: Gemini agent module (this spec)
│   ├── tools/
│   │   ├── __init__.py       # NEW: Tool package init
│   │   ├── declarations.py   # NEW: Gemini tool declarations (from Chunk 3)
│   │   └── handlers.py       # NEW: Tool execution handlers
│   ├── api/
│   │   ├── tasks.py          # Existing: REST CRUD endpoints
│   │   └── chat.py           # NEW: Chat endpoint (Chunk 4, calls agent)
│   ├── database.py           # Existing: AsyncSession provider
│   └── auth/
│       └── jwt.py            # Existing: JWT auth
└── tests/
    └── test_agent.py         # NEW: Agent unit/integration tests
```

**Structure Decision**: Extend existing backend structure with new `services/` and `tools/` modules. Agent logic in `services/agent.py` follows clean separation - agent orchestration is separate from tool execution handlers.

## Complexity Tracking

No constitutional violations identified. The design follows minimal complexity:

- Single agent module with clear responsibilities
- Tool registry pattern for dispatch (no complex abstraction)
- Simple token estimation (chars/4) rather than tiktoken library
- History truncation over summarization for MVP

---

## Phase 0: Research Outputs

See [research.md](./research.md) for:
- google-generativeai SDK async support verification
- Function calling response structure details
- Rate limit error exception types
- Best practices for Gemini function calling

## Phase 1: Design Outputs

See:
- [data-model.md](./data-model.md) - Agent entities (ToolCallRecord, AgentResponse)
- [contracts/agent-response.json](./contracts/agent-response.json) - Response schema
- [quickstart.md](./quickstart.md) - Step-by-step implementation guide

---

## Implementation Tasks Overview

*(Detailed tasks will be generated by `/sp.tasks` command)*

### Task Groups

1. **SDK Setup & Configuration**
   - Install google-generativeai if not present
   - Create `backend/src/services/agent.py` with initialization
   - Define SYSTEM_PROMPT constant
   - Validate GEMINI_API_KEY on startup

2. **Tool Integration**
   - Create `backend/src/tools/declarations.py` with 5 tool declarations
   - Create `backend/src/tools/handlers.py` with execute_tool dispatcher
   - Integrate with existing Task model operations

3. **Agent Runner Implementation**
   - Implement `build_contents_from_history()`
   - Implement `run_gemini_agent()` with tool execution loop
   - Implement `run_gemini_agent_safe()` error wrapper
   - Add logging throughout

4. **Context Management**
   - Implement token estimation
   - Implement history truncation
   - Add max iteration enforcement

5. **Testing**
   - Unit tests for history building
   - Unit tests for tool dispatch
   - Integration tests with mocked Gemini responses
   - Error handling tests (rate limits, timeouts)

---

## Dependencies on Other Chunks

| Chunk | What This Chunk Needs | Status |
|-------|----------------------|--------|
| Chunk 2 (Database) | AsyncSession, Task model | ✅ Exists |
| Chunk 3/4 (Tools) | Tool declarations schema | ✅ Spec exists, need implementation |
| Chunk 4 (FastAPI) | Chat endpoint that calls agent | Separate spec, parallel work |
| Chunk 7 (Conversations) | Fetch history from DB | Parallel work, this chunk accepts history as param |

---

## Risks and Mitigations

1. **Risk**: google-generativeai SDK may not support true async
   **Mitigation**: Research confirmed - use thread pool executor wrapper if needed

2. **Risk**: Rate limits during multi-turn tool execution
   **Mitigation**: Max 5 iterations limit, graceful error response

3. **Risk**: Token estimation inaccuracy causing context overflow
   **Mitigation**: Conservative 90k limit (10k buffer below 100k max)

---

## Follow-up Actions

1. Run `/sp.tasks` to generate detailed implementation tasks
2. Implement Chunk 3/4 tool declarations if not already done
3. Coordinate with Chunk 4 (FastAPI endpoint) for integration
4. Consider ADR for "google-generativeai vs alternative SDKs" decision
