'use client';

import Header from '@/components/Header';
import ChatWindow from '@/components/chat/ChatWindow';

/**
 * Chat Page
 *
 * Full-page chat interface for interacting with TaskBot AI assistant.
 * Protected route - requires authentication.
 */
export default function ChatPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <Header />

      {/* Chat Container */}
      <main className="flex-1 flex flex-col max-w-4xl w-full mx-auto">
        <div className="flex-1 flex flex-col bg-white shadow-sm border-x border-gray-200">
          <ChatWindow className="flex-1" />
        </div>
      </main>
    </div>
  );
}
