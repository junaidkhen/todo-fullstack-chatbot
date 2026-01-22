'use client';

import { ChatLoadingProps } from '@/types/chat';

/**
 * ChatLoading Component
 *
 * Displays an animated loading indicator while waiting for AI response.
 * Shows as a typing indicator in the assistant's message position.
 */
export default function ChatLoading({ className = '' }: ChatLoadingProps) {
  return (
    <div className={`flex items-start ${className}`}>
      {/* Avatar placeholder for assistant */}
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

      {/* Loading bubble */}
      <div className="bg-gray-100 rounded-2xl rounded-tl-md px-4 py-3 max-w-xs">
        <div className="flex items-center space-x-1">
          {/* Animated dots */}
          <span
            className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
            style={{ animationDelay: '0ms' }}
          />
          <span
            className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
            style={{ animationDelay: '150ms' }}
          />
          <span
            className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
            style={{ animationDelay: '300ms' }}
          />
        </div>
      </div>
    </div>
  );
}
