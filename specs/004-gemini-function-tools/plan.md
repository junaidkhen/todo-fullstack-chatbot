# Implementation Plan: Gemini Function Calling Tools Definition

**Branch**: `004-gemini-function-tools` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-gemini-function-tools/spec.md`

## Summary

This plan defines the implementation of 5 Gemini function calling tool declarations (`add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`) using the `google-genai` Python SDK. Tools will be declared using `types.FunctionDeclaration` with JSON schema parameters, and placeholder implementations will be provided for testing.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: google-genai (unified Google Gen AI SDK), FastAPI, SQLModel
**Storage**: Neon PostgreSQL (via existing SQLModel setup)
**Testing**: pytest, pytest-asyncio
**Target Platform**: Linux server (backend API)
**Project Type**: Web application (frontend/backend split)
**Performance Goals**: Gemini free tier rate limits (5-15 RPM)
**Constraints**: Free tier compliance, <200ms tool execution p95
**Scale/Scope**: Single-user concurrent requests, 5 tools

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-Driven Development Only | ✅ PASS | Spec created at `/specs/004-gemini-function-tools/spec.md` |
| II. Stateless Backend Architecture | ✅ PASS | Tools are pure function declarations; no in-memory state |
| III. Gemini API Free Tier Compliance | ✅ PASS | Using `google-genai` with gemini-2.5-flash model |
| IV. Friendly Conversational Interface | ✅ PASS | Tool descriptions include natural language guidance |
| V. Security Through User Isolation | ✅ PASS | Every tool requires `user_id` as required parameter |
| VI. Type Safety and Validation | ✅ PASS | Using types.FunctionDeclaration with JSON schema |
| VII. Persistent Storage | N/A | Tool declarations don't directly handle storage |

## Project Structure

### Documentation (this feature)

```text
specs/004-gemini-function-tools/
├── plan.md              # This file
├── research.md          # Phase 0: SDK research findings
├── data-model.md        # Phase 1: Tool entity definitions
├── quickstart.md        # Phase 1: Implementation quickstart
├── contracts/           # Phase 1: Tool JSON schemas
│   └── gemini-tools.json
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   └── task.py      # Existing Task model
│   ├── services/
│   │   └── task_tools.py  # NEW: Tool implementations
│   ├── gemini/
│   │   ├── __init__.py    # NEW: Module init
│   │   └── tools.py       # NEW: Tool declarations
│   └── api/
│       └── tasks.py     # Existing API (reference)
└── tests/
    └── unit/
        └── test_gemini_tools.py  # NEW: Tool declaration tests
```

**Structure Decision**: Web application structure. New `gemini/` module under `backend/src/` for Gemini-specific code. Tool implementations in `services/task_tools.py` to separate business logic from Gemini declarations.

## Complexity Tracking

No violations. Implementation is minimal:
- Single new dependency (`google-genai`)
- 5 tool declarations (required by spec)
- Placeholder implementations only (execution logic out of scope)

## Implementation Approach

### Phase 1: Tool Declaration Module

1. **Add google-genai to dependencies**
   - Add `google-genai>=1.0.0` to `backend/requirements.txt`
   - This is the new unified SDK (replaces deprecated `google-generativeai`)

2. **Create tool declarations module** (`backend/src/gemini/tools.py`)
   - Use `types.FunctionDeclaration` for each tool
   - Use `parameters_json_schema` for parameter definitions
   - Return `types.Tool` object containing all 5 declarations

3. **Create tool implementations module** (`backend/src/services/task_tools.py`)
   - Placeholder functions matching tool signatures
   - Type hints for all parameters
   - Return types as TypedDict for JSON consistency

4. **Write unit tests** (`backend/tests/unit/test_gemini_tools.py`)
   - Verify tool declarations load without error
   - Verify all 5 tools are present
   - Verify parameter schemas match spec

### Gemini SDK Integration Pattern

Based on research, the recommended pattern is:

```python
from google.genai import types

# Method 1: Explicit FunctionDeclaration (PREFERRED for control)
function = types.FunctionDeclaration(
    name='add_task',
    description='Use this to create a new todo task...',
    parameters_json_schema={
        'type': 'object',
        'properties': {...},
        'required': [...]
    }
)

tool = types.Tool(function_declarations=[function])

# Method 2: Automatic from Python function (simpler but less control)
def add_task(user_id: str, title: str, description: str = None) -> dict:
    """Use this to create a new todo task..."""
    pass

# Pass directly as tool
config = types.GenerateContentConfig(tools=[add_task])
```

**Decision**: Use Method 1 (explicit `FunctionDeclaration`) for:
- Full control over parameter schemas
- Spec-compliant descriptions
- Clear separation between declaration and implementation

### Tool Execution Mode

The SDK supports two modes:
1. **Automatic** (default): SDK executes functions automatically
2. **Manual**: Returns function calls for external execution

**Decision**: Use manual mode with `automatic_function_calling=disable` because:
- Tool execution needs async database operations
- User ownership validation requires API layer context
- Better observability and error handling

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| SDK Package | `google-genai` | Unified SDK, replaces deprecated `google-generativeai` |
| Declaration Style | Explicit `FunctionDeclaration` | Full schema control, spec-compliant |
| Execution Mode | Manual | Async DB ops, ownership validation needs |
| File Location | `backend/src/gemini/tools.py` | Dedicated module for Gemini code |

## Dependencies

- **External**: `google-genai>=1.0.0`
- **Internal**: Task model from `backend/src/models/task.py`
- **Spec**: Database Schema (Chunk 2) must be complete

## Out of Scope (per spec)

- Tool execution logic (Chunk 4+)
- Conversation history management
- Rate limit handling
- Frontend chat UI
- System prompt engineering

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| SDK version incompatibility | Pin version in requirements.txt |
| Schema validation errors | Unit tests verify all schemas |
| Integer vs string type mismatch | Spec requires integer task_id, verify in tests |

## Next Steps

1. Complete `research.md` with SDK findings
2. Create `data-model.md` with tool entity definitions
3. Generate `contracts/gemini-tools.json` with full schemas
4. Create `quickstart.md` for implementation guide
5. Run `/sp.tasks` to generate tasks.md
