"use client";

/**
 * Footer Component
 *
 * Reusable footer for Dashboard and Chat pages.
 * Matches the styling of the homepage footer.
 */

import Link from "next/link";

interface FooterProps {
  variant?: "light" | "dark";
}

export function Footer({ variant = "light" }: FooterProps) {
  const isDark = variant === "dark";

  return (
    <footer
      className={`
        relative z-10 px-6 py-6 border-t
        ${isDark
          ? "border-white/10 bg-slate-900/50 backdrop-blur-sm"
          : "border-slate-200 bg-white"
        }
      `}
    >
      <div className="max-w-4xl mx-auto">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          {/* Logo & App Name */}
          <Link href="/" className="flex items-center gap-2 group">
            <div
              className={`
                w-8 h-8 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110
                ${isDark
                  ? "bg-gradient-to-br from-blue-400 to-indigo-500"
                  : "bg-gradient-to-br from-blue-500 to-blue-600"
                }
              `}
            >
              <svg
                className="w-4 h-4 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                />
              </svg>
            </div>
            <span className={`text-sm font-medium ${isDark ? "text-white/60" : "text-slate-500"}`}>
              TaskFlow &copy; 2025
            </span>
          </Link>

          {/* Developer Info */}
          <div className="flex flex-col items-center gap-2">
            <p className={`text-sm ${isDark ? "text-white/60" : "text-slate-500"}`}>
              Built by{" "}
              <a
                href="https://github.com/Psqasim"
                target="_blank"
                rel="noopener noreferrer"
                className={`font-medium hover:underline ${isDark ? "text-white/80" : "text-slate-700"}`}
              >
                Muhammad Qasim
              </a>
            </p>
            <div className="flex items-center gap-4">
              {/* GitHub */}
              <a
                href="https://github.com/Psqasim"
                target="_blank"
                rel="noopener noreferrer"
                className={`transition-colors ${isDark
                  ? "text-white/50 hover:text-white"
                  : "text-slate-400 hover:text-slate-700"
                }`}
                title="GitHub"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path
                    fillRule="evenodd"
                    d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                    clipRule="evenodd"
                  />
                </svg>
              </a>
              {/* LinkedIn */}
              <a
                href="https://www.linkedin.com/in/muhammad-qasim-5bba592b4/"
                target="_blank"
                rel="noopener noreferrer"
                className={`transition-colors ${isDark
                  ? "text-white/50 hover:text-white"
                  : "text-slate-400 hover:text-slate-700"
                }`}
                title="LinkedIn"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                </svg>
              </a>
              {/* Twitter/X */}
              <a
                href="https://x.com/psqasim0"
                target="_blank"
                rel="noopener noreferrer"
                className={`transition-colors ${isDark
                  ? "text-white/50 hover:text-white"
                  : "text-slate-400 hover:text-slate-700"
                }`}
                title="Twitter/X"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className={`text-sm transition-colors ${isDark
                ? "text-white/50 hover:text-white"
                : "text-slate-400 hover:text-slate-700"
              }`}
            >
              Dashboard
            </Link>
            <Link
              href="/chat"
              className={`text-sm transition-colors ${isDark
                ? "text-white/50 hover:text-white"
                : "text-slate-400 hover:text-slate-700"
              }`}
            >
              AI Chat
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
