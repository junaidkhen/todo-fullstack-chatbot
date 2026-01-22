# Data Model: Agent Behavior & Intent Mapping

**Feature**: Chunk 6 - Agent Behavior | **Date**: 2026-01-17

## Overview

This document defines the conceptual entities for the agent behavior layer. Unlike database-focused chunks, this is primarily about **prompt configuration** entities represented as string constants and embedded patterns in the system prompt.

---

## Entity: SYSTEM_PROMPT

**Purpose**: Complete instruction set for TaskBot agent behavior

**Type**: String constant (Python)

**Location**: `backend/src/services/agent.py` or `backend/src/services/prompts.py`

**Structure**:
```
┌─────────────────────────────────────┐
│ SYSTEM_PROMPT                       │
├─────────────────────────────────────┤
│ 1. Persona Section                  │
│    - Identity (TaskBot)             │
│    - Personality traits             │
│    - Language preferences           │
│                                     │
│ 2. Capabilities Section             │
│    - 5 task operations              │
│                                     │
│ 3. Conversation Rules Section       │
│    - 6 subsections:                 │
│      • Confirm Actions              │
│      • Handle Ambiguity             │
│      • Language Adaptation          │
│      • Error Messages               │
│      • Conversational Responses     │
│      • Context Awareness            │
│                                     │
│ 4. Constraints Section              │
│    - What NOT to Do                 │
│                                     │
│ 5. Notes Section                    │
│    - user_id injection              │
└─────────────────────────────────────┘
```

**Estimated Size**: ~1500 tokens / ~6000 characters

---

## Entity: Intent

**Purpose**: Conceptual classification of user message purpose (not a database model)

**Values**:
| Intent | Description | Tool(s) Called |
|--------|-------------|----------------|
| ADD | User wants to create a new task | `add_task(user_id, title)` |
| LIST | User wants to view their tasks | `list_tasks(user_id, status?)` |
| COMPLETE | User wants to mark a task done | `complete_task(user_id, task_id)` |
| DELETE | User wants to remove a task | `delete_task(user_id, task_id)` |
| UPDATE | User wants to modify a task | `update_task(user_id, task_id, title?, description?)` |
| GREETING | User says hello/hi | None (conversational response) |
| HELP | User asks what the bot can do | None (capability explanation) |
| ACKNOWLEDGMENT | User says thanks | None (friendly response) |

**Detection**: Handled by Gemini model via function calling - not explicit code

---

## Entity: TaskReference

**Purpose**: How users identify a task in their message

**Types**:
| Reference Type | Example | Resolution Strategy |
|----------------|---------|---------------------|
| Direct ID | "task 3", "task #5" | Extract integer, use directly |
| By Name | "the meeting task", "grocery task" | Call list_tasks, search by keyword |
| Pronoun | "it", "that one" | Check conversation history |
| Positional | "the first one", "my last task" | Call list_tasks, select by position |

**Resolution Flow**:
```
User Message
    │
    ▼
┌──────────────────┐     ┌──────────────────┐
│ Contains task_id?│─Yes─▶│ Use task_id      │
└──────────────────┘     └──────────────────┘
    │ No
    ▼
┌──────────────────┐     ┌──────────────────┐
│ Contains keyword?│─Yes─▶│ list_tasks()     │
└──────────────────┘     │ search for match │
    │ No                 └──────────────────┘
    ▼
┌──────────────────┐     ┌──────────────────┐
│ Uses pronoun?    │─Yes─▶│ Check history    │
└──────────────────┘     │ find last task   │
    │ No                 └──────────────────┘
    ▼
┌──────────────────┐
│ Ask for clarity  │
└──────────────────┘
```

---

## Entity: ConfirmationTemplate

**Purpose**: Success message patterns after tool execution

**Instances**:
| Action | Template | Variables |
|--------|----------|-----------|
| ADD | "Done! Task added: '{title}'" | title |
| LIST_ALL | "You have {count} tasks:" | count |
| LIST_EMPTY | "Abhi tou koi task nahi hai. Kuch add karna hai?" | - |
| LIST_PENDING | "You have {count} pending tasks:" | count |
| LIST_ALL_DONE | "Sab tasks complete ho gaye! Great job!" | - |
| COMPLETE | "Nice! Marked '{title}' as complete" | title |
| DELETE | "Got it! Deleted '{title}' from your list" | title |
| UPDATE | "Updated! '{old_title}' is now '{new_title}'" | old_title, new_title |

---

## Entity: ErrorTemplate

**Purpose**: User-friendly error message patterns

**Instances**:
| Error Code | Template | Romanized Meaning |
|------------|----------|-------------------|
| TASK_NOT_FOUND | "Task nahi mila bhai. Check your task list?" | Task not found |
| EMPTY_TITLE | "Task ka naam tou batao! Kya add karna hai?" | Tell the task name! |
| PERMISSION_DENIED | "Ye task aap ka nahi hai" | This task isn't yours |
| DATABASE_ERROR | "Kuch gadbad ho gaya - try again please!" | Something went wrong |
| RATE_LIMIT | "Thoda busy hoon - ek second mein try karo" | A bit busy - try in a sec |
| INVALID_ID | "Task ID samajh nahi aaya - number use karo" | Didn't understand ID |
| ALREADY_COMPLETED | "Ye task tou pehle se complete hai!" | This task is already done |
| ALREADY_DELETED | "Ye task already delete ho chuka hai" | This task is already deleted |

---

## Entity: ConversationalResponse

**Purpose**: Non-tool responses for greetings and help

**Instances**:
| Trigger | Response Pattern |
|---------|------------------|
| "hello" / "hi" / "hey" | "Hey! Kya hal hai? Need help with tasks?" |
| "what can you do?" | "I can help you manage tasks - add, view, complete, delete, update. Try 'add task buy milk'!" |
| "thanks" / "thank you" | "Happy to help! Aur kuch?" |
| "bye" / "goodbye" | "Bye! Take care!" |

---

## Relationships

```
SYSTEM_PROMPT
    │
    ├── contains → Intent patterns (examples)
    ├── contains → ConfirmationTemplates
    ├── contains → ErrorTemplates
    └── contains → ConversationalResponses

Intent
    │
    └── resolved via → TaskReference (for COMPLETE, DELETE, UPDATE)

TaskReference
    │
    └── uses → Conversation History (for pronoun resolution)
```

---

## Validation Rules

1. **SYSTEM_PROMPT length**: Must be < 2000 tokens to leave room for history
2. **Intent patterns**: Each intent must have 2+ example phrasings
3. **Error templates**: Must use romanized Urdu where specified
4. **No technical jargon**: Error templates must not contain HTTP codes, exception types, or stack traces

---

## Testing Considerations

| Entity | Test Type | Example |
|--------|-----------|---------|
| Intent detection | Manual + Unit | "add task X" → ADD intent |
| Confirmation format | Unit | Verify message includes task title |
| Error message | Unit | Verify no technical details exposed |
| Pronoun resolution | Integration | "add task X" → "delete it" works |
