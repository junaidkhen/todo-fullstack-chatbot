// src/app/api/auth/signin/route.ts
import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json();

    // Validate input
    if (!email || !password) {
      return NextResponse.json(
        { message: 'Email and password are required' },
        { status: 400 }
      );
    }

    // Forward the request to our backend
    const backendResponse = await fetch(`${BACKEND_URL}/api/auth/signin`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (backendResponse.ok) {
      const data = await backendResponse.json();

      // Create response with success data
      const response = NextResponse.json(
        { message: data.message, user_id: data.user_id },
        { status: 200 }
      );

      // Set the auth token from the backend response as an HTTP-only cookie
      if (data.token) {
        response.cookies.set('auth-token', data.token, {
          httpOnly: true,
          secure: process.env.NODE_ENV === 'production',
          maxAge: 60 * 60 * 24 * 7, // 1 week
          path: '/',
          sameSite: 'strict',
        });
      }

      return response;
    } else {
      const errorData = await backendResponse.json();
      return NextResponse.json(
        { message: errorData.detail || 'Invalid email or password' },
        { status: backendResponse.status }
      );
    }
  } catch (error) {
    console.error('Signin error:', error);
    return NextResponse.json(
      { message: 'An error occurred during signin' },
      { status: 500 }
    );
  }
}