import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Chat API Proxy Route
 *
 * Extracts auth-token from cookies and forwards chat requests to backend.
 * Route: POST /api/chat
 * Backend: POST /api/{user_id}/chat
 */
export async function POST(request: NextRequest) {
  try {
    // Get the auth token from the cookie
    const cookieStore = await cookies();
    const token = cookieStore.get('auth-token')?.value;

    if (!token) {
      return NextResponse.json(
        { error: 'UNAUTHORIZED', message: 'Authentication required' },
        { status: 401 }
      );
    }

    // Decode JWT to extract user_id (simple base64 decode of payload)
    let userId: string;
    try {
      const payload = token.split('.')[1];
      const decoded = JSON.parse(atob(payload));
      userId = decoded.sub || decoded.user_id || decoded.id;

      if (!userId) {
        return NextResponse.json(
          { error: 'UNAUTHORIZED', message: 'Invalid token: missing user ID' },
          { status: 401 }
        );
      }
    } catch {
      return NextResponse.json(
        { error: 'UNAUTHORIZED', message: 'Invalid authentication token' },
        { status: 401 }
      );
    }

    // Parse request body
    const body = await request.json();
    const { message, conversation_id } = body;

    // Validate message
    if (!message || typeof message !== 'string' || message.trim().length === 0) {
      return NextResponse.json(
        { error: 'VALIDATION_ERROR', message: 'Message cannot be empty' },
        { status: 400 }
      );
    }

    if (message.length > 10000) {
      return NextResponse.json(
        { error: 'VALIDATION_ERROR', message: 'Message is too long (max 10000 characters)' },
        { status: 400 }
      );
    }

    // Forward the request to the backend
    const backendUrl = `${BACKEND_URL}/api/${userId}/chat`;
    const backendResponse = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message.trim(),
        conversation_id: conversation_id,
      }),
    });

    // Handle rate limiting
    if (backendResponse.status === 429) {
      const errorData = await backendResponse.json().catch(() => ({}));
      return NextResponse.json(
        {
          error: 'RATE_LIMIT',
          message: 'Please wait a moment before sending another message.',
          details: errorData.details || { retry_after_seconds: 60 },
        },
        { status: 429 }
      );
    }

    // Handle other error responses
    if (!backendResponse.ok) {
      const errorData = await backendResponse.json().catch(() => ({}));
      return NextResponse.json(
        {
          error: errorData.error || 'INTERNAL_ERROR',
          message: errorData.message || errorData.detail || 'Failed to process message',
          details: errorData.details,
        },
        { status: backendResponse.status }
      );
    }

    // Return successful response
    const data = await backendResponse.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      {
        error: 'INTERNAL_ERROR',
        message: 'An error occurred while processing your message',
      },
      { status: 500 }
    );
  }
}
