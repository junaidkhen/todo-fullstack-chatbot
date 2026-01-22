# Implementation Plan: Agent Behavior & Natural Language Understanding Rules (Chunk 6)

**Branch**: `007-agent-behavior` | **Date**: 2026-01-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification for "Chunk 6: Agent Behavior & Natural Language Understanding Rules"

## Summary

Implement the behavioral rules and natural language understanding patterns for the Gemini AI agent. This chunk focuses on **prompt engineering** - defining the system prompt text that instructs the Gemini model on how to:

1. Recognize intents from natural language variations
2. Map recognized intents to tool calls
3. Handle ambiguous task references via multi-step reasoning
4. Provide friendly, localized confirmation and error messages
5. Adapt language style (English/Urdu code-switching)
6. Resolve pronouns and contextual references from conversation history

This is primarily a **prompt configuration** task with the deliverable being a refined system prompt constant and intent mapping documentation integrated into the Chunk 5 agent module.

## Technical Context

**Language/Version**: Python 3.12 (prompt text is language-agnostic but integrated into Python module)
**Primary Dependencies**: google-generativeai (via Chunk 5 agent), existing tool declarations (Chunk 4)
**Storage**: N/A (prompt text is code constant, not database)
**Testing**: Manual verification via sample message tests; pytest for regression tests
**Target Platform**: Linux server / Docker (same as Chunk 5)
**Project Type**: Web application (backend)
**Performance Goals**: No additional latency (prompt engineering is compile-time, not runtime)
**Constraints**: System prompt must fit within Gemini context window with room for conversation history
**Scale/Scope**: Single system prompt constant; intent mapping documentation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase III Constitution Compliance

| Principle | Gate | Status | Evidence |
|-----------|------|--------|----------|
| I. Spec-Driven Development | Feature spec exists | ✅ PASS | `specs/007-agent-behavior/spec.md` exists with full requirements |
| II. Stateless Backend | No in-memory state | ✅ PASS | Prompt is a constant; no state stored between requests |
| III. Gemini Free Tier | Uses gemini-1.5-flash | ✅ PASS | Prompt designed for function calling models (no change from Chunk 5) |
| IV. Friendly Conversational Interface | Defined in spec | ✅ PASS | Spec defines TaskBot persona, confirmation templates, error messages |
| V. Security Through User Isolation | user_id in tool calls | ✅ PASS | FR-014: user_id injection in every tool call (from Chunk 5) |
| VI. Type Safety | All functions typed | ✅ PASS | No new functions; prompt is string constant |
| VII. Persistent Storage | Conversation history | ✅ PASS | Uses conversation history (Chunk 8) for pronoun resolution |

### Universal Principles Compliance

| Principle | Gate | Status |
|-----------|------|--------|
| Type Safety | N/A for prompt text | ✅ PASS |
| Clean Architecture | Prompt separate from agent logic | ✅ PASS |
| Quality Standards | No hardcoded secrets in prompt | ✅ PASS |

**Constitution Check Result**: ✅ ALL GATES PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/007-agent-behavior/
├── spec.md              # Feature specification (exists)
├── plan.md              # This file
├── research.md          # Phase 0 output - intent mapping best practices
├── data-model.md        # Phase 1 output - intent/tool mapping schema
├── contracts/           # Phase 1 output - system prompt contract
│   └── system-prompt.md # Full system prompt text
├── quickstart.md        # Phase 1 output - prompt integration guide
└── tasks.md             # Phase 2 output (/sp.tasks - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── services/
│   │   ├── agent.py             # MODIFY: Update SYSTEM_PROMPT constant
│   │   └── prompts.py           # NEW: Optional - dedicated prompts module
│   └── tools/
│       └── handlers.py          # EXISTING: Tool handlers with friendly error messages
└── tests/
    └── test_agent_behavior.py   # NEW: Intent recognition and response tests
```

**Structure Decision**: Web application pattern. Minimal code changes - the system prompt constant in `services/agent.py` is the primary deliverable. Option to extract to dedicated `prompts.py` module for maintainability.

## Complexity Tracking

No constitutional violations identified. This feature is inherently low-complexity as it's primarily prompt engineering documentation integrated into an existing module.

---

## Phase 0: Research

### Research Tasks

1. **Gemini system prompt best practices**: How to structure instructions for function calling models
2. **Intent recognition patterns**: Common NLU phrasings for task management (add, list, complete, delete, update)
3. **Urdu/English code-switching examples**: Authentic bilingual phrasings for confirmations and errors
4. **Multi-step reasoning in prompts**: How to instruct the model to chain tool calls for ambiguous references

### Research Findings

*(Detailed in `research.md`)*

**Decision 1**: Use structured sections in system prompt (Personality, Capabilities, Conversation Rules, Error Handling)
**Rationale**: Structured prompts improve model adherence to instructions
**Alternatives**: Free-form prompt text (rejected: harder to maintain, less predictable behavior)

**Decision 2**: Include intent mapping table as bullet points in prompt, not as structured data
**Rationale**: Gemini function calling models respond better to natural language examples than tables
**Alternatives**: Separate intent classifier (rejected: adds complexity, not needed for free tier)

**Decision 3**: Define error messages in prompt text with exact Urdu/English phrasings
**Rationale**: Ensures consistent, friendly error handling across all tool failures
**Alternatives**: Programmatic error message generation (rejected: prompt-level consistency preferred)

**Decision 4**: Use conversation history for pronoun resolution by instructing model to check context
**Rationale**: Leverages Gemini's context window instead of implementing custom anaphora resolution
**Alternatives**: Rule-based pronoun resolution (rejected: Gemini handles this natively)

---

## Phase 1: Design & Contracts

### Key Entities (Prompt Layer)

| Entity | Purpose | Location |
|--------|---------|----------|
| SYSTEM_PROMPT | Complete agent behavior instructions | `backend/src/services/agent.py` or `prompts.py` |
| INTENT_EXAMPLES | Intent-to-tool mapping examples (in prompt) | Embedded in SYSTEM_PROMPT |
| CONFIRMATION_TEMPLATES | Success message templates | Embedded in SYSTEM_PROMPT |
| ERROR_TEMPLATES | Friendly error message templates | Embedded in SYSTEM_PROMPT |

### System Prompt Structure

The system prompt follows this structure:

```
1. Persona Introduction (TaskBot identity)
2. Capabilities (5 task operations)
3. Conversation Rules
   3.1 Always Confirm Actions
   3.2 Handle Ambiguity (multi-step reasoning)
   3.3 Language Adaptation (English/Urdu)
   3.4 Error Messages (friendly, no tech jargon)
   3.5 Conversational Responses (greetings, help)
   3.6 Context Awareness (pronoun resolution)
4. What NOT to Do (constraints)
5. User ID Injection Note
```

### Intent Mapping (Embedded in Prompt)

| User Says Pattern | Intent | Tool Call | Notes |
|-------------------|--------|-----------|-------|
| "add task X" / "I need to remember X" / "remind me to X" | ADD | add_task(title=X) | Direct extraction |
| "show my tasks" / "what's on my list?" | LIST | list_tasks() | No filter |
| "show pending/completed" / "what's left?" | LIST | list_tasks(status=X) | Status filter |
| "mark task N done" / "I finished X" | COMPLETE | complete_task(task_id=N) | Direct or multi-step |
| "delete task N" / "remove X" | DELETE | delete_task(task_id=N) | Direct or multi-step |
| "rename task N to X" / "change X to Y" | UPDATE | update_task(task_id=N, title=X) | Direct or multi-step |
| "hello" / "hi" / "what can you do?" | GREETING/HELP | None | Conversational response |

### Confirmation Templates (Embedded in Prompt)

| Action | Template |
|--------|----------|
| ADD | "Done! Task added: '[title]'" |
| LIST | "You have N tasks:" or "Abhi tou koi task nahi hai" |
| COMPLETE | "Nice! Marked '[title]' as complete" |
| DELETE | "Got it! Deleted '[title]' from your list" |
| UPDATE | "Updated! '[old]' is now '[new]'" |

### Error Templates (Embedded in Prompt)

| Error | Message |
|-------|---------|
| Task not found | "Task nahi mila bhai. Check your task list?" |
| Empty title | "Task ka naam tou batao! Kya add karna hai?" |
| Permission denied | "Ye task aap ka nahi hai" |
| Database error | "Kuch gadbad ho gaya - try again please!" |
| Rate limit | "Thoda busy hoon - ek second mein try karo" |

### Multi-Step Reasoning Rules (Embedded in Prompt)

1. **Name-based resolution**: When user refers to task by name, call list_tasks first, find matching task, then proceed
2. **Pronoun resolution**: Check conversation history for recent task mentions
3. **Disambiguation**: If multiple tasks match, ask "Multiple tasks match '[keyword]'. Which one?"

---

## Implementation Tasks Overview

*(Detailed tasks will be generated by `/sp.tasks` command)*

### Task Groups

1. **System Prompt Authoring**
   - Write complete SYSTEM_PROMPT constant following spec structure
   - Include TaskBot persona, capabilities, conversation rules
   - Embed intent mapping examples as natural language bullets
   - Embed confirmation and error templates
   - Add multi-step reasoning instructions

2. **Prompt Integration**
   - Update `backend/src/services/agent.py` SYSTEM_PROMPT constant
   - Optionally extract to `prompts.py` module for maintainability
   - Ensure prompt passes to Gemini model initialization

3. **Error Message Integration**
   - Update tool handlers to return error messages matching prompt templates
   - Ensure consistency between prompt-defined messages and handler outputs

4. **Testing**
   - Manual test: Send sample messages, verify intent recognition
   - Manual test: Verify confirmation and error message formats
   - Regression tests: Add pytest tests for expected agent responses
   - Test Urdu/English code-switching

---

## Dependencies on Other Chunks

| Chunk | What This Chunk Needs | Status |
|-------|----------------------|--------|
| Chunk 4 (Function Tools) | Tool declarations and handlers | ✅ Spec exists, implementation parallel |
| Chunk 5 (Agent Runner) | SYSTEM_PROMPT constant location | ✅ Spec exists, defines agent.py |
| Chunk 8 (Conversation Persistence) | History for pronoun resolution | ✅ Spec exists, provides history context |

---

## Risks and Mitigations

1. **Risk**: Gemini model may not follow all prompt instructions consistently
   **Mitigation**: Use structured sections, provide concrete examples, test iteratively

2. **Risk**: Intent mapping may miss edge cases
   **Mitigation**: Comprehensive testing with varied phrasings; can update prompt post-deployment

3. **Risk**: Urdu phrases may not render correctly in some environments
   **Mitigation**: Use romanized Urdu (as specified), test in actual chat UI

4. **Risk**: System prompt becomes too long and reduces response quality
   **Mitigation**: Keep prompt concise (~1500 tokens max), prioritize essential rules

---

## Follow-up Actions

1. Run `/sp.tasks` to generate detailed implementation tasks
2. Create `contracts/system-prompt.md` with the complete prompt text
3. Integrate prompt into Chunk 5 agent module
4. Coordinate with frontend team on Urdu text display

---

## Token Budget Estimate

| Component | Estimated Tokens |
|-----------|------------------|
| Persona & Capabilities | ~200 |
| Conversation Rules (6 sections) | ~800 |
| Intent Examples (20+ phrasings) | ~300 |
| Confirmation/Error Templates | ~200 |
| **Total System Prompt** | **~1500 tokens** |

This leaves ample room for conversation history (20 messages × ~50 tokens = 1000) and tool responses within Gemini's context window.
