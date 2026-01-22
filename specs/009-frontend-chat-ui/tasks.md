# Tasks: Frontend Chat UI (Chunk-8)

**Input**: Design documents from `/specs/009-frontend-chat-ui/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/chat-api.ts, quickstart.md
**Constitution**: Phase III (`specs/phase3/constitution.md`)

**Tests**: Optional - not explicitly requested in specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for source code

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and TypeScript types foundation

- [X] T001 Create TypeScript types file with Message, MessageRole, ToolCall, ChatRequest, ChatResponse, ChatError, and all component props interfaces in `frontend/src/types/chat.ts`
- [X] T002 [P] Create conversation storage utility with getConversationId, setConversationId, clearConversationId functions in `frontend/src/lib/chat-storage.ts`
- [X] T003 [P] Create chat components directory structure at `frontend/src/components/chat/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add sendChatMessage function to `frontend/src/lib/api.ts` using existing authenticatedFetch pattern
- [X] T005 Create API proxy route handler in `frontend/src/app/api/chat/route.ts` that extracts auth-token from cookies and forwards to backend `/api/{user_id}/chat`
- [X] T006 Add `/chat` to protected routes array in `frontend/src/middleware.ts`
- [X] T007 [P] Create ChatLoading component with animated loading indicator in `frontend/src/components/chat/ChatLoading.tsx`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Send Chat Message (Priority: P1) MVP

**Goal**: Enable authenticated users to type a message and send it to the AI assistant

**Independent Test**: Type a message, click send or press Enter, verify message appears in chat and loading indicator shows

### Implementation for User Story 1

- [X] T008 [US1] Create ChatInput component with text input, send button, Enter key handling, and empty message prevention in `frontend/src/components/chat/ChatInput.tsx`
- [X] T009 [US1] Create ChatMessage component with role-based styling (user right-aligned, assistant left-aligned) and pending/error states in `frontend/src/components/chat/ChatMessage.tsx`
- [X] T010 [US1] Create ChatWindow container component with message state management, API call handling, and send message logic in `frontend/src/components/chat/ChatWindow.tsx`
- [X] T011 [US1] Create chat page at `frontend/src/app/chat/page.tsx` that renders ChatWindow component
- [X] T012 [US1] Wire ChatInput onSend to ChatWindow sendMessage handler with optimistic message display
- [X] T013 [US1] Add user message rendering with distinct right-aligned bubble styling using Tailwind CSS in ChatMessage
- [X] T014 [US1] Add assistant message rendering with distinct left-aligned bubble styling using Tailwind CSS in ChatMessage

**Checkpoint**: User Story 1 complete - users can send messages and receive AI responses

---

## Phase 4: User Story 2 - View Conversation History (Priority: P2)

**Goal**: Display previous messages in a scrollable view with session continuity

**Independent Test**: Load chat page, verify previous messages display in chronological order, scroll works, visual distinction between user/assistant

### Implementation for User Story 2

- [X] T015 [US2] Integrate localStorage conversation_id retrieval on ChatWindow mount using chat-storage utility
- [X] T016 [US2] Persist conversation_id from ChatResponse to localStorage after each successful response
- [X] T017 [US2] Implement scrollable message container with CSS overflow-y: auto in ChatWindow
- [X] T018 [US2] Add auto-scroll to latest message using useRef and scrollIntoView on new message arrival in ChatWindow
- [X] T019 [US2] Add timestamp display formatting (optional) to ChatMessage component

**Checkpoint**: User Story 2 complete - conversation persists across page loads and scrolling works

---

## Phase 5: User Story 3 - Loading State Feedback (Priority: P3)

**Goal**: Show loading indicator while waiting for AI response and disable input during processing

**Independent Test**: Send message, verify loading indicator appears immediately, disappears when response arrives, send button disabled during loading

### Implementation for User Story 3

- [X] T020 [US3] Integrate ChatLoading component display when isLoading state is true in ChatWindow
- [X] T021 [US3] Disable ChatInput send button and input field when loading prop is true
- [X] T022 [US3] Show loading indicator at end of message list (assistant typing position) in ChatWindow
- [X] T023 [US3] Ensure loading indicator disappears and is replaced by assistant response on arrival

**Checkpoint**: User Story 3 complete - loading feedback prevents user confusion and duplicate sends

---

## Phase 6: User Story 4 - Error Handling (Priority: P4)

**Goal**: Display friendly error messages for network failures, backend errors, and rate limits

**Independent Test**: Simulate network failure or backend error, verify friendly error message displays with retry option

### Implementation for User Story 4

- [X] T024 [US4] Handle 401 Unauthorized response in ChatWindow with redirect to `/signin` and toast notification
- [X] T025 [US4] Handle 429 Rate Limit response with inline rate limit message and retry guidance in ChatWindow
- [X] T026 [US4] Handle network errors (fetch failure) with toast notification and retry option in ChatWindow
- [X] T027 [US4] Handle generic backend errors (500) with user-friendly toast message in ChatWindow
- [X] T028 [US4] Add error state display in ChatMessage component for failed message sends
- [X] T029 [US4] Implement retry mechanism for failed messages with retry button display

**Checkpoint**: User Story 4 complete - users see friendly errors and can retry failed operations

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Navigation integration and final touches

- [X] T030 [P] Add Chat navigation link to Header component in `frontend/src/components/Header.tsx`
- [X] T031 [P] Add empty state / welcome message for new conversations (no messages) in ChatWindow
- [X] T032 TypeScript strict mode validation - run `npx tsc --noEmit` and fix any type errors
- [X] T033 Run `npm run build` to verify production build succeeds
- [ ] T034 Manual testing against quickstart.md acceptance checklist

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories should proceed sequentially in priority order (P1 -> P2 -> P3 -> P4)
  - Each story builds on components created in previous stories
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Core send/receive functionality
- **User Story 2 (P2)**: Depends on US1 components - Adds persistence and scrolling
- **User Story 3 (P3)**: Depends on US1 components - Adds loading states
- **User Story 4 (P4)**: Depends on US1 components - Adds error handling

### Within Each User Story

- Components before integration
- Core functionality before enhancements
- Story complete before moving to next priority

### Parallel Opportunities

- T002, T003 can run in parallel (Setup phase)
- T007 can run in parallel with T004, T005, T006 (Foundational phase)
- T030, T031 can run in parallel (Polish phase)

---

## Parallel Example: Phase 1 Setup

```bash
# Launch in parallel:
Task: "Create TypeScript types file in frontend/src/types/chat.ts" (T001)

# After T001 completes, launch in parallel:
Task: "Create conversation storage utility in frontend/src/lib/chat-storage.ts" (T002)
Task: "Create chat components directory at frontend/src/components/chat/" (T003)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (3 tasks)
2. Complete Phase 2: Foundational (4 tasks) - CRITICAL
3. Complete Phase 3: User Story 1 (7 tasks)
4. **STOP and VALIDATE**: Test sending/receiving messages independently
5. Deploy/demo if ready - core chat functionality works

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready
2. Add User Story 1 -> Test independently -> Deploy/Demo (MVP!)
3. Add User Story 2 -> Test session persistence -> Deploy/Demo
4. Add User Story 3 -> Test loading states -> Deploy/Demo
5. Add User Story 4 -> Test error handling -> Deploy/Demo
6. Complete Polish phase -> Final validation

### Suggested MVP Scope

**Minimum**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = 14 tasks
- Delivers: Working chat send/receive with message display
- Missing: Persistence, loading states, error handling

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Setup | 3 | Types, storage utility, directory structure |
| Foundational | 4 | API function, proxy route, middleware, loading component |
| User Story 1 (P1) | 7 | Send chat message - MVP core |
| User Story 2 (P2) | 5 | View conversation history |
| User Story 3 (P3) | 4 | Loading state feedback |
| User Story 4 (P4) | 6 | Error handling |
| Polish | 5 | Navigation, empty state, validation |

**Total Tasks**: 34

**Parallel Opportunities**:
- Phase 1: T002, T003 (after T001)
- Phase 2: T007 (with T004-T006)
- Phase 7: T030, T031

**Independent Test Criteria per Story**:
- US1: Send message, see it appear, receive response
- US2: Reload page, see previous messages, scroll works
- US3: Send message, see loading indicator, button disabled
- US4: Simulate error, see friendly message, retry option

---

*Tasks generated following Phase III constitution and spec-driven development workflow.*
