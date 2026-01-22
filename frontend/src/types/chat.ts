/**
 * Chat API Types
 *
 * TypeScript interfaces for the chat feature, aligned with backend Pydantic schemas.
 * Feature: 009-frontend-chat-ui
 */

// ============================================================================
// Core Types
// ============================================================================

/** Role of a message sender */
export type MessageRole = 'user' | 'assistant';

/** Details of a tool/function call made by the AI assistant */
export interface ToolCall {
  /** Tool name (e.g., 'add_task', 'list_tasks') */
  name: string;
  /** Arguments passed to the tool */
  arguments: Record<string, unknown>;
  /** Result returned from tool execution */
  result: Record<string, unknown>;
}

/** A single chat message displayed in the UI */
export interface Message {
  /** Unique identifier for frontend tracking */
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

// ============================================================================
// API Types
// ============================================================================

/** Request payload for sending a message to the backend */
export interface ChatRequest {
  /** User's message content */
  message: string;
  /** Existing conversation ID for continuity (null for new conversation) */
  conversation_id: number | null;
}

/** Response from the backend chat endpoint */
export interface ChatResponse {
  /** Conversation ID (use for subsequent requests) */
  conversation_id: number;
  /** AI assistant's response text */
  response: string;
  /** Tool calls executed during this interaction */
  tool_calls: ToolCall[] | null;
}

/** Error response from the backend */
export interface ChatError {
  /** Error type/code (e.g., 'RATE_LIMIT', 'VALIDATION_ERROR') */
  error: string;
  /** Human-readable error description */
  message: string;
  /** Additional context (optional) */
  details?: Record<string, unknown>;
}

/** Wrapper for API responses */
export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

// ============================================================================
// Component Props Interfaces
// ============================================================================

/** Props for ChatWindow container component */
export interface ChatWindowProps {
  /** Optional class name for styling */
  className?: string;
}

/** Props for individual message bubble component */
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
  /** Retry callback for failed messages */
  onRetry?: () => void;
}

/** Props for the message input component */
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

/** Props for loading indicator component */
export interface ChatLoadingProps {
  /** Optional class name for styling */
  className?: string;
}

// ============================================================================
// State Types
// ============================================================================

/** Internal state for ChatWindow component */
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

// ============================================================================
// Validation & Constants
// ============================================================================

/** Message validation rules */
export const MESSAGE_VALIDATION = {
  MIN_LENGTH: 1,
  MAX_LENGTH: 10000,
  TRIM_WHITESPACE: true,
} as const;

/** Chat constants */
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

/** Validate message content */
export const isValidMessage = (message: string): boolean => {
  const trimmed = message.trim();
  return (
    trimmed.length >= MESSAGE_VALIDATION.MIN_LENGTH &&
    trimmed.length <= MESSAGE_VALIDATION.MAX_LENGTH
  );
};

// ============================================================================
// Type Guards
// ============================================================================

/** Type guard for ToolCall */
export const isToolCall = (obj: unknown): obj is ToolCall => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'name' in obj &&
    'arguments' in obj &&
    'result' in obj
  );
};

/** Type guard for ChatResponse */
export const isChatResponse = (obj: unknown): obj is ChatResponse => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'conversation_id' in obj &&
    'response' in obj
  );
};

/** Type guard for ChatError */
export const isChatError = (obj: unknown): obj is ChatError => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'error' in obj &&
    'message' in obj
  );
};
