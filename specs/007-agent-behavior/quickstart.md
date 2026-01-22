# Quickstart: Agent Behavior Implementation

**Feature**: Chunk 6 - Agent Behavior | **Date**: 2026-01-17

This guide provides step-by-step instructions for implementing the TaskBot agent behavior system prompt.

---

## Prerequisites

Before implementing this chunk, ensure:

1. **Chunk 4 (Function Tools)** is implemented or stubbed:
   - Tool declarations exist in `backend/src/tools/declarations.py`
   - Tool handlers exist in `backend/src/tools/handlers.py`

2. **Chunk 5 (Agent Runner)** structure exists:
   - `backend/src/services/agent.py` with `run_gemini_agent()` function
   - SYSTEM_PROMPT constant (may be placeholder)

3. **Chunk 8 (Conversation Persistence)** is implemented:
   - History retrieval for context awareness

---

## Step 1: Create Prompts Module (Optional)

For maintainability, extract the system prompt to a dedicated module:

```bash
# Create the prompts module
touch backend/src/services/prompts.py
```

```python
# backend/src/services/prompts.py
"""TaskBot system prompt and agent behavior definitions."""

SYSTEM_PROMPT = """
You are TaskBot, a friendly and helpful Todo manager assistant.

## Your Personality
- Friendly, warm, and encouraging
- Casual but professional
- Comfortable with English/Urdu code-switching (respond in the style the user uses)
- Use simple language, avoid jargon
- Keep responses concise - no walls of text

## Your Capabilities
You help users manage their tasks through natural conversation:
- Add new tasks
- List existing tasks (all, pending, or completed)
- Mark tasks as complete
- Delete tasks
- Update task titles or descriptions

## Conversation Rules

### 1. Always Confirm Actions
After every successful operation, confirm with the task details:
- Add: "Done! Task added: '[title]'"
- Complete: "Nice! Marked '[title]' as complete"
- Delete: "Got it! Deleted '[title]' from your list"
- Update: "Updated! '[old_title]' is now '[new_title]'"
- List (empty): "Abhi tou koi task nahi hai. Kuch add karna hai?"
- List (all done): "Sab tasks complete ho gaye! Great job!"

### 2. Handle Ambiguity
When a user refers to a task vaguely (by name, description, or pronoun):
1. First call list_tasks to see their tasks
2. If exactly one match: proceed with the action
3. If multiple matches: ask "Multiple tasks match '[keyword]'. Which one?" and list them with IDs
4. If no matches: say "Task nahi mila bhai. Show tasks likhein?"

### 3. Language Adaptation
- If user writes in English: respond in English
- If user mixes English/Urdu: respond in similar style
- Common Urdu phrases to use:
  - "Task add ho gaya!" (Task added!)
  - "Task nahi mila bhai" (Task not found)
  - "Kya add karna hai?" (What to add?)
  - "Sab tasks complete ho gaye!" (All tasks completed!)
  - "Ho gaya!" (Done!)
  - "Aur kuch?" (Anything else?)

### 4. Error Messages (Be Friendly)
Instead of technical errors, say:
- Not found: "Task nahi mila bhai. Check your task list?"
- Permission: "Ye task aap ka nahi hai"
- Empty title: "Task ka naam tou batao! Kya add karna hai?"
- Server error: "Kuch gadbad ho gaya - try again please!"
- Rate limit: "Thoda busy hoon - ek second mein try karo"

### 5. Conversational Responses
For greetings and general chat, respond naturally without calling tools:
- "Hello!" → "Hey! Kya hal hai? Need help with tasks?"
- "What can you do?" → "I can help you manage tasks - add, view, complete, delete, update. Try 'add task buy milk'!"
- "Thanks" → "Happy to help! Aur kuch?"

### 6. Context Awareness
Use conversation history to understand references:
- "Add task: call mom" → [added] → "Actually delete it" → understand "it" = "call mom"
- Remember recent task mentions within the conversation

## Intent Recognition Examples

### Adding Tasks
- "add task buy milk" → add_task(title="buy milk")
- "I need to remember to call mom" → add_task(title="call mom")
- "remind me to send the report" → add_task(title="send the report")

### Listing Tasks
- "show my tasks" → list_tasks()
- "show pending tasks" → list_tasks(status="pending")
- "what's left to do?" → list_tasks(status="pending")

### Completing Tasks
- "mark task 3 done" → complete_task(task_id=3)
- "complete the grocery task" → [list first, find match, then complete]

### Deleting Tasks
- "delete task 5" → delete_task(task_id=5)
- "remove the meeting task" → [list first, find match, then delete]

### Updating Tasks
- "rename task 2 to Weekly standup" → update_task(task_id=2, title="Weekly standup")

## What NOT to Do
- Never expose technical error details or stack traces
- Never access tasks belonging to other users
- Never create tasks with empty titles
- Don't be overly verbose - keep responses to 1-2 sentences
- Don't ask for user_id - it's provided automatically

## Note
The user_id is injected into every tool call automatically.
"""
```

---

## Step 2: Update Agent Module

Import and use the system prompt in the agent:

```python
# backend/src/services/agent.py

from .prompts import SYSTEM_PROMPT
# ... or define SYSTEM_PROMPT inline

import google.generativeai as genai
from typing import Optional
from dataclasses import dataclass

@dataclass
class AgentResponse:
    text: str
    tool_calls: list

async def run_gemini_agent(
    user_id: str,
    history: list[dict],
    new_message: str,
    db_session
) -> AgentResponse:
    """Run the Gemini agent with TaskBot system prompt."""

    # Initialize model with system instruction
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT,
        tools=[...]  # Tool declarations from Chunk 4
    )

    # Build conversation contents from history
    contents = build_contents_from_history(history)
    contents.append({"role": "user", "parts": [new_message]})

    # Call Gemini
    response = await model.generate_content_async(contents)

    # Handle tool calls and return response
    # ... (implementation from Chunk 5)
```

---

## Step 3: Ensure Error Messages Match

Update tool handlers to return error messages matching the prompt templates:

```python
# backend/src/tools/handlers.py

ERROR_MESSAGES = {
    "task_not_found": "Task nahi mila bhai. Check your task list?",
    "empty_title": "Task ka naam tou batao! Kya add karna hai?",
    "permission_denied": "Ye task aap ka nahi hai",
    "database_error": "Kuch gadbad ho gaya - try again please!",
    "already_completed": "Ye task tou pehle se complete hai!",
}

async def complete_task(user_id: str, task_id: int, session) -> dict:
    """Complete a task with friendly error handling."""
    task = await get_task_by_id(task_id, session)

    if not task:
        return {"status": "error", "message": ERROR_MESSAGES["task_not_found"]}

    if task.user_id != user_id:
        return {"status": "error", "message": ERROR_MESSAGES["permission_denied"]}

    if task.is_completed:
        return {"status": "error", "message": ERROR_MESSAGES["already_completed"]}

    # ... complete the task
    return {"status": "success", "task": {"id": task.id, "title": task.title}}
```

---

## Step 4: Test Intent Recognition

Create a test file to verify intent recognition:

```python
# backend/tests/test_agent_behavior.py

import pytest
from src.services.agent import run_gemini_agent

@pytest.mark.asyncio
async def test_add_intent_direct():
    """Test direct 'add task X' intent recognition."""
    response = await run_gemini_agent(
        user_id="test-user",
        history=[],
        new_message="add task buy milk",
        db_session=mock_session
    )
    # Verify add_task was called with title="buy milk"
    assert any(tc.name == "add_task" for tc in response.tool_calls)

@pytest.mark.asyncio
async def test_add_intent_implicit():
    """Test implicit add intent ('I need to remember X')."""
    response = await run_gemini_agent(
        user_id="test-user",
        history=[],
        new_message="I need to remember to call mom",
        db_session=mock_session
    )
    assert any(tc.name == "add_task" for tc in response.tool_calls)

@pytest.mark.asyncio
async def test_greeting_no_tool():
    """Test that greetings don't trigger tool calls."""
    response = await run_gemini_agent(
        user_id="test-user",
        history=[],
        new_message="hello",
        db_session=mock_session
    )
    assert len(response.tool_calls) == 0
    assert "help with tasks" in response.text.lower() or "kya hal hai" in response.text.lower()
```

---

## Step 5: Manual Testing Checklist

Test the following scenarios manually:

### Intent Recognition
- [ ] "add task buy milk" → Creates task
- [ ] "I need to remember to call mom" → Creates task
- [ ] "show my tasks" → Lists all tasks
- [ ] "what's left to do?" → Lists pending tasks
- [ ] "mark task 3 done" → Completes task 3
- [ ] "delete the meeting task" → Lists, finds, deletes

### Error Handling
- [ ] Complete non-existent task → "Task nahi mila bhai"
- [ ] Add empty task → "Task ka naam tou batao!"
- [ ] Delete someone else's task → "Ye task aap ka nahi hai"

### Language Adaptation
- [ ] English input → English response
- [ ] "Task add karo: gym jaana" → Mixed response

### Conversational
- [ ] "hello" → Friendly greeting, no tool call
- [ ] "what can you do?" → Capability explanation
- [ ] "thanks" → Acknowledgment

### Context Awareness
- [ ] Add task → "delete it" → Deletes the just-added task
- [ ] Multiple tasks with same word → Asks for clarification

---

## Verification

After implementation, verify:

1. **System prompt is loaded**: Check Gemini model initialization includes `system_instruction`
2. **Error messages match**: Tool handlers return pre-defined friendly messages
3. **No technical leaks**: Error responses never include stack traces or HTTP codes
4. **Urdu rendering**: Test Urdu phrases display correctly in chat UI
5. **Token budget**: System prompt + 20 messages + response fits in context window

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Model ignores prompt rules | Restructure prompt with clearer sections; add more examples |
| Tool not called for implicit intent | Add more intent examples to prompt |
| Technical error exposed | Check tool handler returns friendly message |
| Pronoun resolution fails | Ensure conversation history is included in context |
| Response too verbose | Add "Keep responses concise" to personality section |
