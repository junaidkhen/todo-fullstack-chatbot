# Research Document: Frontend Chat UI

**Feature**: 009-frontend-chat-ui
**Date**: 2026-01-17
**Status**: Complete

## Research Summary

This document resolves all technical unknowns identified during plan.md creation for the Frontend Chat UI feature. All NEEDS CLARIFICATION items have been investigated and decisions documented.

---

## Research Task 1: Existing Frontend Architecture Patterns

### Question
How does the existing Next.js frontend handle API calls, authentication, and component structure?

### Findings

**API Call Pattern** (from `frontend/src/lib/api.ts`):
- Uses `authenticatedFetch<T>(endpoint, options)` wrapper
- Automatically includes `credentials: 'include'` for cookies
- Sets `Content-Type: application/json`
- Handles 401 responses with redirect to `/signin`
- Returns `{ data?, error? }` structure

**Authentication Integration**:
- HTTP-only cookies (`auth-token`) for session management
- Middleware protects routes by checking cookie presence
- Auth routes proxy to backend at `http://localhost:8000`
- JWT token extracted from cookie and forwarded as Bearer token

**Component Structure**:
- Functional components with React hooks
- TypeScript with proper prop interfaces
- Tailwind CSS for styling
- Toast notifications via react-hot-toast
- No global state management (local component state)

### Decision
**Follow existing patterns**: Use `authenticatedFetch` for chat API calls, functional components with hooks, Tailwind CSS styling, and react-hot-toast for error notifications.

### Alternatives Considered
- Redux/Context for global chat state: Rejected - overkill for single conversation, existing pattern works
- SWR/React Query: Rejected - simple fetch pattern sufficient for MVP; no caching needed for chat

---

## Research Task 2: Backend Chat Endpoint Contract

### Question
What is the exact request/response contract for the backend `/api/{user_id}/chat` endpoint?

### Findings

**Endpoint**: `POST /api/{user_id}/chat`

**Request Schema (ChatRequest)**:
```typescript
interface ChatRequest {
  message: string;          // Required, 1-10,000 characters
  conversation_id?: number; // Optional, for continuing conversation
}
```

**Response Schema (ChatResponse)**:
```typescript
interface ToolCall {
  name: string;      // e.g., 'add_task', 'list_tasks'
  arguments: object; // Tool-specific arguments
  result: object;    // Tool execution result
}

interface ChatResponse {
  conversation_id: number;     // Always returned, use for subsequent requests
  response: string;            // AI's natural language response
  tool_calls: ToolCall[] | null; // Optional, if tools were invoked
}
```

**Error Response Schema**:
```typescript
interface ChatError {
  error: string;     // Error type/code
  message: string;   // Human-readable description
  details?: object;  // Optional additional context
}
```

**HTTP Status Codes**:
- 400: Invalid/missing user_id, empty message, invalid conversation_id
- 401: Unauthorized, invalid JWT
- 403: Accessing another user's conversation
- 422: Pydantic validation errors
- 429: Gemini rate limit exceeded
- 500: Internal server error

### Decision
**Create TypeScript types** matching backend schemas. Handle all error codes with user-friendly messages. Store conversation_id in localStorage for session continuity.

---

## Research Task 3: Conversation ID Persistence Strategy

### Question
How should conversation_id be persisted for session continuity (FR-009)?

### Findings

**Options Evaluated**:

1. **localStorage**
   - Pros: Simple API, persists across tab close, survives browser restart
   - Cons: Only accessible client-side, no SSR hydration
   - Fit: Good for single conversation per user requirement

2. **sessionStorage**
   - Pros: Simple API, isolated per tab
   - Cons: Lost on tab close, doesn't persist across sessions
   - Fit: Poor - users expect conversation to persist

3. **Cookie**
   - Pros: Server-accessible, automatic with requests
   - Cons: Complexity with Next.js API routes, size limits
   - Fit: Overkill for single ID; auth cookies already handled separately

4. **IndexedDB**
   - Pros: Large storage, async API
   - Cons: Complex API for simple use case
   - Fit: Overkill for storing single integer

### Decision
**Use localStorage** with key `chat_conversation_id`. Simple, reliable, meets requirements.

**Implementation**:
```typescript
// lib/chat-storage.ts
export const getConversationId = (): number | null => {
  if (typeof window === 'undefined') return null;
  const id = localStorage.getItem('chat_conversation_id');
  return id ? parseInt(id, 10) : null;
};

export const setConversationId = (id: number): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem('chat_conversation_id', id.toString());
};

export const clearConversationId = (): void => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('chat_conversation_id');
};
```

---

## Research Task 4: Message List Performance

### Question
How to handle message list rendering for 50+ messages (SC-003)?

### Findings

**Requirements Analysis**:
- SC-003: View 50 messages without performance degradation
- SC-008: Auto-scroll to latest message
- Edge case: Scrollable history for older messages

**Options Evaluated**:

1. **Simple Scrollable Div**
   - Pros: Minimal code, built-in browser scrolling
   - Cons: All messages in DOM
   - Fit: Sufficient for 50 messages

2. **Virtualized List (react-window)**
   - Pros: Only visible messages in DOM, handles thousands
   - Cons: Added dependency, complexity for variable height messages
   - Fit: Premature optimization for MVP

3. **Infinite Scroll with Pagination**
   - Pros: Load messages on demand
   - Cons: Complexity; backend doesn't return paginated history
   - Fit: Not needed for single session history

### Decision
**Simple scrollable div** with CSS `overflow-y: auto`. Use `useRef` + `scrollIntoView` for auto-scroll.

**Rationale**: 50 message DOM elements are trivial for modern browsers. React's reconciliation handles updates efficiently. Virtualization can be added later if needed.

---

## Research Task 5: Error Handling UX Patterns

### Question
How to display errors matching existing UI patterns and edge cases?

### Findings

**Existing Error Patterns** (from TaskList.tsx):
- Toast notifications for transient errors
- Component-level error state for persistent errors
- Error messages are user-friendly, not technical

**Edge Cases from Spec**:
- Network failure: "Connection lost. Please try again."
- Rate limit (429): "Please wait a moment before sending another message."
- Session expired (401): Redirect to login
- Backend error: Generic "Something went wrong. Please try again."

### Decision
**Layered error handling**:

1. **Transient errors** (network, 500): Toast notification with retry option
2. **Rate limit (429)**: Inline message in chat with countdown suggestion
3. **Auth errors (401)**: Redirect to `/signin` with session expired message
4. **Validation errors (400, 422)**: Inline error near input field

**Implementation**:
```typescript
const handleChatError = (status: number, message: string) => {
  if (status === 401) {
    toast.error('Session expired. Please sign in again.');
    router.push('/signin');
    return;
  }
  if (status === 429) {
    setRateLimitError(true);
    return;
  }
  toast.error(message || 'Something went wrong. Please try again.');
};
```

---

## Research Task 6: Chat UI Component Structure

### Question
What component hierarchy best supports the requirements?

### Findings

**Requirements Mapping**:
- FR-001: Chat interface with input and send button → ChatInput
- FR-004, FR-005: Message bubbles with distinct styling → ChatMessage
- FR-006: Loading indicator → ChatLoading
- FR-008: Auto-scroll → ChatWindow container

**Component Hierarchy**:
```
ChatWindow (container)
├── ChatMessages (message list area)
│   ├── ChatMessage (user bubble)
│   ├── ChatMessage (assistant bubble)
│   └── ChatLoading (when waiting)
└── ChatInput (input + send button)
```

### Decision
**Four components**:

1. **ChatWindow.tsx**: Container managing state, API calls, scrolling
2. **ChatMessage.tsx**: Individual message bubble (user or assistant)
3. **ChatInput.tsx**: Text input with send button, handles Enter key
4. **ChatLoading.tsx**: Animated loading indicator

**Props Interfaces**:
```typescript
interface ChatWindowProps {
  // Container manages all state internally
}

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: Date;
}

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
  loading: boolean;
}

interface ChatLoadingProps {
  // Simple presentational component
}
```

---

## Research Task 7: Authentication Integration

### Question
How to retrieve user_id and protect the /chat route?

### Findings

**Existing Auth Pattern**:
- Middleware checks for `auth-token` cookie
- Protected routes: `/tasks`, `/profile`
- Unauthenticated users redirected to `/signin`

**User ID Retrieval**:
- Backend extracts user_id from JWT token
- Frontend doesn't need user_id directly - backend handles it
- API proxy route extracts token from cookie and forwards to backend

### Decision
**Follow existing pattern**:

1. Add `/chat` to protected routes in `middleware.ts`
2. Create `/api/chat` route that:
   - Extracts `auth-token` from cookies
   - Forwards request to backend `/api/{user_id}/chat`
   - Note: user_id comes from JWT sub claim on backend

**Middleware Update**:
```typescript
// middleware.ts
const protectedRoutes = ['/tasks', '/profile', '/chat'];
```

---

## Technology Decisions Summary

| Decision Area | Choice | Rationale |
|---------------|--------|-----------|
| API Pattern | authenticatedFetch | Consistent with existing code |
| State Management | Local component state | Simple; no global state needed |
| Styling | Tailwind CSS | Existing stack |
| Notifications | react-hot-toast | Existing stack |
| Conversation Storage | localStorage | Simple; persists across sessions |
| Message List | Simple scrollable div | Sufficient for 50 messages |
| Error Display | Toast + inline | Matches existing patterns |
| Components | 4 components | Clean separation of concerns |

---

## Open Questions (None)

All technical unknowns have been resolved. Implementation can proceed to Phase 1.

---

*Research completed for Phase 0 of /sp.plan workflow.*
