# Research: Agent Behavior & Natural Language Understanding Rules

**Feature**: Chunk 6 - Agent Behavior | **Date**: 2026-01-17

## Overview

This document consolidates research findings for designing the TaskBot system prompt with natural language understanding rules, intent mapping, and conversational behavior patterns.

---

## Research Task 1: Gemini System Prompt Best Practices

### Question
How should we structure system prompts for Gemini function calling models to maximize instruction adherence?

### Findings

**Source**: Google Gemini API documentation and function calling best practices

1. **Structured Sections**: Use clear headers (##) to separate different instruction domains
2. **Persona First**: Lead with the agent's identity and personality
3. **Explicit Examples**: Provide concrete input → output examples for complex behaviors
4. **Negative Examples**: Include "What NOT to Do" section for constraints
5. **Brevity**: Keep instructions concise; verbose prompts reduce adherence
6. **Function Context**: The model uses tool declarations for understanding capabilities, so the system prompt should focus on _when_ and _how_ to use tools, not re-describing them

### Decision
**Use structured sections**: Persona → Capabilities → Conversation Rules → Constraints

**Rationale**: Mirrors successful patterns from Gemini function calling examples; separates concerns for maintainability

---

## Research Task 2: Intent Recognition Patterns for Task Management

### Question
What natural language phrasings should trigger each task operation?

### Findings

**Source**: Analysis of task management NLU patterns (from TodoMVC UX studies, voice assistant designs)

#### ADD Intent Patterns
- Direct: "add task X", "create task X", "new task X"
- Implicit: "I need to remember X", "remind me to X", "don't let me forget X"
- List metaphor: "put X on my list", "add X to my list"

#### LIST Intent Patterns
- Direct: "show my tasks", "list tasks", "what are my tasks?"
- Metaphor: "what's on my list?", "what do I have to do?"
- Status-filtered: "show pending", "what's left?", "show completed"

#### COMPLETE Intent Patterns
- Direct: "mark task N done", "complete task N", "done with task N"
- Natural: "I finished X", "X is done", "completed X"
- Pronoun: "mark it done" (requires context)

#### DELETE Intent Patterns
- Direct: "delete task N", "remove task N"
- Metaphor: "cancel X", "forget about X", "take X off my list"

#### UPDATE Intent Patterns
- Direct: "rename task N to X", "update task N"
- Change: "change X to Y", "modify the X task"

### Decision
**Include 2-3 examples per intent in system prompt**

**Rationale**: Covering major variation patterns without overloading the prompt

---

## Research Task 3: Urdu/English Code-Switching Patterns

### Question
What authentic bilingual phrasings should TaskBot use for confirmations and errors?

### Findings

**Source**: Pakistani English/Urdu code-switching patterns in informal communication

#### Common Romanized Urdu Phrases for TaskBot
- Confirmations:
  - "Ho gaya!" (Done!)
  - "Zaroor!" (Sure!)
  - "Bilkul!" (Absolutely!)
  - "Sab set hai" (All set)
  - "Aur kuch?" (Anything else?)

- Errors/Not Found:
  - "Task nahi mila bhai" (Task not found, bro)
  - "Ye task aap ka nahi hai" (This task isn't yours)
  - "Kuch gadbad ho gaya" (Something went wrong)

- Questions:
  - "Kya add karna hai?" (What to add?)
  - "Kya hal hai?" (How are you?)

- Empty States:
  - "Abhi tou koi task nahi hai" (No tasks right now)
  - "Sab tasks complete ho gaye!" (All tasks completed!)

#### Language Matching Rule
- If user writes in English: respond in English
- If user mixes English/Urdu: match their style
- Default to English with occasional Urdu flavor

### Decision
**Use romanized Urdu phrases in confirmation/error templates**

**Rationale**: Aligns with Phase III constitution principle IV (Friendly Conversational Interface); authentic to Pakistani English usage

---

## Research Task 4: Multi-Step Reasoning in Prompts

### Question
How do we instruct the model to chain tool calls for ambiguous task references?

### Findings

**Source**: Gemini function calling patterns for multi-turn tool execution

#### Challenge
User says "delete the meeting task" but we need the task_id. The model must:
1. Call list_tasks() to get all tasks
2. Find the task matching "meeting"
3. Call delete_task(task_id=matched_id)

#### Solution: Explicit Reasoning Instructions
```
When a user refers to a task vaguely (by name, description, or pronoun):
1. First call list_tasks to see their tasks
2. If exactly one match: proceed with the action
3. If multiple matches: ask which one they mean
4. If no matches: say "Task nahi mila bhai"
```

#### Pronoun Resolution
The model naturally uses conversation history for pronoun resolution when we include:
```
Use conversation history to understand references:
- "Add task: call mom" → [added] → "Actually delete it" → understand "it" = "call mom"
```

### Decision
**Embed explicit reasoning steps in Conversation Rules section**

**Rationale**: Clear step-by-step instructions improve multi-step tool chaining accuracy

---

## Research Task 5: Error Message Design

### Question
How should errors be presented to maintain friendly tone?

### Findings

**Source**: UX error message best practices, conversational UI design patterns

#### Principles
1. **Never expose technical details**: No stack traces, exception types, or status codes
2. **Use natural language**: "Something went wrong" not "500 Internal Server Error"
3. **Suggest next action**: "Check your list?" gives user a path forward
4. **Match tone**: Use same casual/friendly style as success messages
5. **Be brief**: 1 sentence max, no paragraph explanations

#### Error Mapping
| Technical Error | User-Facing Message |
|-----------------|---------------------|
| 404 Task not found | "Task nahi mila bhai. Check your task list?" |
| 403 Permission denied | "Ye task aap ka nahi hai" |
| 400 Empty title | "Task ka naam tou batao! Kya add karna hai?" |
| 500 Database error | "Kuch gadbad ho gaya - try again please!" |
| 429 Rate limit | "Thoda busy hoon - ek second mein try karo" |

### Decision
**Pre-define all error messages in system prompt**

**Rationale**: Ensures consistency; prevents model from generating verbose or technical errors

---

## Research Summary

| Topic | Decision | Confidence |
|-------|----------|------------|
| Prompt structure | Structured sections (Persona → Rules → Constraints) | High |
| Intent examples | 2-3 per intent type, natural language format | High |
| Language style | Romanized Urdu/English code-switching | High |
| Multi-step reasoning | Explicit step-by-step instructions in prompt | Medium-High |
| Error messages | Pre-defined templates, no technical jargon | High |

---

## Open Questions Resolved

1. ~~How does Gemini handle pronoun resolution?~~ → Uses conversation history natively
2. ~~Should we use a separate intent classifier?~~ → No, Gemini's function calling handles this
3. ~~Max prompt length recommendation?~~ → ~1500 tokens for system prompt, leaves room for history
4. ~~Urdu script or romanized?~~ → Romanized (spec requirement, cross-platform compatibility)

---

## Appendix: Sample System Prompt Skeleton

```text
You are TaskBot, a friendly and helpful Todo manager assistant.

## Your Personality
[Friendly, casual, bilingual...]

## Your Capabilities
[Add, list, complete, delete, update tasks]

## Conversation Rules
### 1. Always Confirm Actions
[Templates...]

### 2. Handle Ambiguity
[Multi-step reasoning steps...]

### 3. Language Adaptation
[Match user's style...]

### 4. Error Messages
[Friendly templates...]

### 5. Conversational Responses
[Greetings, help...]

### 6. Context Awareness
[Pronoun resolution...]

## What NOT to Do
[Constraints...]

## Note
The user_id is provided automatically - never ask for it.
```
