/**
 * Chat API Contract
 *
 * Feature: 009-frontend-chat-ui
 * Date: 2026-01-17
 *
 * This contract defines the TypeScript interfaces for the chat API
 * between the Next.js frontend and FastAPI backend.
 *
 * Backend Endpoint: POST /api/{user_id}/chat
 * Frontend Proxy: POST /api/chat
 */

// ============================================================================
// Request/Response Types
// ============================================================================

/**
 * Request payload for sending a chat message.
 *
 * Frontend sends to: POST /api/chat
 * Proxy forwards to: POST /api/{user_id}/chat (user_id from JWT)
 */
export interface ChatRequest {
  /**
   * User's message content.
   *
   * @minLength 1
   * @maxLength 10000
   * @description Cannot be empty or whitespace-only
   */
  message: string;

  /**
   * Existing conversation ID for continuity.
   *
   * @description Pass null for new conversation. Backend will create one
   *              and return the ID in the response.
   */
  conversation_id: number | null;
}

/**
 * Successful response from the chat endpoint.
 */
export interface ChatResponse {
  /**
   * Conversation ID for this chat session.
   *
   * @description Store this and include in subsequent requests for
   *              conversation continuity.
   */
  conversation_id: number;

  /**
   * AI assistant's natural language response.
   *
   * @description Plain text response from the TaskBot. May contain
   *              mixed English/Urdu as per Phase III constitution.
   */
  response: string;

  /**
   * Tool calls executed during this interaction.
   *
   * @description null if no tools were invoked. Contains details of
   *              any task operations performed (add, list, complete, etc.)
   */
  tool_calls: ToolCall[] | null;
}

/**
 * Details of a tool/function call made by the AI.
 */
export interface ToolCall {
  /**
   * Tool name that was invoked.
   *
   * @example 'add_task', 'list_tasks', 'complete_task', 'delete_task', 'update_task'
   */
  name: string;

  /**
   * Arguments passed to the tool.
   *
   * @example { "title": "Buy groceries", "description": "Milk, eggs, bread" }
   */
  arguments: Record<string, unknown>;

  /**
   * Result returned from tool execution.
   *
   * @example { "task_id": 42, "status": "created" }
   */
  result: Record<string, unknown>;
}

// ============================================================================
// Error Types
// ============================================================================

/**
 * Error response from the chat endpoint.
 */
export interface ChatError {
  /**
   * Error type/code for programmatic handling.
   *
   * @example 'VALIDATION_ERROR', 'RATE_LIMIT', 'UNAUTHORIZED', 'INTERNAL_ERROR'
   */
  error: string;

  /**
   * Human-readable error message.
   *
   * @description Display this to the user. May be in English or mixed English/Urdu.
   */
  message: string;

  /**
   * Additional error context.
   *
   * @description Optional. May contain field-specific validation errors or
   *              rate limit retry-after information.
   */
  details?: Record<string, unknown>;
}

// ============================================================================
// HTTP Status Code Reference
// ============================================================================

/**
 * HTTP status codes returned by the chat endpoint.
 */
export const ChatHttpStatus = {
  /** Successful response */
  OK: 200,

  /** Invalid request (empty message, invalid conversation_id format) */
  BAD_REQUEST: 400,

  /** Invalid or missing JWT token */
  UNAUTHORIZED: 401,

  /** Attempting to access another user's conversation */
  FORBIDDEN: 403,

  /** Pydantic validation errors */
  UNPROCESSABLE_ENTITY: 422,

  /** Gemini API rate limit exceeded */
  TOO_MANY_REQUESTS: 429,

  /** Internal server error */
  INTERNAL_SERVER_ERROR: 500,
} as const;

// ============================================================================
// API Function Signatures
// ============================================================================

/**
 * Send a chat message and receive AI response.
 *
 * @param request - The chat request payload
 * @returns Promise resolving to ChatResponse or ChatError
 *
 * @example
 * const result = await sendChatMessage({
 *   message: "Add a task to buy groceries",
 *   conversation_id: 42, // or null for new conversation
 * });
 *
 * if ('error' in result) {
 *   // Handle error
 *   console.error(result.message);
 * } else {
 *   // Handle success
 *   console.log(result.response);
 *   // Store conversation_id for next request
 *   setConversationId(result.conversation_id);
 * }
 */
export type SendChatMessage = (
  request: ChatRequest
) => Promise<ChatResponse | ChatError>;

// ============================================================================
// API Implementation Contract
// ============================================================================

/**
 * Chat API client interface.
 *
 * Implementation should be in: frontend/src/lib/api.ts
 */
export interface ChatApiClient {
  /**
   * Send a message to the chat endpoint.
   */
  sendMessage: SendChatMessage;
}

// ============================================================================
// Frontend Route Contract
// ============================================================================

/**
 * Next.js API route handler contract.
 *
 * Route: POST /api/chat
 * File: frontend/src/app/api/chat/route.ts
 *
 * Responsibilities:
 * 1. Extract auth-token from request cookies
 * 2. Decode JWT to get user_id
 * 3. Forward request to backend: POST /api/{user_id}/chat
 * 4. Return backend response to client
 */
export interface ChatRouteHandler {
  /**
   * Handle POST request to /api/chat
   *
   * @param request - Next.js Request object with JSON body
   * @returns Response with ChatResponse or ChatError
   */
  POST: (request: Request) => Promise<Response>;
}

// ============================================================================
// Request/Response Examples
// ============================================================================

/**
 * Example: Send new message (new conversation)
 *
 * Request:
 * POST /api/chat
 * Content-Type: application/json
 * Cookie: auth-token=<jwt>
 *
 * {
 *   "message": "Add a task to buy groceries",
 *   "conversation_id": null
 * }
 *
 * Response (200 OK):
 * {
 *   "conversation_id": 1,
 *   "response": "Task add ho gaya! 'Buy groceries' add kar diya.",
 *   "tool_calls": [
 *     {
 *       "name": "add_task",
 *       "arguments": { "title": "Buy groceries" },
 *       "result": { "task_id": 42, "status": "created" }
 *     }
 *   ]
 * }
 */
export const _exampleNewConversation = null;

/**
 * Example: Continue existing conversation
 *
 * Request:
 * POST /api/chat
 * Content-Type: application/json
 * Cookie: auth-token=<jwt>
 *
 * {
 *   "message": "Show me all my tasks",
 *   "conversation_id": 1
 * }
 *
 * Response (200 OK):
 * {
 *   "conversation_id": 1,
 *   "response": "Tumhare 3 tasks hain:\n1. Buy groceries (pending)\n2. Call mom (completed)\n3. Finish report (pending)",
 *   "tool_calls": [
 *     {
 *       "name": "list_tasks",
 *       "arguments": {},
 *       "result": { "tasks": [...], "count": 3 }
 *     }
 *   ]
 * }
 */
export const _exampleContinueConversation = null;

/**
 * Example: Rate limit error
 *
 * Response (429 Too Many Requests):
 * {
 *   "error": "RATE_LIMIT",
 *   "message": "Please wait a moment before sending another message.",
 *   "details": { "retry_after_seconds": 60 }
 * }
 */
export const _exampleRateLimitError = null;

/**
 * Example: Validation error
 *
 * Response (400 Bad Request):
 * {
 *   "error": "VALIDATION_ERROR",
 *   "message": "Message cannot be empty.",
 *   "details": { "field": "message" }
 * }
 */
export const _exampleValidationError = null;
