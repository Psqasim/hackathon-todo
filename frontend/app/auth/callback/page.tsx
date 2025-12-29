"use client";

/**
 * OAuth Callback Page
 *
 * Handles OAuth redirects from Google/GitHub.
 * Stores the JWT token and redirects to dashboard.
 */

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { setAuth } from "@/lib/auth-client";
import { Loading } from "@/components/loading";

function AuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const token = searchParams.get("token");
    const userId = searchParams.get("user_id");
    const email = searchParams.get("email");
    const name = searchParams.get("name");
    const errorParam = searchParams.get("error");

    if (errorParam) {
      const errorMessages: Record<string, string> = {
        invalid_state: "Authentication session expired. Please try again.",
        not_configured: "OAuth is not configured. Please use email/password.",
        token_error: "Failed to authenticate. Please try again.",
        userinfo_error: "Failed to get user info. Please try again.",
        no_token: "Authentication failed. Please try again.",
        no_email: "Email access is required. Please allow email access and try again.",
        oauth_error: "An error occurred during authentication. Please try again.",
      };
      setError(errorMessages[errorParam] || "Authentication failed");
      setTimeout(() => router.push("/signin"), 3000);
      return;
    }

    if (token && userId && email) {
      // Store auth data
      setAuth(token, {
        id: userId,
        email,
        name: name || email.split("@")[0],
        created_at: new Date().toISOString(),
      });

      // Redirect to dashboard
      router.push("/dashboard");
    } else {
      setError("Invalid callback data");
      setTimeout(() => router.push("/signin"), 2000);
    }
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full text-center p-8">
          <div className="mb-4">
            <svg
              className="w-16 h-16 mx-auto text-red-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Authentication Error
          </h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <p className="text-sm text-gray-500">Redirecting to sign in...</p>
        </div>
      </div>
    );
  }

  return <Loading message="Completing sign in..." />;
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={<Loading message="Loading..." />}>
      <AuthCallbackContent />
    </Suspense>
  );
}
