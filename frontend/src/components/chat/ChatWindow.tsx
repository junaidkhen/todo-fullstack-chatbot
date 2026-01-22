'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { Message, ChatWindowProps } from '@/types/chat';
import { sendChatMessage } from '@/lib/api';
import { getConversationId, setConversationId } from '@/lib/chat-storage';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import ChatLoading from './ChatLoading';

/**
 * ChatWindow Component
 *
 * Main chat container that manages conversation state, API calls,
 * and renders the message list with input.
 */
export default function ChatWindow({ className = '' }: ChatWindowProps) {
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // State
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationIdState] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pendingMessageId, setPendingMessageId] = useState<string | null>(null);

  // Load conversation ID from localStorage on mount
  useEffect(() => {
    const storedId = getConversationId();
    if (storedId) {
      setConversationIdState(storedId);
    }
  }, []);

  // Auto-scroll to latest message
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  // Generate unique message ID
  const generateMessageId = () => {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  // Send message handler
  const handleSendMessage = useCallback(
    async (content: string) => {
      // Clear any previous error
      setError(null);

      // Create optimistic user message
      const userMessageId = generateMessageId();
      const userMessage: Message = {
        id: userMessageId,
        role: 'user',
        content,
        timestamp: new Date(),
        pending: true,
      };

      // Add user message to state
      setMessages((prev) => [...prev, userMessage]);
      setPendingMessageId(userMessageId);
      setIsLoading(true);

      try {
        const result = await sendChatMessage(content, conversationId);

        if (result.error) {
          // Handle specific error types
          if (result.error === 'Unauthorized') {
            toast.error('Session expired. Please sign in again.');
            router.push('/signin');
            return;
          }

          // Handle rate limit
          if (result.error.includes('Rate') || result.error.includes('rate')) {
            setError('Rate limit reached. Please wait a moment before sending another message.');
            toast.error('Rate limit reached. Please wait before trying again.');
          } else {
            setError(result.error);
            toast.error(result.error);
          }

          // Mark user message as failed
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === userMessageId ? { ...msg, pending: false, error: result.error } : msg
            )
          );
          return;
        }

        if (result.data) {
          // Mark user message as sent
          setMessages((prev) =>
            prev.map((msg) => (msg.id === userMessageId ? { ...msg, pending: false } : msg))
          );

          // Add assistant response
          const assistantMessage: Message = {
            id: generateMessageId(),
            role: 'assistant',
            content: result.data.response,
            timestamp: new Date(),
            toolCalls: result.data.tool_calls || undefined,
          };

          setMessages((prev) => [...prev, assistantMessage]);

          // Store conversation ID
          if (result.data.conversation_id) {
            setConversationIdState(result.data.conversation_id);
            setConversationId(result.data.conversation_id);
          }
        }
      } catch (err) {
        console.error('Chat error:', err);
        const errorMessage = 'Connection error. Please check your network and try again.';
        setError(errorMessage);
        toast.error(errorMessage);

        // Mark user message as failed
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === userMessageId ? { ...msg, pending: false, error: errorMessage } : msg
          )
        );
      } finally {
        setIsLoading(false);
        setPendingMessageId(null);
      }
    },
    [conversationId, router]
  );

  // Retry failed message
  const handleRetry = useCallback(
    (messageId: string) => {
      const failedMessage = messages.find((msg) => msg.id === messageId);
      if (failedMessage) {
        // Remove failed message
        setMessages((prev) => prev.filter((msg) => msg.id !== messageId));
        // Resend
        handleSendMessage(failedMessage.content);
      }
    },
    [messages, handleSendMessage]
  );

  return (
    <div className={`flex flex-col h-full bg-white ${className}`}>
      {/* Header */}
      <div className="flex-shrink-0 border-b border-gray-200 px-6 py-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-teal-500 flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">TaskBot</h2>
            <p className="text-sm text-gray-500">Your AI task assistant</p>
          </div>
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {/* Empty state / welcome message */}
        {messages.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-full bg-teal-100 flex items-center justify-center mb-4">
              <svg
                className="w-8 h-8 text-teal-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Welcome to TaskBot!</h3>
            <p className="text-gray-500 max-w-sm">
              I can help you manage your tasks. Try saying &quot;Add a task to buy groceries&quot; or
              &quot;Show me my tasks&quot;.
            </p>
          </div>
        )}

        {/* Message list */}
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            role={message.role}
            content={message.content}
            timestamp={message.timestamp}
            pending={message.pending}
            error={message.error}
            onRetry={message.error ? () => handleRetry(message.id!) : undefined}
          />
        ))}

        {/* Loading indicator */}
        {isLoading && !pendingMessageId && <ChatLoading />}

        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Global error banner */}
      {error && !messages.some((m) => m.error) && (
        <div className="flex-shrink-0 bg-red-50 border-t border-red-200 px-6 py-3">
          <div className="flex items-center text-red-800">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span className="flex-1">{error}</span>
            <button
              onClick={() => setError(null)}
              className="ml-4 text-red-600 hover:text-red-800 focus:outline-none"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Input area */}
      <ChatInput onSend={handleSendMessage} disabled={isLoading} loading={isLoading} />
    </div>
  );
}
