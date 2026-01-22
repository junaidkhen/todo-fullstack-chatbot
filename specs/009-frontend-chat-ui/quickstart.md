# Quickstart: Frontend Chat UI

**Feature**: 009-frontend-chat-ui
**Date**: 2026-01-17

## Prerequisites

Before implementing the Frontend Chat UI, ensure the following are in place:

### 1. Backend Chat Endpoint Running

The backend `/api/{user_id}/chat` endpoint must be operational:

```bash
cd backend

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Start backend server
uvicorn main:app --reload --port 8000
```

Verify with:
```bash
curl -X POST http://localhost:8000/api/test-user/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{"message": "hello", "conversation_id": null}'
```

### 2. Frontend Development Server

Ensure the Next.js frontend is running:

```bash
cd frontend

# Install dependencies (if not done)
npm install

# Start development server
npm run dev
```

Frontend should be accessible at: http://localhost:3000

### 3. Environment Variables

Ensure `.env.local` contains:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key
NEXT_PUBLIC_DEBUG=true
```

### 4. Authentication Working

- User can sign up at `/signup`
- User can sign in at `/signin`
- Protected routes redirect unauthenticated users

---

## Implementation Order

Follow this order for implementing the chat UI:

### Step 1: Create Types File

Create `frontend/src/types/chat.ts` with all TypeScript interfaces from `data-model.md`.

```bash
# Create types directory if needed
mkdir -p frontend/src/types
```

### Step 2: Create Storage Utility

Create `frontend/src/lib/chat-storage.ts` for localStorage operations:

```typescript
const STORAGE_KEY = 'chat_conversation_id';

export const getConversationId = (): number | null => {
  if (typeof window === 'undefined') return null;
  const id = localStorage.getItem(STORAGE_KEY);
  return id ? parseInt(id, 10) : null;
};

export const setConversationId = (id: number): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem(STORAGE_KEY, id.toString());
};

export const clearConversationId = (): void => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(STORAGE_KEY);
};
```

### Step 3: Update API Library

Add chat function to `frontend/src/lib/api.ts`:

```typescript
import { ChatRequest, ChatResponse, ChatError } from '@/types/chat';

export async function sendChatMessage(
  request: ChatRequest
): Promise<{ data?: ChatResponse; error?: string }> {
  return authenticatedFetch<ChatResponse>('/api/chat', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}
```

### Step 4: Create API Route

Create `frontend/src/app/api/chat/route.ts`:

```typescript
import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function POST(request: Request) {
  const cookieStore = await cookies();
  const authToken = cookieStore.get('auth-token')?.value;

  if (!authToken) {
    return NextResponse.json(
      { error: 'UNAUTHORIZED', message: 'Not authenticated' },
      { status: 401 }
    );
  }

  // Extract user_id from JWT (or pass token to backend)
  const body = await request.json();
  const backendUrl = process.env.NEXT_PUBLIC_API_URL;

  // Forward to backend
  const response = await fetch(`${backendUrl}/api/{user_id}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`,
    },
    body: JSON.stringify(body),
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}
```

### Step 5: Create Components

Create components in order:

1. `frontend/src/components/chat/ChatLoading.tsx` - Loading indicator
2. `frontend/src/components/chat/ChatMessage.tsx` - Message bubble
3. `frontend/src/components/chat/ChatInput.tsx` - Input with send button
4. `frontend/src/components/chat/ChatWindow.tsx` - Main container

### Step 6: Create Chat Page

Create `frontend/src/app/chat/page.tsx`:

```typescript
'use client';

import ChatWindow from '@/components/chat/ChatWindow';

export default function ChatPage() {
  return (
    <main className="h-screen flex flex-col">
      <ChatWindow />
    </main>
  );
}
```

### Step 7: Update Middleware

Add `/chat` to protected routes in `frontend/middleware.ts`:

```typescript
const protectedRoutes = ['/tasks', '/profile', '/chat'];
```

### Step 8: Add Navigation

Update `frontend/src/components/Header.tsx` to include chat link:

```tsx
<Link href="/chat">Chat</Link>
```

---

## Testing Commands

### Run Unit Tests

```bash
cd frontend
npm test -- --watch
```

### Run Specific Test File

```bash
npm test -- src/components/chat/ChatWindow.test.tsx
```

### Build Check

```bash
npm run build
```

### Type Check

```bash
npx tsc --noEmit
```

---

## Development Tips

### 1. Mock Backend for UI Development

If backend isn't ready, create a mock API route:

```typescript
// frontend/src/app/api/chat/route.ts (mock version)
export async function POST(request: Request) {
  const body = await request.json();

  // Simulate delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  return NextResponse.json({
    conversation_id: 1,
    response: `You said: "${body.message}"`,
    tool_calls: null,
  });
}
```

### 2. Test Rate Limit Handling

Return 429 from mock to test rate limit UI:

```typescript
return NextResponse.json(
  {
    error: 'RATE_LIMIT',
    message: 'Please wait before sending another message.',
    details: { retry_after_seconds: 60 },
  },
  { status: 429 }
);
```

### 3. Debug State Changes

Add logging to ChatWindow:

```typescript
useEffect(() => {
  console.log('Messages:', messages);
  console.log('ConversationId:', conversationId);
}, [messages, conversationId]);
```

### 4. Clear Conversation for Testing

Use browser dev tools:

```javascript
localStorage.removeItem('chat_conversation_id');
location.reload();
```

---

## File Structure After Implementation

```
frontend/src/
├── app/
│   ├── api/
│   │   ├── chat/
│   │   │   └── route.ts          # NEW
│   │   └── ...
│   ├── chat/
│   │   └── page.tsx              # NEW
│   └── ...
├── components/
│   ├── chat/
│   │   ├── ChatWindow.tsx        # NEW
│   │   ├── ChatMessage.tsx       # NEW
│   │   ├── ChatInput.tsx         # NEW
│   │   └── ChatLoading.tsx       # NEW
│   └── ...
├── lib/
│   ├── api.ts                    # MODIFY: add sendChatMessage
│   └── chat-storage.ts           # NEW
├── types/
│   └── chat.ts                   # NEW
└── middleware.ts                 # MODIFY: add /chat route
```

---

## Acceptance Checklist

Before marking implementation complete:

- [ ] User can navigate to `/chat` when authenticated
- [ ] Unauthenticated users redirected to `/signin`
- [ ] User can type message and press Enter or click Send
- [ ] Empty messages are prevented from sending
- [ ] User messages appear as right-aligned bubbles
- [ ] Loading indicator shows while waiting for response
- [ ] Assistant messages appear as left-aligned bubbles
- [ ] Conversation continues using stored conversation_id
- [ ] Error messages display for network/backend errors
- [ ] Chat auto-scrolls to latest message
- [ ] All TypeScript types pass strict mode

---

*Quickstart generated for Phase 1 of /sp.plan workflow.*
