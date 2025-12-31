"use client";

/**
 * Chat Page - AI Task Assistant
 *
 * Phase III: Mobile-first chat interface for natural language task management.
 *
 * Architecture:
 * - Chat history stored in OpenAI Conversations API (NOT PostgreSQL)
 * - conversation_ids stored in localStorage for sidebar
 * - Each conversation maps to one OpenAI conversation thread
 * - Backend is stateless
 *
 * Features:
 * - ChatGPT-style conversation sidebar (localStorage-based)
 * - Message history per conversation (session-only, from OpenAI memory)
 * - Quick action suggestions
 */

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";
import { Loading } from "@/components/loading";
import {
  isAuthenticated,
  getStoredUser,
  getCurrentUser,
  type User,
} from "@/lib/auth-client";
import {
  sendChatMessage,
  deleteConversation,
  type ChatMessage,
  type ChatResponse,
  ApiError,
} from "@/lib/api-client";

// =============================================================================
// Types for localStorage conversation storage
// =============================================================================

interface StoredConversation {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  // Note: Messages are NOT stored - they live in OpenAI's Conversations API
}

// =============================================================================
// localStorage helpers
// =============================================================================

const CONVERSATIONS_KEY = "taskflow_conversations";
const PRIVACY_CONSENT_KEY = "taskflow_chat_privacy_consent";

function hasPrivacyConsent(): boolean {
  if (typeof window === "undefined") return false;
  return localStorage.getItem(PRIVACY_CONSENT_KEY) === "true";
}

function setPrivacyConsent(): void {
  localStorage.setItem(PRIVACY_CONSENT_KEY, "true");
}

function getStoredConversations(): StoredConversation[] {
  if (typeof window === "undefined") return [];
  try {
    const stored = localStorage.getItem(CONVERSATIONS_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

function saveConversation(conv: StoredConversation) {
  const conversations = getStoredConversations();
  const existingIndex = conversations.findIndex((c) => c.id === conv.id);

  if (existingIndex >= 0) {
    // Update existing
    conversations[existingIndex] = conv;
  } else {
    // Add new at beginning
    conversations.unshift(conv);
  }

  // Keep only last 50 conversations
  const trimmed = conversations.slice(0, 50);
  localStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(trimmed));
  return trimmed;
}

function removeStoredConversation(id: string): StoredConversation[] {
  const conversations = getStoredConversations();
  const filtered = conversations.filter((c) => c.id !== id);
  localStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(filtered));
  return filtered;
}

// =============================================================================
// Components
// =============================================================================

// Message bubble component
function MessageBubble({
  message,
  isUser,
}: {
  message: ChatMessage;
  isUser: boolean;
}) {
  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}
    >
      <div
        className={`
          max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3
          ${
            isUser
              ? "bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-br-md"
              : "bg-white border border-slate-200 text-slate-800 rounded-bl-md shadow-sm"
          }
        `}
      >
        {/* Message content */}
        <div className="text-sm sm:text-base whitespace-pre-wrap break-words">
          {message.content}
        </div>

        {/* Tool calls indicator (for assistant messages) */}
        {!isUser && message.tool_calls && message.tool_calls.length > 0 && (
          <div className="mt-2 pt-2 border-t border-slate-100">
            <p className="text-xs text-slate-400 flex items-center gap-1">
              <svg
                className="w-3 h-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
              {message.tool_calls.length} action
              {message.tool_calls.length > 1 ? "s" : ""} performed
            </p>
          </div>
        )}

        {/* Timestamp */}
        <p
          className={`text-xs mt-1 ${
            isUser ? "text-blue-200" : "text-slate-400"
          }`}
        >
          {new Date(message.created_at).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
    </div>
  );
}

// Typing indicator component
function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4">
      <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
        </div>
      </div>
    </div>
  );
}

// Conversation Sidebar Item
function ConversationItem({
  conversation,
  isActive,
  onClick,
  onDelete,
}: {
  conversation: StoredConversation;
  isActive: boolean;
  onClick: () => void;
  onDelete: () => void;
}) {
  const [showDelete, setShowDelete] = useState(false);

  return (
    <div
      className={`
        group relative flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer
        transition-colors duration-150
        ${isActive
          ? "bg-blue-50 border border-blue-200"
          : "hover:bg-slate-100 border border-transparent"
        }
      `}
      onClick={onClick}
      onMouseEnter={() => setShowDelete(true)}
      onMouseLeave={() => setShowDelete(false)}
    >
      {/* Chat icon */}
      <svg
        className={`w-4 h-4 flex-shrink-0 ${isActive ? "text-blue-500" : "text-slate-400"}`}
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

      {/* Title */}
      <div className="flex-1 min-w-0">
        <p className={`text-sm truncate ${isActive ? "text-blue-700 font-medium" : "text-slate-700"}`}>
          {conversation.title || "New conversation"}
        </p>
        <p className="text-xs text-slate-400 truncate">
          {new Date(conversation.updatedAt).toLocaleDateString()}
        </p>
      </div>

      {/* Delete button */}
      {showDelete && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="p-1 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
          title="Delete conversation"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </button>
      )}
    </div>
  );
}

// Quick action suggestions
const QUICK_ACTIONS = [
  { label: "Show my tasks", message: "Show me all my tasks" },
  { label: "Add a task", message: "Add a new task: " },
  { label: "What's due today?", message: "What tasks are due today?" },
  { label: "Complete a task", message: "Mark my latest task as complete" },
];

// Privacy Notice Modal Component
function PrivacyNoticeModal({
  onAgree,
  onDecline,
}: {
  onAgree: () => void;
  onDecline: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden animate-in fade-in zoom-in duration-300">
        {/* Header with gradient */}
        <div className="bg-gradient-to-r from-purple-500 to-pink-500 px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Privacy Notice</h2>
              <p className="text-sm text-white/80">Please read before continuing</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-5">
          <p className="text-slate-600 mb-4">
            To provide AI-powered task assistance, we use OpenAI&apos;s services. Here&apos;s how your data is handled:
          </p>

          <div className="space-y-3">
            {/* Task data */}
            <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-slate-800">Your Tasks</p>
                <p className="text-xs text-slate-500">Stored securely in our database</p>
              </div>
            </div>

            {/* Chat history */}
            <div className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg">
              <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-slate-800">Chat History</p>
                <p className="text-xs text-slate-500">Stored with OpenAI for up to 30 days</p>
              </div>
            </div>

            {/* No training */}
            <div className="flex items-start gap-3 p-3 bg-emerald-50 rounded-lg">
              <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-slate-800">Not Used for Training</p>
                <p className="text-xs text-slate-500">Your data is never used to train AI models</p>
              </div>
            </div>
          </div>

          <p className="text-xs text-slate-400 mt-4 text-center">
            By continuing, you agree to these data handling practices.
          </p>
        </div>

        {/* Actions */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex flex-col sm:flex-row gap-3">
          <button
            onClick={onDecline}
            className="flex-1 px-4 py-2.5 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-100 transition-colors"
          >
            Go to Dashboard
          </button>
          <button
            onClick={onAgree}
            className="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all shadow-sm"
          >
            I Agree &amp; Continue
          </button>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export default function ChatPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string>("");
  const [conversationId, setConversationId] = useState<string | undefined>();

  // Sidebar state - conversations stored in localStorage
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [conversations, setConversations] = useState<StoredConversation[]>([]);

  // Privacy consent state
  const [showPrivacyNotice, setShowPrivacyNotice] = useState(false);
  const [hasConsent, setHasConsent] = useState(true); // Default true to avoid flash

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Check authentication and privacy consent
  useEffect(() => {
    const checkAuth = async () => {
      setIsLoading(true);

      if (!isAuthenticated()) {
        router.push("/signin");
        return;
      }

      let currentUser = getStoredUser();
      const validatedUser = await getCurrentUser();

      if (!validatedUser) {
        router.push("/signin");
        return;
      }

      currentUser = validatedUser;
      setUser(currentUser);

      // Check privacy consent
      const consentGiven = hasPrivacyConsent();
      setHasConsent(consentGiven);
      if (!consentGiven) {
        setShowPrivacyNotice(true);
      }

      setIsLoading(false);
    };

    checkAuth();
  }, [router]);

  // Handle privacy consent
  const handlePrivacyAgree = () => {
    setPrivacyConsent();
    setHasConsent(true);
    setShowPrivacyNotice(false);
  };

  const handlePrivacyDecline = () => {
    router.push("/dashboard");
  };

  // Load conversations from localStorage when user is authenticated
  useEffect(() => {
    if (user) {
      setConversations(getStoredConversations());
    }
  }, [user]);

  // Select a conversation (just sets the conversation ID, OpenAI has the history)
  const selectConversation = (conv: StoredConversation) => {
    // Clear current messages (will be populated by continuing the conversation)
    setMessages([]);
    setConversationId(conv.id);
    setSidebarOpen(false);
    // Note: We don't fetch old messages - OpenAI's Conversations API
    // maintains the context, so the agent will remember previous messages
  };

  // Delete a conversation
  const handleDeleteConversation = async (convId: string) => {
    if (!confirm("Delete this conversation? This cannot be undone.")) {
      return;
    }

    try {
      // Try to delete from OpenAI (may fail silently)
      await deleteConversation(convId);
    } catch {
      // Ignore errors - just remove from localStorage
    }

    // Remove from localStorage
    const updated = removeStoredConversation(convId);
    setConversations(updated);

    // If we deleted the current conversation, start fresh
    if (convId === conversationId) {
      handleNewConversation();
    }
  };

  // Auto-resize textarea
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);

    // Auto-resize
    const textarea = e.target;
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + "px";
  };

  // Send message handler
  const handleSendMessage = async (messageText?: string) => {
    const text = messageText || inputValue.trim();
    if (!text || isSending) return;

    setError("");
    setIsSending(true);

    // Create optimistic user message
    const userMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");

    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
    }

    try {
      const response: ChatResponse = await sendChatMessage(text, conversationId);

      // Update conversation ID for continuity
      const isNewConversation = !conversationId;

      if (isNewConversation || conversationId !== response.conversation_id) {
        setConversationId(response.conversation_id);

        // Save to localStorage with title from first message
        const conv: StoredConversation = {
          id: response.conversation_id,
          title: text.slice(0, 50) + (text.length > 50 ? "..." : ""),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        const updated = saveConversation(conv);
        setConversations(updated);
      } else {
        // Update existing conversation's timestamp
        const conv = conversations.find((c) => c.id === conversationId);
        if (conv) {
          const updated = saveConversation({
            ...conv,
            updatedAt: new Date().toISOString(),
          });
          setConversations(updated);
        }
      }

      // Add assistant response
      setMessages((prev) => [...prev, response.message]);
    } catch (err) {
      // Remove the optimistic message on error
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));

      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to send message. Please try again.");
      }
    } finally {
      setIsSending(false);
    }
  };

  // Handle Enter key (send on Enter, new line on Shift+Enter)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Handle quick action click
  const handleQuickAction = (message: string) => {
    if (message.endsWith(": ")) {
      // For "Add a task:" type prompts, put cursor at the end
      setInputValue(message);
      inputRef.current?.focus();
    } else {
      handleSendMessage(message);
    }
  };

  // Start new conversation
  const handleNewConversation = () => {
    setMessages([]);
    setConversationId(undefined);
    setError("");
  };

  // Loading state
  if (isLoading || !user) {
    return <Loading message="Loading chat..." />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 flex flex-col">
      {/* Privacy Notice Modal */}
      {showPrivacyNotice && (
        <PrivacyNoticeModal
          onAgree={handlePrivacyAgree}
          onDecline={handlePrivacyDecline}
        />
      )}

      <Header user={user} />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar Overlay (mobile) */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black/50 z-20 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Conversation Sidebar */}
        <aside
          className={`
            fixed lg:relative inset-y-0 left-0 z-30
            w-72 bg-white border-r border-slate-200
            transform transition-transform duration-300 ease-in-out
            ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
            flex flex-col
            pt-16 lg:pt-0
          `}
        >
          {/* Sidebar Header */}
          <div className="p-4 border-b border-slate-200">
            <button
              onClick={handleNewConversation}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all shadow-sm"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span className="font-medium">New Chat</span>
            </button>
          </div>

          {/* Conversations List */}
          <div className="flex-1 overflow-y-auto p-2">
            {conversations.length === 0 ? (
              <div className="text-center py-8 px-4">
                <svg
                  className="w-12 h-12 mx-auto text-slate-300 mb-3"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
                <p className="text-sm text-slate-500">No conversations yet</p>
                <p className="text-xs text-slate-400 mt-1">Start chatting to create one</p>
              </div>
            ) : (
              <div className="space-y-1">
                {conversations.map((conv) => (
                  <ConversationItem
                    key={conv.id}
                    conversation={conv}
                    isActive={conv.id === conversationId}
                    onClick={() => selectConversation(conv)}
                    onDelete={() => handleDeleteConversation(conv.id)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Sidebar Footer - Back to Tasks */}
          <div className="p-3 border-t border-slate-200">
            <Link
              href="/dashboard"
              className="flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              </svg>
              <span>Back to Tasks</span>
            </Link>
          </div>
        </aside>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col max-w-3xl mx-auto w-full">
          {/* Chat Header */}
          <div className="bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              {/* Sidebar toggle (mobile) */}
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 text-slate-500 hover:bg-slate-100 rounded-lg"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>

              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-sm">
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  />
                </svg>
              </div>
              <div>
                <h2 className="font-semibold text-slate-800">Task Assistant</h2>
                <p className="text-xs text-slate-500">
                  Powered by AI - Ask me anything about your tasks
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {/* New conversation button */}
              {messages.length > 0 && (
                <button
                  onClick={handleNewConversation}
                  className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                  title="New conversation"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 4v16m8-8H4"
                    />
                  </svg>
                </button>
              )}

              {/* Back to dashboard (desktop) */}
              <Link
                href="/dashboard"
                className="hidden sm:flex items-center gap-1 px-3 py-1.5 text-sm text-slate-600 hover:text-blue-600 hover:bg-slate-100 rounded-lg transition-colors"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 10h16M4 14h16M4 18h16"
                  />
                </svg>
                <span>Tasks</span>
              </Link>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-4 py-6">
            {messages.length === 0 ? (
              // Welcome state
              <div className="h-full flex flex-col items-center justify-center text-center px-4">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-6 shadow-lg shadow-purple-500/20">
                  <svg
                    className="w-10 h-10 text-white"
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
                </div>
                <h3 className="text-2xl font-bold text-slate-800 mb-2">
                  Hi {user.name?.split(" ")[0] || "there"}!
                </h3>
                <p className="text-slate-500 mb-8 max-w-md">
                  I&apos;m your AI task assistant. Tell me what you need help with
                  - create tasks, check what&apos;s due, or manage your to-do
                  list.
                </p>

                {/* Quick actions */}
                <div className="flex flex-wrap justify-center gap-2 max-w-md">
                  {QUICK_ACTIONS.map((action) => (
                    <button
                      key={action.label}
                      onClick={() => handleQuickAction(action.message)}
                      className="px-4 py-2 text-sm bg-white border border-slate-200 rounded-full text-slate-600 hover:border-blue-300 hover:text-blue-600 hover:bg-blue-50 transition-all shadow-sm"
                    >
                      {action.label}
                    </button>
                  ))}
                </div>

                {/* Info about conversation continuity */}
                {conversationId && (
                  <p className="text-xs text-slate-400 mt-6">
                    Continuing conversation... The assistant remembers your previous messages.
                  </p>
                )}
              </div>
            ) : (
              // Message list
              <div>
                {messages.map((message) => (
                  <MessageBubble
                    key={message.id}
                    message={message}
                    isUser={message.role === "user"}
                  />
                ))}
                {isSending && <TypingIndicator />}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Error message */}
          {error && (
            <div className="px-4 pb-2">
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2">
                <svg
                  className="w-5 h-5 text-red-500 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
                <p className="text-sm text-red-700">{error}</p>
                <button
                  onClick={() => setError("")}
                  className="ml-auto text-red-400 hover:text-red-600"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="bg-white border-t border-slate-200 px-4 py-4">
            <div className="flex items-end gap-2">
              <div className="flex-1 relative">
                <textarea
                  ref={inputRef}
                  value={inputValue}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyDown}
                  placeholder="Type a message..."
                  rows={1}
                  disabled={isSending}
                  className="
                    w-full px-4 py-3 pr-12
                    bg-slate-50 border border-slate-200 rounded-xl
                    text-slate-800 placeholder:text-slate-400
                    focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-transparent
                    disabled:opacity-50 disabled:cursor-not-allowed
                    resize-none transition-all
                  "
                  style={{ minHeight: "48px", maxHeight: "150px" }}
                />
              </div>

              <button
                onClick={() => handleSendMessage()}
                disabled={!inputValue.trim() || isSending}
                className="
                  p-3 rounded-xl
                  bg-gradient-to-r from-blue-500 to-blue-600
                  text-white shadow-lg shadow-blue-500/25
                  hover:from-blue-600 hover:to-blue-700
                  focus:outline-none focus:ring-2 focus:ring-blue-300 focus:ring-offset-2
                  disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none
                  transition-all duration-200
                "
              >
                {isSending ? (
                  <svg
                    className="w-5 h-5 animate-spin"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                ) : (
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                    />
                  </svg>
                )}
              </button>
            </div>

            <p className="text-xs text-slate-400 mt-2 text-center">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
