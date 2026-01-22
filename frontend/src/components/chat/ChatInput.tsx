'use client';

import { useState, useCallback, KeyboardEvent } from 'react';
import { ChatInputProps, CHAT_CONSTANTS, isValidMessage } from '@/types/chat';

/**
 * ChatInput Component
 *
 * Text input with send button for composing chat messages.
 * Supports Enter key to send, and prevents empty message submission.
 */
export default function ChatInput({
  onSend,
  disabled,
  loading,
  placeholder = CHAT_CONSTANTS.INPUT_PLACEHOLDER,
  maxLength = CHAT_CONSTANTS.MAX_MESSAGE_LENGTH,
}: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSend = useCallback(() => {
    if (!isValidMessage(message) || disabled || loading) {
      return;
    }

    onSend(message.trim());
    setMessage('');
  }, [message, onSend, disabled, loading]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  const isButtonDisabled = disabled || loading || !isValidMessage(message);
  const showCharWarning =
    message.length > CHAT_CONSTANTS.CHAR_WARNING_THRESHOLD &&
    message.length <= maxLength;

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <div className="flex items-end space-x-3">
        {/* Text Input */}
        <div className="flex-1 relative">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled || loading}
            maxLength={maxLength}
            rows={1}
            className="w-full px-4 py-3 border border-gray-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
            style={{
              minHeight: '48px',
              maxHeight: '120px',
            }}
          />
          {/* Character count warning */}
          {showCharWarning && (
            <div className="absolute right-3 bottom-1 text-xs text-amber-600">
              {message.length}/{maxLength}
            </div>
          )}
        </div>

        {/* Send Button */}
        <button
          onClick={handleSend}
          disabled={isButtonDisabled}
          className="flex-shrink-0 w-12 h-12 bg-teal-500 text-white rounded-xl hover:bg-teal-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          aria-label="Send message"
        >
          {loading ? (
            <svg
              className="animate-spin h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          )}
        </button>
      </div>

      {/* Helper text */}
      <div className="mt-2 text-xs text-gray-500">
        Press Enter to send, Shift+Enter for new line
      </div>
    </div>
  );
}
