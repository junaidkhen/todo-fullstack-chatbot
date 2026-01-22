// src/app/api/auth/signout/route.ts
import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    // Extract the auth token from cookies
    const authCookie = request.cookies.get('auth-token');

    if (!authCookie) {
      return NextResponse.json(
        { message: 'Not authenticated' },
        { status: 401 }
      );
    }

    // Forward the request to the backend
    const backendResponse = await fetch(`${BACKEND_URL}/api/auth/signout`, {
      method: 'POST',
      headers: {
        'Cookie': `auth-token=${authCookie.value}`,
        'Content-Type': 'application/json',
      },
    });

    if (backendResponse.ok) {
      // Create response and clear the auth cookie
      const response = NextResponse.json(
        { message: 'Signed out successfully' },
        { status: 200 }
      );

      // Clear the auth token cookie
      response.cookies.delete('auth-token');

      return response;
    } else {
      const errorData = await backendResponse.json();
      return NextResponse.json(
        { message: errorData.detail || 'Signout failed' },
        { status: backendResponse.status }
      );
    }
  } catch (error) {
    return NextResponse.json(
      { message: 'An error occurred during signout' },
      { status: 500 }
    );
  }
}