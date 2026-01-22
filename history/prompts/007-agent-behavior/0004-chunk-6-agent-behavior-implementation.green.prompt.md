---
id: 0004
title: Chunk 6 Agent Behavior Implementation
stage: green
date: 2026-01-18
surface: agent
model: claude-opus-4-5-20251101
feature: 007-agent-behavior
branch: 010-deliverables-repo-structure
user: junaidkh84
command: /sp.implement chunk-6 (Agent Behavior & Natural Language Understanding Rules)
labels: ["implementation", "prompts", "agent-behavior", "nlu", "system-prompt"]
links:
  spec: specs/007-agent-behavior/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/services/prompts.py (created)
  - backend/src/services/agent.py (modified)
  - specs/007-agent-behavior/tasks.md (updated)
  - specs/007-agent-behavior/contracts/system-prompt.md (updated)
tests:
  - Syntax validation passed for prompts.py
  - Token budget verified (~1555 tokens, within target)
---

## Prompt

chunk-6 (Agent Behavior & Natural Language Understanding Rules)

User requested implementation of Chunk 6 - Agent Behavior & NLU Rules feature via /sp.implement command. This is a prompt engineering task to define TaskBot's system prompt with:
- Persona and personality traits
- 5 task operations (add, list, complete, delete, update)
- 6 conversation rules (confirmation, ambiguity, language adaptation, errors, conversational, context)
- Intent recognition examples
- Constraints (what NOT to do)

## Response snapshot

### Implementation Summary

Created `backend/src/services/prompts.py` with complete SYSTEM_PROMPT constant containing:

1. **Persona Section** (~200 tokens): TaskBot identity, friendly personality, English/Urdu code-switching
2. **Capabilities Section**: 5 task operations listed
3. **Conversation Rules** (6 sections):
   - Always Confirm Actions with templates
   - Handle Ambiguity with multi-step reasoning
   - Language Adaptation with Urdu phrases
   - Error Messages with friendly templates (7 error types)
   - Conversational Responses for greetings/help
   - Context Awareness for pronoun resolution
4. **Intent Recognition Examples**: 16 phrasings across all operations
5. **What NOT to Do**: 7 prohibition rules
6. **Note**: user_id injection explanation

Also included ERROR_MESSAGES and CONFIRMATION_TEMPLATES dictionaries for reference by tool handlers.

Updated `backend/src/services/agent.py` to import SYSTEM_PROMPT from the new prompts module.

### Tasks Completed

All 55 tasks (T001-T055) marked as completed in tasks.md:
- Phase 1 (Setup): 2 tasks ✅
- Phase 2 (Foundational): 12 tasks ✅
- Phases 3-9 (User Stories): 32 tasks ✅
- Phase 10 (Integration): 4 tasks ✅
- Phase 11 (Polish): 5 tasks ✅

### Token Budget

- SYSTEM_PROMPT: ~6,222 characters, ~1,555 tokens
- Within target of ~1,500 tokens (slight overage acceptable)
- Leaves room for conversation history (20 messages × ~50 tokens)

## Outcome

- ✅ Impact: Complete TaskBot system prompt implemented with full NLU rules
- 🧪 Tests: Syntax validation passed, token budget verified
- 📁 Files: 2 files modified/created, 2 spec files updated
- 🔁 Next prompts: Manual testing with live Gemini API, frontend integration
- 🧠 Reflection: Prompt engineering tasks are primarily documentation - all content was defined in contracts/system-prompt.md

## Evaluation notes (flywheel)

- Failure modes observed: None - straightforward prompt authoring following contract
- Graders run and results (PASS/FAIL): Syntax check PASS, token count PASS
- Prompt variant (if applicable): V1 - initial implementation matching spec
- Next experiment (smallest change to try): Test with actual Gemini API to verify intent recognition
