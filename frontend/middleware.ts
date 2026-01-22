import { NextRequest, NextResponse } from 'next/server';

// Middleware to protect routes
export function middleware(request: NextRequest) {
  // Define protected routes
  const protectedPaths = ['/tasks', '/chat'];
  const isProtectedPath = protectedPaths.some(path =>
    request.nextUrl.pathname.startsWith(path)
  );

  // If it's a protected path, check for auth token
  if (isProtectedPath) {
    // Check if we have an auth token in cookies
    const authToken = request.cookies.get('auth-token')?.value;

    if (!authToken) {
      // Redirect to signin if no auth token
      const signInUrl = new URL('/signin', request.url);
      return NextResponse.redirect(signInUrl);
    }
  }

  return NextResponse.next();
}

// Apply middleware to specific paths
export const config = {
  matcher: ['/tasks/:path*', '/chat/:path*', '/profile/:path*'], // Apply to protected routes
};