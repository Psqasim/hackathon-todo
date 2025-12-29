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

  // Empty state (T055)
  if (tasks.length === 0) {
    return (
      <div className="text-center py-16 px-6">
        {/* Illustration */}
        <div className="relative mx-auto w-24 h-24 mb-6">
          <div className="absolute inset-0 bg-blue-100 rounded-full opacity-50" />
          <div className="absolute inset-2 bg-blue-50 rounded-full flex items-center justify-center">
            <svg
              className="w-10 h-10 text-blue-500"
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

        <h3 className="text-lg font-semibold text-slate-800">
          No tasks yet
        </h3>
        <p className="mt-2 text-sm text-slate-500 max-w-sm mx-auto">
          Start being productive! Add your first task using the form above.
        </p>

        {/* Decorative elements */}
        <div className="mt-8 flex justify-center gap-2">
          <div className="w-2 h-2 rounded-full bg-blue-200" />
          <div className="w-2 h-2 rounded-full bg-blue-300" />
          <div className="w-2 h-2 rounded-full bg-blue-400" />
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
