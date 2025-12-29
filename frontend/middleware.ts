/**
 * Next.js Middleware for Protected Routes
 *
 * Phase II: Redirects unauthenticated users from protected routes.
 *
 * Note: Since we store tokens in localStorage (client-side), we can't check
 * authentication in middleware. Protected routes will handle auth checks
 * client-side using the useAuth hook.
 *
 * This middleware provides basic route configuration for the matcher.
 */

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // For now, just pass through
  // Client-side auth checks will be done in protected page components
  return NextResponse.next();
}

// Only run middleware on specific paths
export const config = {
  matcher: ["/dashboard/:path*"],
};
