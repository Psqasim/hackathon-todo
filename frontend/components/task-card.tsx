"use client";

/**
 * Task Card Component
 *
 * Phase II: Professional task card with depth, status badges, and smooth interactions.
 * Features: Priority badges, due dates, tags, hover effects, accessibility.
 */

import { useState } from "react";
import type { Task, TaskPriority } from "@/lib/api-client";

interface TaskCardProps {
  task: Task;
  onComplete: (taskId: string, completed: boolean) => void;
  onDelete: (taskId: string) => void;
  onEdit?: (task: Task) => void;
  isLoading?: boolean;
}

// Priority badge colors
const priorityStyles: Record<TaskPriority, string> = {
  low: "bg-slate-100 text-slate-600",
  medium: "bg-blue-100 text-blue-700",
  high: "bg-orange-100 text-orange-700",
  urgent: "bg-red-100 text-red-700",
};

const priorityLabels: Record<TaskPriority, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
  urgent: "Urgent",
};

export function TaskCard({
  task,
  onComplete,
  onDelete,
  onEdit,
  isLoading = false,
}: TaskCardProps) {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const isCompleted = task.status === "completed";

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;
    return formatDate(dateString);
  };

  const formatDueDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return { text: `${Math.abs(diffDays)} days overdue`, isOverdue: true };
    if (diffDays === 0) return { text: "Due today", isOverdue: false };
    if (diffDays === 1) return { text: "Due tomorrow", isOverdue: false };
    if (diffDays < 7) return { text: `Due in ${diffDays} days`, isOverdue: false };
    return { text: `Due ${formatDate(dateString)}`, isOverdue: false };
  };

  const handleDelete = () => {
    if (showDeleteConfirm) {
      onDelete(task.id);
      setShowDeleteConfirm(false);
    } else {
      setShowDeleteConfirm(true);
      setTimeout(() => setShowDeleteConfirm(false), 3000);
    }
  };

  const dueInfo = task.due_date ? formatDueDate(task.due_date) : null;

  return (
    <div
      className={`
        group relative bg-white rounded-xl border-2
        transition-all duration-200 ease-out
        ${isCompleted
          ? "border-slate-100 bg-slate-50/50"
          : "border-slate-100 hover:border-slate-200 hover:shadow-lg hover:shadow-slate-200/50"
        }
        ${isLoading ? "animate-pulse pointer-events-none" : ""}
      `}
    >
      {/* Priority indicator bar */}
      {task.priority !== "medium" && !isCompleted && (
        <div
          className={`absolute top-0 left-0 w-1 h-full rounded-l-xl ${
            task.priority === "urgent"
              ? "bg-red-500"
              : task.priority === "high"
              ? "bg-orange-500"
              : "bg-slate-300"
          }`}
        />
      )}

      {/* Card Content */}
      <div className="p-5">
        <div className="flex items-start gap-4">
          {/* Completion checkbox */}
          <button
            onClick={() => onComplete(task.id, !isCompleted)}
            disabled={isLoading}
            className={`
              mt-0.5 w-6 h-6 rounded-full border-2 flex items-center justify-center
              flex-shrink-0 transition-all duration-200
              focus:outline-none focus:ring-2 focus:ring-offset-2
              ${isCompleted
                ? "bg-emerald-500 border-emerald-500 text-white focus:ring-emerald-300"
                : "border-slate-300 hover:border-blue-400 hover:bg-blue-50 focus:ring-blue-300"
              }
              disabled:opacity-50 disabled:cursor-not-allowed
            `}
            aria-label={isCompleted ? "Mark as pending" : "Mark as complete"}
          >
            {isCompleted && (
              <svg
                className="w-3.5 h-3.5"
                fill="currentColor"
                viewBox="0 0 20 20"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            )}
          </button>

          {/* Task content */}
          <div className="flex-1 min-w-0">
            {/* Title and Badges */}
            <div className="flex items-start gap-2 flex-wrap">
              <h3
                className={`
                  text-base font-semibold leading-tight
                  ${isCompleted ? "line-through text-slate-400" : "text-slate-800"}
                `}
              >
                {task.title}
              </h3>
              {/* Priority Badge */}
              <span
                className={`
                  inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium
                  ${priorityStyles[task.priority]}
                `}
              >
                {priorityLabels[task.priority]}
              </span>
              {/* Status Badge */}
              <span
                className={`
                  inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium
                  ${isCompleted
                    ? "bg-emerald-100 text-emerald-700"
                    : "bg-amber-100 text-amber-700"
                  }
                `}
              >
                {isCompleted ? "Completed" : "Pending"}
              </span>
              {/* Recurring Badge */}
              {task.is_recurring && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-700">
                  <svg
                    className="w-3 h-3 mr-1"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                    />
                  </svg>
                  {task.recurrence_pattern}
                </span>
              )}
            </div>

            {/* Description */}
            {task.description && (
              <p
                className={`
                  mt-2 text-sm leading-relaxed whitespace-pre-wrap
                  ${isCompleted ? "text-slate-400" : "text-slate-600"}
                `}
              >
                {task.description}
              </p>
            )}

            {/* Tags */}
            {task.tags && task.tags.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {task.tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-600"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            )}

            {/* Meta info */}
            <div className="mt-3 flex flex-wrap items-center gap-3 text-xs">
              {/* Due date */}
              {dueInfo && !isCompleted && (
                <span
                  className={`inline-flex items-center gap-1.5 font-medium ${
                    dueInfo.isOverdue ? "text-red-500" : "text-slate-500"
                  }`}
                >
                  <svg
                    className="w-3.5 h-3.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  {dueInfo.text}
                </span>
              )}
              <span className="inline-flex items-center gap-1.5 text-slate-400">
                <svg
                  className="w-3.5 h-3.5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                Created {formatRelativeTime(task.created_at)}
              </span>
              {task.completed_at && (
                <span className="inline-flex items-center gap-1.5 text-emerald-500">
                  <svg
                    className="w-3.5 h-3.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  Completed {formatRelativeTime(task.completed_at)}
                </span>
              )}
            </div>
          </div>

          {/* Actions - always visible with clear styling */}
          <div
            className={`
              flex items-center gap-2 flex-shrink-0
              ${isLoading ? "hidden" : ""}
            `}
          >
            {onEdit && (
              <button
                onClick={() => onEdit(task)}
                disabled={isLoading}
                className="
                  p-2.5 rounded-xl bg-blue-50 text-blue-600
                  hover:bg-blue-100 hover:text-blue-700
                  focus:outline-none focus:ring-2 focus:ring-blue-300 focus:ring-offset-1
                  transition-all duration-200 hover:scale-105
                  disabled:opacity-50 disabled:cursor-not-allowed
                  shadow-sm hover:shadow-md
                "
                aria-label="Edit task"
                title="Edit task"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
              </button>
            )}
            <button
              onClick={handleDelete}
              disabled={isLoading}
              className={`
                p-2.5 rounded-xl transition-all duration-200 hover:scale-105
                focus:outline-none focus:ring-2 focus:ring-offset-1
                disabled:opacity-50 disabled:cursor-not-allowed
                shadow-sm hover:shadow-md
                ${showDeleteConfirm
                  ? "text-white bg-red-500 hover:bg-red-600 focus:ring-red-300"
                  : "bg-red-50 text-red-500 hover:bg-red-100 hover:text-red-600 focus:ring-red-300"
                }
              `}
              aria-label={showDeleteConfirm ? "Confirm delete" : "Delete task"}
              title={showDeleteConfirm ? "Click again to confirm" : "Delete task"}
            >
              {showDeleteConfirm ? (
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              ) : (
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Delete confirmation tooltip */}
      {showDeleteConfirm && (
        <div
          className="
            absolute right-2 top-full mt-1 z-10
            px-3 py-1.5 bg-slate-800 text-white text-xs rounded-lg
            shadow-lg
          "
          role="tooltip"
        >
          Click again to delete
          <div className="absolute -top-1 right-4 w-2 h-2 bg-slate-800 rotate-45" />
        </div>
      )}
    </div>
  );
}
