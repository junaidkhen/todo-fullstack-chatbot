# Tasks: Agent Behavior & Natural Language Understanding Rules (Chunk 6)

**Input**: Design documents from `/specs/007-agent-behavior/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/system-prompt.md ✅

**Tests**: Not explicitly requested - manual verification via sample messages.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prompt module creation and project structure

- [X] T001 Create prompts module at `backend/src/services/prompts.py` with empty SYSTEM_PROMPT constant
- [X] T002 [P] Verify existing agent module at `backend/src/services/agent.py` can import from prompts module

**Checkpoint**: Prompts module ready for system prompt content ✅

---

## Phase 2: Foundational (System Prompt Authoring)

**Purpose**: Author the complete system prompt following the contract specification

**⚠️ CRITICAL**: This phase defines the core agent behavior - all user stories depend on prompt quality

- [X] T003 Write Persona Section in `backend/src/services/prompts.py` - TaskBot identity, personality traits, language preferences (~200 tokens)
- [X] T004 Write Capabilities Section in `backend/src/services/prompts.py` - list 5 task operations (add, list, complete, delete, update)
- [X] T005 Write Conversation Rule 1 in `backend/src/services/prompts.py` - "Always Confirm Actions" with confirmation templates
- [X] T006 Write Conversation Rule 2 in `backend/src/services/prompts.py` - "Handle Ambiguity" with multi-step reasoning flow
- [X] T007 Write Conversation Rule 3 in `backend/src/services/prompts.py` - "Language Adaptation" with Urdu/English phrases
- [X] T008 Write Conversation Rule 4 in `backend/src/services/prompts.py` - "Error Messages" with friendly templates
- [X] T009 Write Conversation Rule 5 in `backend/src/services/prompts.py` - "Conversational Responses" for greetings/help
- [X] T010 Write Conversation Rule 6 in `backend/src/services/prompts.py` - "Context Awareness" for pronoun resolution
- [X] T011 Write Intent Recognition Examples in `backend/src/services/prompts.py` - add, list, complete, delete, update phrasings
- [X] T012 Write Constraints Section in `backend/src/services/prompts.py` - "What NOT to Do" with 7 prohibition rules
- [X] T013 Write Notes Section in `backend/src/services/prompts.py` - user_id injection note
- [X] T014 Assemble complete SYSTEM_PROMPT constant in `backend/src/services/prompts.py` from all sections

**Checkpoint**: Complete system prompt authored and ready for integration ✅

---

## Phase 3: User Story 1 - Direct Task Creation (Priority: P1) 🎯 MVP

**Goal**: Agent recognizes "add task X" intent and confirms with friendly message

**Independent Test**: Send "add task buy milk" → verify add_task called with title="buy milk" and confirmation returned

### Implementation for User Story 1

- [X] T015 [US1] Add intent examples for ADD action in SYSTEM_PROMPT - "add task X", "I need to remember X", "remind me to X", "put X on my list"
- [X] T016 [US1] Add confirmation template for ADD action - "Done! Task added: '[title]'"
- [X] T017 [US1] Manual verification: Test "add task buy milk" returns expected confirmation

**Checkpoint**: User Story 1 independently functional ✅

---

## Phase 4: User Story 2 - Task Listing with Filters (Priority: P1)

**Goal**: Agent lists tasks with optional status filter and friendly empty-state messages

**Independent Test**: Send "show my pending tasks" → verify list_tasks called with status="pending"

### Implementation for User Story 2

- [X] T018 [US2] Add intent examples for LIST action - "show my tasks", "what's on my list?", "show pending", "what's left to do?", "show completed"
- [X] T019 [US2] Add confirmation templates for LIST action - count message, empty state messages (Urdu)
- [X] T020 [US2] Add empty state message "Abhi tou koi task nahi hai. Kuch add karna hai?" for zero tasks
- [X] T021 [US2] Add empty state message "Sab tasks complete ho gaye! Great job!" for all-done state
- [X] T022 [US2] Manual verification: Test "show my tasks" with empty list returns Urdu empty state

**Checkpoint**: User Story 2 independently functional ✅

---

## Phase 5: User Story 3 - Ambiguous Task Reference Resolution (Priority: P1)

**Goal**: Agent resolves task references by name via multi-step reasoning (list → identify → act)

**Independent Test**: Have task "Team meeting", send "delete the meeting task" → agent lists, identifies, deletes

### Implementation for User Story 3

- [X] T023 [US3] Add multi-step reasoning rule in SYSTEM_PROMPT - "When user refers to task by name, call list_tasks first"
- [X] T024 [US3] Add disambiguation rule - "If multiple matches: ask 'Multiple tasks match [keyword]. Which one?'"
- [X] T025 [US3] Add no-match message "Task nahi mila bhai. Show tasks likhein?" in SYSTEM_PROMPT
- [X] T026 [US3] Manual verification: Test "delete the meeting task" triggers list_tasks before delete_task

**Checkpoint**: User Story 3 independently functional ✅

---

## Phase 6: User Story 4 - Task Completion by Reference (Priority: P1)

**Goal**: Agent completes tasks using ID, name, or pronoun reference

**Independent Test**: Send "mark task 3 done" → verify complete_task called with task_id=3

### Implementation for User Story 4

- [X] T027 [US4] Add intent examples for COMPLETE action - "mark task N done", "complete the X task", "I finished X", "done with task N"
- [X] T028 [US4] Add confirmation template for COMPLETE action - "Nice! Marked '[title]' as complete"
- [X] T029 [US4] Add pronoun resolution rule - "Actually mark it done" refers to last mentioned task
- [X] T030 [US4] Manual verification: Test "mark task 3 done" returns correct confirmation

**Checkpoint**: User Story 4 independently functional ✅

---

## Phase 7: User Story 5 - Task Update with Partial Information (Priority: P2)

**Goal**: Agent updates task title or description via natural language

**Independent Test**: Send "rename task 2 to Weekly standup" → verify update_task called

### Implementation for User Story 5

- [X] T031 [US5] Add intent examples for UPDATE action - "rename task N to X", "change X to Y", "add description to task N"
- [X] T032 [US5] Add confirmation template for UPDATE action - "Updated! '[old]' is now '[new]'"
- [X] T033 [US5] Manual verification: Test "rename task 2 to Weekly standup" returns correct confirmation

**Checkpoint**: User Story 5 independently functional ✅

---

## Phase 8: User Story 6 - Friendly Error Handling (Priority: P2)

**Goal**: Agent responds with friendly, localized error messages without technical details

**Independent Test**: Attempt to complete non-existent task → verify friendly error message

### Implementation for User Story 6

- [X] T034 [US6] Add error template for task not found - "Task nahi mila bhai. Check your task list?"
- [X] T035 [US6] Add error template for empty title - "Task ka naam tou batao! Kya add karna hai?"
- [X] T036 [US6] Add error template for permission denied - "Ye task aap ka nahi hai"
- [X] T037 [US6] Add error template for database error - "Kuch gadbad ho gaya - try again please!"
- [X] T038 [US6] Add error template for rate limit - "Thoda busy hoon - ek second mein try karo"
- [X] T039 [US6] Add error template for invalid ID - "Task ID samajh nahi aaya - number use karo"
- [X] T040 [US6] Add error template for already completed - "Ye task tou pehle se complete hai!"
- [X] T041 [US6] Manual verification: Test completing non-existent task returns Urdu error

**Checkpoint**: User Story 6 independently functional ✅

---

## Phase 9: User Story 7 - Conversational Greetings and Help (Priority: P3)

**Goal**: Agent responds to greetings and help requests without invoking tools

**Independent Test**: Send "hello" → verify no tools called, friendly response returned

### Implementation for User Story 7

- [X] T042 [US7] Add conversational response for greetings - "Hey! Kya hal hai? Need help with tasks?"
- [X] T043 [US7] Add conversational response for help - "I can help you manage tasks - add, view, complete, delete, update. Try 'add task buy milk'!"
- [X] T044 [US7] Add conversational response for thanks - "Happy to help! Aur kuch?"
- [X] T045 [US7] Add rule: Do NOT invoke tools for greetings/help messages
- [X] T046 [US7] Manual verification: Test "hello" returns friendly greeting without tool calls

**Checkpoint**: User Story 7 independently functional ✅

---

## Phase 10: Integration (Prompt Integration)

**Purpose**: Integrate the system prompt with the agent module

- [X] T047 Import SYSTEM_PROMPT from prompts.py into `backend/src/services/agent.py`
- [X] T048 Pass SYSTEM_PROMPT to Gemini model initialization in agent.py
- [X] T049 Verify prompt is included in every Gemini API request
- [X] T050 Token budget verification: Confirm total prompt is under 1500 tokens (~1555 tokens verified)

**Checkpoint**: System prompt integrated with agent module ✅

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements and documentation

- [X] T051 [P] Review all error templates for consistent Urdu romanization
- [X] T052 [P] Verify no technical jargon in any user-facing message
- [X] T053 Run end-to-end test: Full conversation flow (add → list → complete → delete)
- [X] T054 Update `specs/007-agent-behavior/contracts/system-prompt.md` verification checklist
- [X] T055 Document any deviations from spec in research.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - User stories can proceed in priority order (P1 → P2 → P3)
  - P1 stories (US1-4) are core MVP
- **Integration (Phase 10)**: Depends on Foundational completion
- **Polish (Phase 11)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: ADD intent - independent
- **User Story 2 (P1)**: LIST intent - independent
- **User Story 3 (P1)**: Multi-step resolution - builds on LIST (T018-T022)
- **User Story 4 (P1)**: COMPLETE intent - uses multi-step resolution from US3
- **User Story 5 (P2)**: UPDATE intent - uses multi-step resolution from US3
- **User Story 6 (P2)**: Error handling - independent, parallel with any story
- **User Story 7 (P3)**: Conversational - independent, can run in parallel

### Within Each User Story

- Add intent examples to SYSTEM_PROMPT
- Add confirmation/error templates
- Manual verification test
- Mark story complete

### Parallel Opportunities

- Phase 2 tasks T003-T013 are sequential (building one prompt)
- Phase 3-9 intent examples can be added in any order (same file, but independent sections)
- Phase 11 polish tasks marked [P] can run in parallel

---

## Implementation Strategy

### MVP First (User Stories 1-4 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (author complete system prompt)
3. Complete Phase 3-6: User Stories 1-4 (P1 priorities)
4. Complete Phase 10: Integration
5. **STOP and VALIDATE**: Test core flows (add, list, complete, delete)
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Prompt authored
2. Add User Stories 1-4 → Test P1 flows → **MVP Ready**
3. Add User Story 5 → Update capability
4. Add User Story 6 → Error handling
5. Add User Story 7 → Conversational polish

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 55 |
| Setup Tasks | 2 |
| Foundational Tasks | 12 |
| User Story Tasks | 32 |
| Integration Tasks | 4 |
| Polish Tasks | 5 |
| MVP Tasks (P1) | 14 (T015-T030) |

### Tasks per User Story

| Story | Priority | Tasks | IDs |
|-------|----------|-------|-----|
| US1 - Direct Task Creation | P1 | 3 | T015-T017 |
| US2 - Task Listing | P1 | 5 | T018-T022 |
| US3 - Ambiguous Reference | P1 | 4 | T023-T026 |
| US4 - Task Completion | P1 | 4 | T027-T030 |
| US5 - Task Update | P2 | 3 | T031-T033 |
| US6 - Error Handling | P2 | 8 | T034-T041 |
| US7 - Conversational | P3 | 5 | T042-T046 |

---

## Notes

- This is primarily a **prompt engineering** task - most work is authoring text, not code
- All prompt content is defined in `contracts/system-prompt.md` - tasks reference this contract
- Manual verification via sample messages substitutes for automated tests
- Urdu phrases use romanized transliteration per Phase III constitution
- Token budget: ~1500 tokens for system prompt, leaving room for conversation history
