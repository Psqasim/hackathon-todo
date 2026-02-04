/**
 * API Proxy Route Handler
 *
 * Purpose: Proxy API requests from browser to backend service
 *
 * Why needed:
 * - Browser cannot resolve Kubernetes internal service names (backend-service)
 * - NEXT_PUBLIC_API_URL is embedded at build time, can't be changed at runtime
 * - This proxy runs server-side in K8s and can resolve internal service names
 *
 * Flow:
 * 1. Browser calls: /api/proxy/tasks (relative URL)
 * 2. Next.js server proxies to: http://backend-service:8000/api/tasks
 * 3. Backend processes request and returns response
 * 4. Proxy returns response to browser
 *
 * Usage in frontend:
 * - Before: fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/tasks`)
 * - After:  fetch('/api/proxy/tasks')
 */

import { NextRequest, NextResponse } from 'next/server';

// Backend service URL (internal Kubernetes service name)
// In K8s: http://backend-service:8000
// In local dev: http://localhost:7860 or http://localhost:8000
const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://backend-service:8000';

console.log('[API Proxy] Backend URL:', BACKEND_URL);

/**
 * Helper function to proxy requests
 */
async function proxyRequest(
  request: NextRequest,
  method: string,
  params: { path: string[] }
): Promise<NextResponse> {
  try {
    const path = params.path.join('/');
    const searchParams = request.nextUrl.searchParams.toString();

    // Most backend endpoints use /api prefix, except /health
    // - /health -> /health (no prefix)
    // - auth/signin -> /api/auth/signin
    // - users/123/tasks -> /api/users/123/tasks
    const backendPath = path === 'health' ? path : `api/${path}`;
    const url = `${BACKEND_URL}/${backendPath}${searchParams ? `?${searchParams}` : ''}`;

    console.log(`[API Proxy] ${method} ${path} -> ${url}`);

    // Prepare headers (forward most headers from original request)
    const headers: HeadersInit = {};

    // Forward important headers
    const headersToForward = [
      'authorization',
      'content-type',
      'cookie',
      'x-requested-with',
      'accept',
    ];

    headersToForward.forEach((header) => {
      const value = request.headers.get(header);
      if (value) {
        headers[header] = value;
      }
    });

    // Prepare fetch options
    const fetchOptions: RequestInit = {
      method,
      headers,
    };

    // Add body for POST, PUT, PATCH, DELETE
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
      const contentType = request.headers.get('content-type');

      if (contentType?.includes('application/json')) {
        try {
          const body = await request.json();
          fetchOptions.body = JSON.stringify(body);
          headers['content-type'] = 'application/json';
        } catch (e) {
          console.error('[API Proxy] Failed to parse JSON body:', e);
        }
      } else if (contentType?.includes('multipart/form-data')) {
        // Forward FormData as-is
        fetchOptions.body = await request.formData();
      } else {
        // Forward raw body
        const body = await request.text();
        if (body) {
          fetchOptions.body = body;
        }
      }
    }

    // Make the proxied request
    const response = await fetch(url, fetchOptions);

    // Get response body
    const contentType = response.headers.get('content-type');
    let data: any;

    if (contentType?.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    // Forward response headers
    const responseHeaders = new Headers();

    // Forward important response headers
    const responseHeadersToForward = [
      'content-type',
      'cache-control',
      'set-cookie',
    ];

    responseHeadersToForward.forEach((header) => {
      const value = response.headers.get(header);
      if (value) {
        responseHeaders.set(header, value);
      }
    });

    // Return proxied response
    return new NextResponse(
      typeof data === 'string' ? data : JSON.stringify(data),
      {
        status: response.status,
        statusText: response.statusText,
        headers: responseHeaders,
      }
    );

  } catch (error) {
    console.error('[API Proxy] Error:', error);

    // Return error response
    return NextResponse.json(
      {
        error: 'Proxy request failed',
        message: error instanceof Error ? error.message : 'Unknown error',
        backend_url: BACKEND_URL,
      },
      { status: 500 }
    );
  }
}

/**
 * GET handler
 * Note: Next.js 16 changed params to be a Promise that must be awaited
 */
export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  return proxyRequest(request, 'GET', params);
}

/**
 * POST handler
 */
export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  return proxyRequest(request, 'POST', params);
}

/**
 * PUT handler
 */
export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  return proxyRequest(request, 'PUT', params);
}

/**
 * PATCH handler
 */
export async function PATCH(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  return proxyRequest(request, 'PATCH', params);
}

/**
 * DELETE handler
 */
export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  return proxyRequest(request, 'DELETE', params);
}
