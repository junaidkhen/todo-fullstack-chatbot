# Research: Gemini Agent Integration & Runner

**Feature**: 006-gemini-agent-runner | **Date**: 2026-01-17

## Research Questions

### Q1: google-genai SDK async support verification

**Decision**: The `google-genai` SDK supports async via `client.aio.models.generate_content()`

**Rationale**:
- The SDK provides an async client interface through the `aio` namespace
- Import pattern: `from google import genai; client = genai.Client(); response = await client.aio.models.generate_content(...)`
- Alternative: Use sync `client.models.generate_content()` with `asyncio.to_thread()` if async API has issues
- The spec mentions `generate_content_async` but the google-genai SDK uses `client.aio.models.generate_content()` instead

**Verification Pattern**:
```python
from google import genai
import asyncio

async def test_async_gemini():
    client = genai.Client()
    response = await client.aio.models.generate_content(
        model='gemini-2.5-flash',
        contents='Hello, world!'
    )
    print(response.text)

asyncio.run(test_async_gemini())
```

**Note**: The spec references `google.generativeai` which is the deprecated SDK. We use `google-genai` (unified SDK) per Chunk 4 research decisions.

### Q2: Function calling response structure

**Decision**: Function calls are accessed via `response.candidates[0].content.parts[*].function_call`

**Rationale**:
- Gemini returns function calls in the `parts` array of the response content
- Each function call has `name` and `args` attributes
- The `args` is a dict-like object (can be converted with `dict(fc.args)`)

**Response Structure**:
```python
# Check for function calls
response = await client.aio.models.generate_content(...)

if response.function_calls:
    for fc in response.function_calls:
        fn_name = fc.name
        fn_args = dict(fc.args)  # Convert to regular dict
        # Execute tool...
```

**Alternative Access**:
```python
# Lower-level access
for part in response.candidates[0].content.parts:
    if hasattr(part, 'function_call'):
        fc = part.function_call
        # Process function call...
```

### Q3: Rate limit and error exception types

**Decision**: Use `google.api_core.exceptions` for error handling

**Rationale**:
- `google.api_core.exceptions.ResourceExhausted` for rate limits (HTTP 429)
- `google.api_core.exceptions.ServiceUnavailable` for server errors (HTTP 503)
- `google.api_core.exceptions.DeadlineExceeded` for timeouts
- `google.api_core.exceptions.InvalidArgument` for malformed requests

**Error Handling Pattern**:
```python
from google.api_core.exceptions import (
    ResourceExhausted,
    ServiceUnavailable,
    DeadlineExceeded,
    InvalidArgument
)

try:
    response = await client.aio.models.generate_content(...)
except ResourceExhausted:
    # Rate limit hit - return friendly message
    return AgentResponse(text="I'm a bit busy, please try again!", tool_calls=[])
except ServiceUnavailable:
    # Server error
    return AgentResponse(text="Having trouble connecting...", tool_calls=[])
except DeadlineExceeded:
    # Timeout
    return AgentResponse(text="Request took too long...", tool_calls=[])
```

### Q4: System prompt configuration

**Decision**: Use `system_instruction` in `GenerateContentConfig`

**Rationale**:
- The google-genai SDK uses `config.system_instruction` to set the system prompt
- This is passed as a string to the model configuration
- The system instruction is prepended to every request automatically

**Configuration Pattern**:
```python
from google.genai import types

config = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    tools=[tool],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
)

response = await client.aio.models.generate_content(
    model='gemini-2.5-flash',
    contents=contents,
    config=config
)
```

### Q5: Feeding function results back to Gemini

**Decision**: Use `types.Content` with `role='function'` containing `FunctionResponse`

**Rationale**:
- After executing a function, results must be fed back in a specific format
- The conversation continues with the function result appended
- Gemini then generates a natural language response based on the result

**Pattern**:
```python
from google.genai import types

# After getting function call and executing
function_response = types.FunctionResponse(
    name='add_task',
    response={'status': 'created', 'task_id': 5, 'title': 'Buy groceries'}
)

# Build updated contents
contents = [
    types.Content(role='user', parts=[types.Part(text=user_message)]),
    types.Content(role='model', parts=[types.Part(function_call=function_call)]),
    types.Content(role='function', parts=[types.Part(function_response=function_response)])
]

# Get final response
final_response = await client.aio.models.generate_content(
    model='gemini-2.5-flash',
    contents=contents,
    config=config
)
```

### Q6: History content format

**Decision**: Convert conversation history to `types.Content` objects with proper role mapping

**Rationale**:
- User messages use `role='user'`
- Assistant messages use `role='model'` (Gemini's terminology)
- Parts contain text strings for simple messages
- Function calls/responses are special part types

**Conversion Pattern**:
```python
def build_contents_from_history(history: list[dict]) -> list[types.Content]:
    contents = []
    for msg in history:
        role = 'model' if msg['role'] == 'assistant' else 'user'
        contents.append(types.Content(
            role=role,
            parts=[types.Part(text=msg['content'])]
        ))
    return contents
```

### Q7: Best practices for tool execution loop

**Decision**: Implement iterative loop with max iterations and proper content accumulation

**Best Practices**:
1. **Max iterations**: Cap at 5 to prevent infinite loops
2. **Content accumulation**: Append model response and function results to contents each iteration
3. **Early termination**: Exit loop when response has no function calls
4. **Error isolation**: Catch tool execution errors and return error result to Gemini
5. **User ID injection**: Always inject user_id into tool args for security
6. **Logging**: Log each function call and result for debugging

**Loop Pattern**:
```python
async def run_agent(user_id, contents, config, max_iterations=5):
    tool_calls_executed = []

    for iteration in range(max_iterations):
        response = await client.aio.models.generate_content(...)

        if not response.function_calls:
            # No function calls - return final text
            return AgentResponse(text=response.text, tool_calls=tool_calls_executed)

        # Process function calls
        function_parts = []
        for fc in response.function_calls:
            args = dict(fc.args)
            args['user_id'] = user_id  # Security injection

            result = await execute_tool(fc.name, args)
            tool_calls_executed.append(ToolCallRecord(fc.name, args, result))

            function_parts.append(types.Part(
                function_response=types.FunctionResponse(name=fc.name, response=result)
            ))

        # Append to conversation
        contents.append(response.candidates[0].content)
        contents.append(types.Content(role='function', parts=function_parts))

    # Max iterations reached
    return AgentResponse(
        text="I need to pause. Please try again.",
        tool_calls=tool_calls_executed
    )
```

## SDK Installation

Already specified in Chunk 4 research:
```bash
pip install google-genai
```

`backend/requirements.txt`:
```
google-genai>=1.0.0
```

## Environment Variables

Required (from Constitution):
```
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.5-flash  # Optional, defaults to gemini-1.5-flash
MAX_TOOL_ITERATIONS=5  # Optional, defaults to 5
MAX_HISTORY_MESSAGES=20  # Optional, defaults to 20
```

## Key Findings Summary

| Topic | Decision | Pattern |
|-------|----------|---------|
| Async support | `client.aio.models.generate_content()` | Use `aio` namespace |
| Function calls | `response.function_calls` | Iterate and extract name/args |
| Error handling | `google.api_core.exceptions` | Catch specific exception types |
| System prompt | `config.system_instruction` | Pass in GenerateContentConfig |
| Function results | `types.FunctionResponse` | Append to contents with role='function' |
| History format | `types.Content` with role mapping | 'user'/'model' roles |
| Loop pattern | Max 5 iterations | Accumulate contents, exit on text-only |

## Clarifications Resolved

| Original Unknown | Resolution |
|-----------------|------------|
| Async API method | Use `client.aio.models.generate_content()` not `generate_content_async()` |
| Response structure | Access via `response.function_calls` or iterate `response.candidates[0].content.parts` |
| Error exceptions | Use `google.api_core.exceptions` module |
| System instruction | Passed in `GenerateContentConfig.system_instruction` |

## References

- [Google Gen AI Python SDK](https://github.com/googleapis/python-genai)
- [Function Calling Documentation](https://ai.google.dev/docs/function_calling)
- [Chunk 4 Research](../004-gemini-function-tools/research.md)
- [Phase III Constitution](../../specs/phase3/constitution.md)
