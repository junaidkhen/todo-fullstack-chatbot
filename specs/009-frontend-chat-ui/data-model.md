# Data Model: Frontend Chat UI

**Feature**: 009-frontend-chat-ui
**Date**: 2026-01-17
**Status**: Complete

## Overview

This document defines the TypeScript types and interfaces for the Frontend Chat UI feature. These types align with the backend Pydantic schemas and provide type safety for all chat-related operations.

---

## Core Entities

### MessageRole

Enum representing the sender of a message.

```typescript
// frontend/src/types/chat.ts

export type MessageRole = 'user' | 'assistant';
```

### Message

Represents a single chat message displayed in the UI.

```typescript
export interface Message {
  /** Unique identifier (optional, for frontend tracking) */
  id?: string;

  /** Who sent the message */
  role: MessageRole;

  /** Text content of the message */
  content: string;

  /** When the message was created */
  timestamp: Date;

  /** Optional tool calls executed for this message (assistant only) */
  toolCalls?: ToolCall[];

  /** Loading state for optimistic updates */
  pending?: boolean;

  /** Error state if message failed to send */
  error?: string;
}
```

### ToolCall

Represents a tool/function call made by the AI assistant.

```typescript
export interface ToolCall {
  /** Tool name (e.g., 'add_task', 'list_tasks') */
  name: string;

  /** Arguments passed to the tool */
  arguments: Record<string, unknown>;

  /** Result returned from tool execution */
  result: Record<string, unknown>;
}
```

---

## API Types

### ChatRequest

Request payload for sending a message to the backend.

```typescript
export interface ChatRequest {
  /** User's message content */
  message: string;

  /** Existing conversation ID for continuity (null for new conversation) */
  conversation_id: number | null;
}
```

**Validation Rules**:
- `message`: Required, 1-10,000 characters, cannot be whitespace-only
- `conversation_id`: Optional integer, must be valid if provided

### ChatResponse

Response from the backend chat endpoint.

```typescript
export interface ChatResponse {
  /** Conversation ID (use for subsequent requests) */
  conversation_id: number;

  /** AI assistant's response text */
  response: string;

  /** Tool calls executed during this interaction */
  tool_calls: ToolCall[] | null;
}
```

### ChatError

Error response from the backend.

```typescript
export interface ChatError {
  /** Error type/code (e.g., 'RATE_LIMIT', 'VALIDATION_ERROR') */
  error: string;

  /** Human-readable error description */
  message: string;

  /** Additional context (optional) */
  details?: Record<string, unknown>;
}
```

### API Response Type

Wrapper for API responses (consistent with existing pattern).

```typescript
export interface ApiResponse<T> {
  data?: T;
  error?: string;
}
```

---

## Component Props Interfaces

### ChatWindowProps

Props for the main chat container component.

```typescript
export interface ChatWindowProps {
  /** Optional class name for styling */
  className?: string;
}
```

**Note**: ChatWindow manages its own state internally. No external props required for basic operation.

### ChatMessageProps

Props for individual message bubble component.

```typescript
export interface ChatMessageProps {
  /** Who sent the message */
  role: MessageRole;

  /** Message text content */
  content: string;

  /** When the message was sent (optional, for display) */
  timestamp?: Date;

  /** Whether message is still being sent */
  pending?: boolean;

  /** Error message if send failed */
  error?: string;
}
```

### ChatInputProps

Props for the message input component.

```typescript
export interface ChatInputProps {
  /** Callback when user sends a message */
  onSend: (message: string) => void;

  /** Whether input is disabled (during loading) */
  disabled: boolean;

  /** Whether a message is currently being processed */
  loading: boolean;

  /** Placeholder text (optional) */
  placeholder?: string;

  /** Maximum character limit (optional, default 10000) */
  maxLength?: number;
}
```

### ChatLoadingProps

Props for the loading indicator component.

```typescript
export interface ChatLoadingProps {
  /** Optional class name for styling */
  className?: string;
}
```

---

## State Types

### ChatState

Internal state for ChatWindow component.

```typescript
export interface ChatState {
  /** All messages in the conversation */
  messages: Message[];

  /** Current conversation ID */
  conversationId: number | null;

  /** Whether a message is being processed */
  isLoading: boolean;

  /** Global error message (e.g., rate limit) */
  error: string | null;

  /** Whether rate limited */
  isRateLimited: boolean;
}
```

### ChatAction

Actions for state management (if using useReducer).

```typescript
export type ChatAction =
  | { type: 'ADD_USER_MESSAGE'; message: Message }
  | { type: 'ADD_ASSISTANT_MESSAGE'; message: Message }
  | { type: 'SET_LOADING'; isLoading: boolean }
  | { type: 'SET_ERROR'; error: string | null }
  | { type: 'SET_CONVERSATION_ID'; conversationId: number }
  | { type: 'SET_RATE_LIMITED'; isRateLimited: boolean }
  | { type: 'UPDATE_MESSAGE_STATUS'; id: string; pending: boolean; error?: string };
```

---

## Storage Types

### ConversationStorage

Types for localStorage conversation management.

```typescript
// frontend/src/lib/chat-storage.ts

export interface ConversationStorageAPI {
  /** Get stored conversation ID */
  getConversationId: () => number | null;

  /** Store conversation ID */
  setConversationId: (id: number) => void;

  /** Clear stored conversation ID */
  clearConversationId: () => void;
}
```

---

## Validation Rules

### Message Content Validation

```typescript
export const MESSAGE_VALIDATION = {
  MIN_LENGTH: 1,
  MAX_LENGTH: 10000,
  TRIM_WHITESPACE: true,
} as const;

export const isValidMessage = (message: string): boolean => {
  const trimmed = message.trim();
  return (
    trimmed.length >= MESSAGE_VALIDATION.MIN_LENGTH &&
    trimmed.length <= MESSAGE_VALIDATION.MAX_LENGTH
  );
};
```

---

## Type Guards

Helper functions for runtime type checking.

```typescript
export const isToolCall = (obj: unknown): obj is ToolCall => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'name' in obj &&
    'arguments' in obj &&
    'result' in obj
  );
};

export const isChatResponse = (obj: unknown): obj is ChatResponse => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'conversation_id' in obj &&
    'response' in obj
  );
};

export const isChatError = (obj: unknown): obj is ChatError => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'error' in obj &&
    'message' in obj
  );
};
```

---

## Constants

```typescript
export const CHAT_CONSTANTS = {
  /** localStorage key for conversation ID */
  STORAGE_KEY: 'chat_conversation_id',

  /** API endpoint path */
  API_ENDPOINT: '/api/chat',

  /** Default placeholder text */
  INPUT_PLACEHOLDER: 'Type a message...',

  /** Maximum message length */
  MAX_MESSAGE_LENGTH: 10000,

  /** Character count warning threshold */
  CHAR_WARNING_THRESHOLD: 9000,
} as const;
```

---

## File Mapping

| Type/Interface | File Location |
|----------------|---------------|
| Message, MessageRole, ToolCall | `frontend/src/types/chat.ts` |
| ChatRequest, ChatResponse, ChatError | `frontend/src/types/chat.ts` |
| Component Props (ChatWindowProps, etc.) | `frontend/src/types/chat.ts` |
| ChatState, ChatAction | `frontend/src/types/chat.ts` |
| ConversationStorageAPI | `frontend/src/lib/chat-storage.ts` |
| Validation, Type Guards, Constants | `frontend/src/types/chat.ts` |

---

*Data model generated for Phase 1 of /sp.plan workflow.*
