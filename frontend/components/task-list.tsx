"use client";

/**
 * Task List Component
 *
 * Phase II: Professional task list with responsive grid, skeleton loaders,
 * and polished empty state.
 */

import { TaskCard } from "./task-card";
import type { Task } from "@/lib/api-client";

interface TaskListProps {
  tasks: Task[];
  onComplete: (taskId: string, completed: boolean) => void;
  onDelete: (taskId: string) => void;
  onEdit?: (task: Task) => void;
  loadingTaskId?: string;
  isLoading?: boolean;
}

// Skeleton card for loading state
function TaskSkeleton() {
  return (
    <div className="bg-white rounded-xl border-2 border-slate-100 p-5 animate-pulse">
      <div className="flex items-start gap-4">
        {/* Checkbox skeleton */}
        <div className="w-6 h-6 rounded-full bg-slate-200 flex-shrink-0" />

        {/* Content skeleton */}
        <div className="flex-1 space-y-3">
          <div className="flex items-center gap-2">
            <div className="h-5 bg-slate-200 rounded-lg w-3/4" />
            <div className="h-5 bg-slate-200 rounded-full w-16" />
          </div>
          <div className="h-4 bg-slate-200 rounded w-full" />
          <div className="h-4 bg-slate-200 rounded w-2/3" />
          <div className="flex gap-3 pt-1">
            <div className="h-3 bg-slate-200 rounded w-24" />
          </div>
        </div>
      </div>
    </div>
  );
}

export function TaskList({
  tasks,
  onComplete,
  onDelete,
  onEdit,
  loadingTaskId,
  isLoading = false,
}: TaskListProps) {
  // Loading state with skeletons
  if (isLoading) {
    return (
      <div className="space-y-4">
        <TaskSkeleton />
        <TaskSkeleton />
        <TaskSkeleton />
      </div>
    );
  }

  // Empty state (T055) - Enhanced with gradient and better visuals
  if (tasks.length === 0) {
    return (
      <div className="relative overflow-hidden bg-gradient-to-br from-slate-50 to-blue-50 rounded-2xl border border-slate-100 text-center py-16 px-6">
        {/* Background decoration */}
        <div className="absolute top-0 right-0 w-40 h-40 bg-blue-100 rounded-full blur-3xl opacity-40" />
        <div className="absolute bottom-0 left-0 w-32 h-32 bg-purple-100 rounded-full blur-3xl opacity-40" />

        {/* Illustration */}
        <div className="relative mx-auto w-28 h-28 mb-6">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-200 to-purple-200 rounded-full animate-pulse" />
          <div className="absolute inset-2 bg-white rounded-full flex items-center justify-center shadow-inner">
            <svg
              className="w-12 h-12 text-blue-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
              />
            </svg>
          </div>
        </div>

        <h3 className="relative text-xl font-bold text-slate-800">
          No tasks yet
        </h3>
        <p className="relative mt-2 text-sm text-slate-500 max-w-sm mx-auto leading-relaxed">
          Start being productive! Add your first task using the button above, or ask the AI assistant to help you get organized.
        </p>

        {/* Action hint */}
        <div className="relative mt-6 inline-flex items-center gap-2 text-sm text-purple-600 font-medium">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Try saying &quot;Add a task to buy groceries&quot; in AI Chat
        </div>

        {/* Decorative dots */}
        <div className="relative mt-8 flex justify-center gap-2">
          <div className="w-2 h-2 rounded-full bg-blue-300 animate-bounce" style={{ animationDelay: "0ms" }} />
          <div className="w-2 h-2 rounded-full bg-purple-300 animate-bounce" style={{ animationDelay: "150ms" }} />
          <div className="w-2 h-2 rounded-full bg-pink-300 animate-bounce" style={{ animationDelay: "300ms" }} />
        </div>
      </div>
    );
  }

  // Sort tasks: pending first, then by creation date (newest first)
  const sortedTasks = [...tasks].sort((a, b) => {
    if (a.status !== b.status) {
      return a.status === "pending" ? -1 : 1;
    }
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  // Count stats
  const pendingCount = tasks.filter((t) => t.status === "pending").length;
  const completedCount = tasks.filter((t) => t.status === "completed").length;

  return (
    <div className="space-y-4">
      {/* Task count header */}
      <div className="flex items-center justify-between text-sm text-slate-500 px-1">
        <span>
          Showing <span className="font-semibold text-slate-700">{tasks.length}</span> task{tasks.length !== 1 ? "s" : ""}
        </span>
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-amber-400" />
            {pendingCount} pending
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            {completedCount} done
          </span>
        </div>
      </div>

      {/* Task list */}
      <div className="space-y-3">
        {sortedTasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onComplete={onComplete}
            onDelete={onDelete}
            onEdit={onEdit}
            isLoading={loadingTaskId === task.id}
          />
        ))}
      </div>
    </div>
  );
}
