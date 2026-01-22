# Implementation Plan: Frontend Chat UI

**Branch**: `009-frontend-chat-ui` | **Date**: 2026-01-17 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/009-frontend-chat-ui/spec.md`

## Summary

Build a Next.js chat interface that enables authenticated users to interact with the TaskBot AI via natural language. The interface sends messages to the backend `/api/{user_id}/chat` endpoint, displays conversation history with distinct user/assistant styling, and handles loading states and errors gracefully. Uses existing Better Auth authentication infrastructure and follows Phase III stateless architecture principles.

## Technical Context

**Language/Version**: TypeScript 5 (strict mode), React 19.2.1, Next.js 16.0.10
**Primary Dependencies**: @better-auth/client ^0.0.2-alpha.3, react-hot-toast ^2.6.0, Tailwind CSS 4
**Storage**: localStorage for conversation_id; all messages persisted by backend
**Testing**: Jest ^29.7.0 with React Testing Library
**Target Platform**: Modern browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (Next.js App Router)
**Performance Goals**: Chat UI interactive within 3 seconds; loading indicator within 100ms; response display within 10 seconds
**Constraints**: Single conversation per user; plain text only (no markdown); Gemini free tier rate limits (5-15 RPM)
**Scale/Scope**: Single user per session; up to 50 messages in view without performance degradation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase III Constitution Compliance

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-Driven Development | ✅ PASS | Feature spec created before plan; following spec → plan → tasks workflow |
| II. Stateless Backend Architecture | ✅ PASS | Frontend stores only conversation_id; all state in database via backend |
| III. Gemini API Free Tier | ✅ PASS | Rate limit awareness in error handling; graceful degradation on 429 |
| IV. Friendly Conversational Interface | ✅ PASS | Clear message bubbles; user-friendly error messages |
| V. Security Through User Isolation | ✅ PASS | user_id from auth context; requests authenticated via existing middleware |
| VI. Type Safety and Validation | ✅ PASS | TypeScript strict mode; Pydantic validation on backend |
| VII. Persistent Storage | ✅ PASS | Backend persists all messages; frontend displays from backend state |

### Universal Principles Compliance

| Principle | Status | Evidence |
|-----------|--------|----------|
| Type Safety | ✅ PASS | TypeScript strict mode enforced in frontend |
| Clean Architecture | ✅ PASS | Separation: pages, components, lib/api, types |
| Quality Standards | ✅ PASS | Input validation; error handling; no hardcoded secrets |

**Constitution Check Result**: ✅ ALL GATES PASSED

## Project Structure

### Documentation (this feature)

```text
specs/009-frontend-chat-ui/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - tech decisions
├── data-model.md        # Phase 1 output - frontend types
├── quickstart.md        # Phase 1 output - development setup
├── contracts/           # Phase 1 output - API contracts
│   └── chat-api.ts      # TypeScript interface for chat endpoint
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── chat/
│   │   │       └── route.ts         # NEW: Proxy to backend /api/{user_id}/chat
│   │   ├── chat/
│   │   │   └── page.tsx             # NEW: Chat page
│   │   ├── signin/page.tsx          # Existing
│   │   ├── signup/page.tsx          # Existing
│   │   ├── tasks/page.tsx           # Existing (preserve for direct CRUD)
│   │   ├── layout.tsx               # Existing
│   │   └── page.tsx                 # Modify: Add chat navigation
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatWindow.tsx       # NEW: Main chat container
│   │   │   ├── ChatMessage.tsx      # NEW: Individual message bubble
│   │   │   ├── ChatInput.tsx        # NEW: Message input with send button
│   │   │   └── ChatLoading.tsx      # NEW: Loading indicator
│   │   ├── Header.tsx               # Modify: Add chat navigation link
│   │   └── [existing components]    # Preserve
│   ├── lib/
│   │   ├── api.ts                   # Modify: Add sendChatMessage function
│   │   └── chat-storage.ts          # NEW: localStorage for conversation_id
│   ├── types/
│   │   └── chat.ts                  # NEW: Chat-related TypeScript types
│   └── middleware.ts                # Modify: Protect /chat route
└── tests/
    └── components/
        └── chat/
            ├── ChatWindow.test.tsx  # NEW
            ├── ChatMessage.test.tsx # NEW
            └── ChatInput.test.tsx   # NEW
```

**Structure Decision**: Web application with frontend-only changes. Backend chat endpoint assumed functional from previous chunks. Following existing patterns from Phase II task management implementation.

## Complexity Tracking

> No constitutional violations requiring justification. Implementation uses existing patterns and minimal additions.

## Design Decisions

### DD-001: Chat Page Route
**Decision**: Create `/chat` as a new page rather than modal overlay
**Rationale**: Full page provides better mobile UX and clearer navigation; aligns with spec FR-001 requirements for dedicated chat interface
**Alternative Rejected**: Modal overlay - would complicate state management and reduce screen real estate for conversation

### DD-002: API Proxy Pattern
**Decision**: Create Next.js API route `/api/chat` that proxies to backend
**Rationale**: Consistent with existing task API pattern; handles auth token extraction from cookies; prevents CORS issues
**Alternative Rejected**: Direct browser-to-backend calls - would require cookie forwarding complexity

### DD-003: Conversation ID Storage
**Decision**: Use localStorage for conversation_id persistence
**Rationale**: Simple, reliable for single conversation per user; no need for session storage (survives tab close); aligns with FR-009
**Alternative Rejected**: sessionStorage - would lose conversation on tab close; IndexedDB - overkill for single ID

### DD-004: Message Display Approach
**Decision**: Virtualized list not required initially; simple scrollable div with auto-scroll
**Rationale**: SC-003 requires only 50 messages without degradation; simple implementation meets requirements
**Alternative Rejected**: react-window virtualization - premature optimization for MVP

### DD-005: Error Handling Strategy
**Decision**: Toast notifications for transient errors; inline error banner for persistent errors with retry
**Rationale**: Matches existing TaskList error handling patterns; provides clear user feedback per FR-010
**Alternative Rejected**: Modal errors - too disruptive to conversation flow

## Implementation Phases

### Phase 0: Research (Completed in this Plan)
- [x] Explore existing frontend patterns
- [x] Understand backend chat endpoint contract
- [x] Verify auth integration approach
- [x] Document technology decisions

### Phase 1: Design & Contracts
- [ ] Define TypeScript types for Message, ChatRequest, ChatResponse
- [ ] Create API contract documentation
- [ ] Generate data-model.md with component interfaces
- [ ] Create quickstart.md for development setup

### Phase 2: Tasks (Generated by /sp.tasks)
Will include:
1. Create chat API proxy route
2. Create chat types and storage utilities
3. Implement ChatMessage component
4. Implement ChatInput component
5. Implement ChatLoading component
6. Implement ChatWindow container
7. Create /chat page
8. Update navigation and middleware
9. Integration testing

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Backend chat endpoint not ready | Low | High | Spec assumes it's implemented; mock endpoint for testing |
| Rate limit errors from Gemini | Medium | Medium | Graceful error messages; retry guidance per edge case |
| Auth token expiration during chat | Low | Medium | Handle 401 response; redirect to login per edge case |

## Follow-ups

1. Consider adding typing indicators in future iteration (explicitly out of scope for MVP)
2. Consider markdown rendering for code snippets in future iteration (explicitly out of scope)
3. Consider multiple conversation threads in future iteration (explicitly out of scope)

---

*Plan generated by /sp.plan command following Phase III constitution and spec-driven development workflow.*
