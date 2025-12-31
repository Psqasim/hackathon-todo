"use client";

/**
 * Home Page
 *
 * Phase II: Modern landing page with hero section, features, and CTAs.
 * Shows different navigation based on authentication status.
 */

import { useState, useEffect } from "react";
import Link from "next/link";
import { isAuthenticated } from "@/lib/auth-client";

// Feature icons
function TaskIcon() {
  return (
    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
    </svg>
  );
}

function SecurityIcon() {
  return (
    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
    </svg>
  );
}

function SpeedIcon() {
  return (
    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
  );
}

function PriorityIcon() {
  return (
    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
    </svg>
  );
}

function AiChatIcon() {
  return (
    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
  );
}

function TagsIcon() {
  return (
    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
    </svg>
  );
}

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    // Check authentication status (no redirect)
    setIsLoggedIn(isAuthenticated());
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-50" />

      {/* Gradient Orbs */}
      <div className="absolute top-0 -left-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" />
      <div className="absolute top-0 -right-40 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse delay-1000" />
      <div className="absolute bottom-40 left-1/2 w-80 h-80 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse delay-500" />

      {/* Navigation */}
      <nav className="relative z-10 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-xl flex items-center justify-center shadow-lg">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <span className="text-xl font-bold text-white">TaskFlow</span>
          </div>
          <div className="flex gap-3">
            {isLoggedIn ? (
              <Link
                href="/dashboard"
                className="px-5 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 rounded-lg shadow-lg shadow-blue-500/25 transition-all hover:scale-105"
              >
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link
                  href="/signin"
                  className="px-4 py-2 text-sm font-medium text-white/80 hover:text-white transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  href="/signup"
                  className="px-4 py-2 text-sm font-medium text-white bg-white/10 hover:bg-white/20 rounded-lg backdrop-blur-sm transition-all border border-white/10"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      <main className="relative z-10">
        {/* Hero Section */}
        <section className="px-6 pt-20 pb-32 text-center">
          <div className="max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/10 mb-8">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-sm text-white/80">New: AI Chat Assistant & Smart Task Management</span>
            </div>

            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight">
              Manage Tasks with
              <span className="block bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 text-transparent bg-clip-text">
                Effortless Precision
              </span>
            </h1>

            <p className="text-xl text-white/60 mb-10 max-w-2xl mx-auto leading-relaxed">
              A modern task management app built for productivity. Prioritize, track, and complete your work with a beautiful, intuitive interface.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {isLoggedIn ? (
                <Link
                  href="/dashboard"
                  className="group inline-flex items-center justify-center gap-2 px-8 py-4 text-base font-semibold text-slate-900 bg-white hover:bg-gray-100 rounded-xl shadow-xl shadow-blue-500/25 transition-all hover:shadow-blue-500/40 hover:scale-105"
                >
                  Go to Dashboard
                  <svg className="w-5 h-5 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </Link>
              ) : (
                <>
                  <Link
                    href="/signup"
                    className="group inline-flex items-center justify-center gap-2 px-8 py-4 text-base font-semibold text-slate-900 bg-white hover:bg-gray-100 rounded-xl shadow-xl shadow-blue-500/25 transition-all hover:shadow-blue-500/40 hover:scale-105"
                  >
                    Start Free Today
                    <svg className="w-5 h-5 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </Link>
                  <Link
                    href="/signin"
                    className="inline-flex items-center justify-center gap-2 px-8 py-4 text-base font-semibold text-white bg-white/10 hover:bg-white/20 rounded-xl backdrop-blur-sm border border-white/20 transition-all"
                  >
                    Sign In
                  </Link>
                </>
              )}
            </div>

            {/* Trust Badges */}
            <div className="mt-12 flex items-center justify-center gap-8 text-white/40 text-sm">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <span>Secure Auth</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
                <span>Free Forever</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Real-time Sync</span>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="px-6 py-20 bg-white/5 backdrop-blur-sm">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
                Everything You Need to Stay Organized
              </h2>
              <p className="text-lg text-white/60 max-w-2xl mx-auto">
                Powerful features designed to help you manage tasks efficiently and boost your productivity.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Feature 1 - AI Chat (NEW!) */}
              <div className="group p-6 bg-gradient-to-br from-purple-500/20 to-pink-500/20 hover:from-purple-500/30 hover:to-pink-500/30 rounded-2xl border border-purple-400/30 transition-all hover:scale-105 hover:shadow-xl hover:shadow-purple-500/20 relative overflow-hidden">
                <div className="absolute top-2 right-2 px-2 py-0.5 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full">
                  <span className="text-xs font-bold text-white">NEW</span>
                </div>
                <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mb-4 text-white shadow-lg">
                  <AiChatIcon />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">AI Chat Assistant</h3>
                <p className="text-white/60 text-sm leading-relaxed">
                  Manage tasks with natural language. Just tell the AI what you need - &quot;Add a task for tomorrow&quot;.
                </p>
              </div>

              {/* Feature 2 */}
              <div className="group p-6 bg-white/5 hover:bg-white/10 rounded-2xl border border-white/10 transition-all hover:scale-105 hover:shadow-xl hover:shadow-blue-500/10">
                <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center mb-4 text-white shadow-lg">
                  <TaskIcon />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Easy Task Management</h3>
                <p className="text-white/60 text-sm leading-relaxed">
                  Create, update, and complete tasks with a clean, intuitive interface designed for speed.
                </p>
              </div>

              {/* Feature 3 */}
              <div className="group p-6 bg-white/5 hover:bg-white/10 rounded-2xl border border-white/10 transition-all hover:scale-105 hover:shadow-xl hover:shadow-amber-500/10">
                <div className="w-14 h-14 bg-gradient-to-br from-amber-500 to-orange-500 rounded-xl flex items-center justify-center mb-4 text-white shadow-lg">
                  <PriorityIcon />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Priority Levels</h3>
                <p className="text-white/60 text-sm leading-relaxed">
                  Set priorities from low to urgent. Focus on what matters most with smart sorting.
                </p>
              </div>

              {/* Feature 4 */}
              <div className="group p-6 bg-white/5 hover:bg-white/10 rounded-2xl border border-white/10 transition-all hover:scale-105 hover:shadow-xl hover:shadow-teal-500/10">
                <div className="w-14 h-14 bg-gradient-to-br from-teal-500 to-cyan-500 rounded-xl flex items-center justify-center mb-4 text-white shadow-lg">
                  <TagsIcon />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Tags & Categories</h3>
                <p className="text-white/60 text-sm leading-relaxed">
                  Organize tasks with custom tags. Filter and search to find exactly what you need.
                </p>
              </div>

              {/* Feature 5 */}
              <div className="group p-6 bg-white/5 hover:bg-white/10 rounded-2xl border border-white/10 transition-all hover:scale-105 hover:shadow-xl hover:shadow-green-500/10">
                <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center mb-4 text-white shadow-lg">
                  <SecurityIcon />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Secure & Private</h3>
                <p className="text-white/60 text-sm leading-relaxed">
                  Your data is protected with JWT authentication. Sign in with Google or GitHub.
                </p>
              </div>

              {/* Feature 6 */}
              <div className="group p-6 bg-white/5 hover:bg-white/10 rounded-2xl border border-white/10 transition-all hover:scale-105 hover:shadow-xl hover:shadow-rose-500/10">
                <div className="w-14 h-14 bg-gradient-to-br from-rose-500 to-red-500 rounded-xl flex items-center justify-center mb-4 text-white shadow-lg">
                  <SpeedIcon />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Fast & Responsive</h3>
                <p className="text-white/60 text-sm leading-relaxed">
                  Built with Next.js and FastAPI for blazing-fast performance on any device.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="px-6 py-24 text-center">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
              {isLoggedIn ? "Welcome Back!" : "Ready to Get More Done?"}
            </h2>
            <p className="text-lg text-white/60 mb-10">
              {isLoggedIn
                ? "Your tasks are waiting. Jump back into your dashboard and stay productive."
                : "Join thousands of users who trust TaskFlow for their daily productivity. Start for free today."
              }
            </p>
            <Link
              href={isLoggedIn ? "/dashboard" : "/signup"}
              className="inline-flex items-center justify-center gap-2 px-10 py-4 text-lg font-semibold text-slate-900 bg-gradient-to-r from-blue-400 to-purple-400 hover:from-blue-300 hover:to-purple-300 rounded-xl shadow-xl shadow-purple-500/25 transition-all hover:scale-105"
            >
              {isLoggedIn ? "Go to Dashboard" : "Create Free Account"}
            </Link>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="relative z-10 px-6 py-8 border-t border-white/10">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            {/* Logo & Copyright */}
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <span className="text-white/60 text-sm">TaskFlow &copy; 2025</span>
            </div>

            {/* Developer Info */}
            <div className="flex flex-col items-center gap-2">
              <p className="text-white/60 text-sm">
                Built by <span className="text-white/80 font-medium">Muhammad Qasim</span>
              </p>
              <div className="flex items-center gap-4">
                {/* GitHub */}
                <a
                  href="https://github.com/Psqasim"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-white/50 hover:text-white transition-colors"
                  title="GitHub"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                  </svg>
                </a>
                {/* LinkedIn */}
                <a
                  href="https://www.linkedin.com/in/muhammad-qasim-5bba592b4/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-white/50 hover:text-white transition-colors"
                  title="LinkedIn"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                </a>
                {/* Twitter/X */}
                <a
                  href="https://x.com/psqasim0"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-white/50 hover:text-white transition-colors"
                  title="Twitter/X"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                  </svg>
                </a>
              </div>
            </div>

            {/* Phase Info */}
            <p className="text-white/40 text-sm">
              Phase III: AI-Powered Task Management
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
