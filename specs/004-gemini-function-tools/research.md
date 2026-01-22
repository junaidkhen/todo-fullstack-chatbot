# Research: Gemini Function Calling Tools

**Feature**: 004-gemini-function-tools | **Date**: 2026-01-16

## Research Questions

### Q1: Which Gemini SDK to use?

**Decision**: Use `google-genai` (the unified Google Gen AI SDK for Python)

**Rationale**:
- The `google-generativeai` package is deprecated and superseded by `google-genai`
- `google-genai` provides a unified interface for both Gemini Developer API and Vertex AI
- Active development with recent updates (version 1.33.0 as of research)
- Better documentation and code examples

**Alternatives Considered**:
- `google-generativeai` (deprecated) - Would work but not recommended for new projects
- `pydantic-ai` - Third-party wrapper, adds unnecessary abstraction layer

### Q2: How to declare function tools?

**Decision**: Use explicit `types.FunctionDeclaration` with `parameters_json_schema`

**Rationale**:
- Full control over parameter schemas (type, description, enum values)
- Matches spec requirement for exact JSON schema format
- Better documentation of tool purpose in descriptions
- Separation of declaration from implementation

**Example Pattern**:
```python
from google.genai import types

function = types.FunctionDeclaration(
    name='add_task',
    description='Use this to create a new todo task for the user. Call when user wants to add, create, or make a new task.',
    parameters_json_schema={
        'type': 'object',
        'properties': {
            'user_id': {
                'type': 'string',
                'description': "The authenticated user's unique ID"
            },
            'title': {
                'type': 'string',
                'description': 'Short title of the task (required)'
            },
            'description': {
                'type': 'string',
                'description': 'Optional longer details or notes about the task'
            }
        },
        'required': ['user_id', 'title']
    }
)

tool = types.Tool(function_declarations=[function])
```

**Alternatives Considered**:
- Automatic function inference (pass Python function directly) - Less control over schema, docstrings become descriptions
- Dict-based declarations - Works but less type-safe than FunctionDeclaration objects

### Q3: Automatic vs Manual function calling?

**Decision**: Use manual function calling with `automatic_function_calling=disable`

**Rationale**:
- Tool execution requires async database operations (SQLModel)
- User ownership validation needs API layer context (user_id from auth)
- Better observability: can log function calls before execution
- Error handling: can catch and format errors before returning to Gemini
- Spec requires ownership validation on every tool call

**Implementation Pattern**:
```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=user_message,
    config=types.GenerateContentConfig(
        tools=[tool],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        )
    )
)

# Manual execution
if response.function_calls:
    for fc in response.function_calls:
        result = await execute_tool(fc.name, fc.args)
        # Feed result back to Gemini
```

**Alternatives Considered**:
- Automatic execution - SDK runs functions directly, but can't do async DB ops or pre-validation

### Q4: How to pass tool results back to Gemini?

**Decision**: Use multi-turn conversation with function call responses

**Rationale**:
- Gemini expects function results in a specific format
- The SDK handles this through conversation history
- Results feed back into the model for natural language response generation

**Pattern**:
```python
from google.genai import types

# After getting function call from model
function_response = types.FunctionResponse(
    name='add_task',
    response={'status': 'created', 'task_id': 5, 'title': 'Buy groceries'}
)

# Feed back to model
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
        types.Content(role='user', parts=[types.Part(text=user_message)]),
        types.Content(role='model', parts=[types.Part(function_call=fc)]),
        types.Content(role='function', parts=[types.Part(function_response=function_response)])
    ],
    config=config
)
```

### Q5: Which Gemini model to use?

**Decision**: Use `gemini-2.5-flash` (or fallback to `gemini-1.5-flash`)

**Rationale**:
- `gemini-2.5-flash` is the latest flash model with function calling support
- Free tier compatible
- Fast response times for chat applications
- Both models support function calling

**Alternatives Considered**:
- `gemini-2.0-pro` - More capable but slower and may hit rate limits faster
- `gemini-1.5-flash` - Fallback if 2.5 has issues

### Q6: How to structure the tools module?

**Decision**: Create dedicated `backend/src/gemini/tools.py` module

**Rationale**:
- Separates Gemini-specific code from business logic
- Easy to test tool declarations in isolation
- Clean import path: `from src.gemini.tools import get_task_tools`

**File Structure**:
```
backend/src/gemini/
├── __init__.py          # Exports get_task_tools
└── tools.py             # FunctionDeclaration definitions
```

### Q7: Return type structure for tools?

**Decision**: Use consistent JSON structure with `status` field

**Rationale**:
- Spec defines exact return formats
- All responses have `status` field for consistency
- Error responses always include `message` field
- Success statuses: "created", "listed", "completed", "deleted", "updated"

**Return Type Examples**:
```python
# Success
{"status": "created", "task_id": 5, "title": "Buy groceries"}

# Error
{"status": "error", "message": "Task not found or does not belong to user"}
```

## SDK Installation

```bash
pip install google-genai
```

Add to `backend/requirements.txt`:
```
google-genai>=1.0.0
```

## Environment Variables

Required:
```
GEMINI_API_KEY=your-api-key-here
```

## Key Findings Summary

| Topic | Decision | Package/Pattern |
|-------|----------|-----------------|
| SDK | google-genai | Unified SDK, replaces deprecated google-generativeai |
| Declaration | FunctionDeclaration | Explicit schema control |
| Execution | Manual | Disable automatic_function_calling |
| Model | gemini-2.5-flash | Free tier, function calling support |
| Return format | JSON with status | Consistent error handling |

## References

- [Google Gen AI Python SDK](https://github.com/googleapis/python-genai)
- [Function Calling Documentation](https://ai.google.dev/docs/function_calling)
- [Phase III Constitution](../../specs/phase3/constitution.md)
