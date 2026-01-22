import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    // Get the auth token from the cookie
    const cookieStore = await cookies();
    const token = cookieStore.get('auth-token')?.value;

    if (!token) {
      return NextResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      );
    }

    // Forward the request to the backend with the Authorization header
    const backendResponse = await fetch(`${BACKEND_URL}/api/tasks/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (backendResponse.ok) {
      const data = await backendResponse.json();
      return NextResponse.json(data);
    } else {
      const errorData = await backendResponse.json();
      return NextResponse.json(
        { detail: errorData.detail || 'Failed to fetch tasks' },
        { status: backendResponse.status }
      );
    }
  } catch (error) {
    console.error('Error fetching tasks:', error);
    return NextResponse.json(
      { detail: 'An error occurred while fetching tasks' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    // Get the auth token from the cookie
    const cookieStore = await cookies();
    const token = cookieStore.get('auth-token')?.value;

    if (!token) {
      return NextResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      );
    }

    const body = await request.json();
    const { title, description } = body;

    // Validate input
    if (!title || title.trim().length === 0) {
      return NextResponse.json(
        { detail: 'Title is required' },
        { status: 400 }
      );
    }

    // Forward the request to the backend with the Authorization header
    const backendResponse = await fetch(`${BACKEND_URL}/api/tasks/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title, description }),
    });

    if (backendResponse.ok) {
      const data = await backendResponse.json();
      return NextResponse.json(data);
    } else {
      const errorData = await backendResponse.json();
      return NextResponse.json(
        { detail: errorData.detail || 'Failed to create task' },
        { status: backendResponse.status }
      );
    }
  } catch (error) {
    console.error('Error creating task:', error);
    return NextResponse.json(
      { detail: 'An error occurred while creating task' },
      { status: 500 }
    );
  }
}