'use client';

import { ChatMessageProps } from '@/types/chat';

/**
 * ChatMessage Component
 *
 * Displays a single chat message with role-based styling.
 * User messages are right-aligned; assistant messages are left-aligned.
 */
export default function ChatMessage({
  role,
  content,
  timestamp,
  pending = false,
  error,
  onRetry,
}: ChatMessageProps) {
  const isUser = role === 'user';

  // Format timestamp for display
  const formatTime = (date?: Date) => {
    if (!date) return null;
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`flex items-start ${isUser ? 'justify-end' : 'justify-start'}`}>
      {/* Assistant avatar */}
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-teal-500 flex items-center justify-center mr-3">
          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
            />
          </svg>
        </div>
      )}

      {/* Message bubble */}
      <div
        className={`max-w-[70%] ${
          isUser
            ? 'bg-teal-500 text-white rounded-2xl rounded-tr-md'
            : 'bg-gray-100 text-gray-900 rounded-2xl rounded-tl-md'
        } px-4 py-3 ${pending ? 'opacity-60' : ''} ${error ? 'border-2 border-red-400' : ''}`}
      >
        {/* Message content */}
        <p className="whitespace-pre-wrap break-words">{content}</p>

        {/* Timestamp and status */}
        <div
          className={`mt-1 text-xs ${
            isUser ? 'text-teal-100' : 'text-gray-500'
          } flex items-center justify-end space-x-2`}
        >
          {timestamp && <span>{formatTime(timestamp)}</span>}
          {pending && <span>Sending...</span>}
        </div>

        {/* Error state */}
        {error && (
          <div className="mt-2 flex items-center text-red-600 text-sm">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>{error}</span>
            {onRetry && (
              <button
                onClick={onRetry}
                className="ml-2 underline hover:no-underline focus:outline-none"
              >
                Retry
              </button>
            )}
          </div>
        )}
      </div>

      {/* User avatar */}
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center ml-3">
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            />
          </svg>
        </div>
      )}
    </div>
  );
}
