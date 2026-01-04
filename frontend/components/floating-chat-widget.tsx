"use client";

/**
 * Floating Chat Widget Component
 *
 * Phase III UI Enhancement: A floating AI chat button/card that appears on
 * Dashboard and Home pages. Similar to PanaChat design reference.
 * Shows greeting message and navigates to /chat on click.
 */

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface FloatingChatWidgetProps {
  userName?: string;
}

export function FloatingChatWidget({ userName }: FloatingChatWidgetProps) {
  const router = useRouter();
  const [isVisible, setIsVisible] = useState(false);
  const [showCard, setShowCard] = useState(true);

  // Show widget after a short delay for smooth entrance
  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 800);
    return () => clearTimeout(timer);
  }, []);

  const handleClick = () => {
    router.push("/chat");
  };

  const handleCloseCard = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowCard(false);
  };

  const firstName = userName?.split(" ")[0] || "";

  return (
    <div
      className={`
        fixed bottom-6 right-6 z-50
        transition-all duration-700 ease-out
        ${isVisible ? "translate-y-0 opacity-100" : "translate-y-12 opacity-0"}
      `}
    >
      {/* Greeting Card - Similar to PanaChat */}
      {showCard && (
        <div
          onClick={handleClick}
          className="
            absolute bottom-[70px] right-0
            bg-white rounded-2xl
            shadow-xl shadow-slate-200/60
            border border-slate-100
            p-4 pr-10
            min-w-[240px] max-w-[280px]
            cursor-pointer
            hover:shadow-2xl hover:border-slate-200
            transition-all duration-300
            animate-in slide-in-from-bottom-4 fade-in duration-500
          "
        >
          {/* Close button */}
          <button
            onClick={handleCloseCard}
            className="
              absolute top-2 right-2
              w-6 h-6 rounded-full
              text-slate-400 hover:text-slate-600 hover:bg-slate-100
              flex items-center justify-center
              transition-colors
            "
            aria-label="Close"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          {/* Greeting text */}
          <div className="space-y-1">
            <p className="text-base font-semibold text-slate-800">
              Hi{firstName ? ` ${firstName}` : ""}! I&apos;m TaskFlow AI
            </p>
            <p className="text-sm text-slate-500">
              How can I assist you today?
            </p>
          </div>

          {/* Arrow pointer */}
          <div
            className="
              absolute -bottom-2 right-8
              w-4 h-4 bg-white
              border-b border-r border-slate-100
              transform rotate-45
            "
          />
        </div>
      )}

      {/* Floating Action Button */}
      <button
        onClick={handleClick}
        className="
          group
          w-14 h-14
          rounded-full
          bg-gradient-to-br from-emerald-400 to-teal-500
          text-white
          shadow-lg shadow-emerald-500/30
          hover:shadow-xl hover:shadow-emerald-500/40
          hover:scale-105
          active:scale-95
          transition-all duration-200
          focus:outline-none focus:ring-4 focus:ring-emerald-300/50 focus:ring-offset-2
          flex items-center justify-center
        "
        aria-label="Open AI Chat Assistant"
        title="Chat with AI Assistant"
      >
        {/* Chat icon */}
        <svg
          className="w-6 h-6 transition-transform duration-200 group-hover:scale-110"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
      </button>
    </div>
  );
}
