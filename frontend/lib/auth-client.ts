/**
 * Auth Client for Todo Application
 *
 * Phase II: Client-side authentication helpers for Next.js frontend.
 * Communicates with FastAPI backend for auth operations.
 */

// Types
export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface SignupData {
  email: string;
  name: string;
  password: string;
}

export interface SigninData {
  email: string;
  password: string;
}

export interface AuthError {
  error: string;
  detail?: string;
}

// Constants
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const TOKEN_KEY = "todo_auth_token";
const USER_KEY = "todo_auth_user";

/**
 * Store authentication data in localStorage
 */
export function storeAuth(response: AuthResponse): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEY, response.token);
    localStorage.setItem(USER_KEY, JSON.stringify(response.user));
  }
}

/**
 * Set authentication data directly (for OAuth callbacks)
 */
export function setAuth(token: string, user: User): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
}

/**
 * Clear all cookies
 */
function clearAllCookies(): void {
  if (typeof window !== "undefined") {
    document.cookie.split(";").forEach((c) => {
      document.cookie = c
        .replace(/^ +/, "")
        .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
    });
  }
}

/**
 * Clear authentication data from localStorage and cookies
 */
export function clearAuth(): void {
  if (typeof window !== "undefined") {
    // Clear specific auth keys
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);

    // Clear any OAuth state
    localStorage.removeItem("oauth_state");
    sessionStorage.removeItem("oauth_state");

    // Clear all cookies (for OAuth sessions)
    clearAllCookies();
  }
}

/**
 * Get the current auth token
 */
export function getToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem(TOKEN_KEY);
  }
  return null;
}

/**
 * Get the current user from localStorage
 */
export function getStoredUser(): User | null {
  if (typeof window !== "undefined") {
    const userJson = localStorage.getItem(USER_KEY);
    if (userJson) {
      try {
        return JSON.parse(userJson) as User;
      } catch {
        return null;
      }
    }
  }
  return null;
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getToken() !== null;
}

/**
 * Sign up a new user
 */
export async function signup(data: SignupData): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/api/auth/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Signup failed");
  }

  const authResponse = (await response.json()) as AuthResponse;
  storeAuth(authResponse);
  return authResponse;
}

/**
 * Sign in an existing user
 */
export async function signin(data: SigninData): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/api/auth/signin`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Sign in failed");
  }

  const authResponse = (await response.json()) as AuthResponse;
  storeAuth(authResponse);
  return authResponse;
}

/**
 * Sign out the current user
 * Clears all auth state immediately, then notifies backend
 */
export async function signout(): Promise<void> {
  // Clear auth FIRST for instant logout experience
  clearAuth();

  // Notify backend (non-blocking, fire-and-forget)
  try {
    fetch(`${API_URL}/api/auth/signout`, {
      method: "POST",
    }).catch(() => {
      // Ignore errors - user is already logged out locally
    });
  } catch {
    // Ignore - local logout is what matters
  }
}

/**
 * Get current user from API (validates token)
 */
export async function getCurrentUser(): Promise<User | null> {
  const token = getToken();
  if (!token) {
    return null;
  }

  try {
    const response = await fetch(`${API_URL}/api/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      // Token is invalid, clear auth
      clearAuth();
      return null;
    }

    return (await response.json()) as User;
  } catch {
    return null;
  }
}
