"use client";

/**
 * Dashboard Page
 *
 * Phase II: Professional task management dashboard with welcome header,
 * task statistics, and polished UI.
 */

import { useState, useEffect, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/header";
import { TaskList } from "@/components/task-list";
import { TaskForm } from "@/components/task-form";
import { Loading } from "@/components/loading";
import {
  isAuthenticated,
  getStoredUser,
  getCurrentUser,
  type User,
} from "@/lib/auth-client";
import {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
  completeTask,
  type Task,
  type CreateTaskData,
  type UpdateTaskData,
} from "@/lib/api-client";

type FilterStatus = "all" | "pending" | "completed";

// Custom hook for debounced value
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}

// Helper to get time-based greeting
function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

// Stat card component with enhanced design
function StatCard({
  label,
  value,
  icon,
  color,
  suffix,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
  color: "blue" | "amber" | "emerald" | "purple";
  suffix?: string;
}) {
  const colorStyles = {
    blue: {
      bg: "bg-gradient-to-br from-blue-500 to-blue-600",
      light: "bg-blue-400/20",
      text: "text-white",
    },
    amber: {
      bg: "bg-gradient-to-br from-amber-500 to-orange-500",
      light: "bg-amber-400/20",
      text: "text-white",
    },
    emerald: {
      bg: "bg-gradient-to-br from-emerald-500 to-teal-500",
      light: "bg-emerald-400/20",
      text: "text-white",
    },
    purple: {
      bg: "bg-gradient-to-br from-purple-500 to-pink-500",
      light: "bg-purple-400/20",
      text: "text-white",
    },
  };

  const style = colorStyles[color];

  return (
    <div className={`relative overflow-hidden rounded-2xl ${style.bg} p-5 shadow-lg shadow-${color}-500/20 hover:shadow-xl hover:shadow-${color}-500/30 transition-all duration-300 hover:scale-[1.02]`}>
      {/* Background decoration */}
      <div className="absolute -right-4 -top-4 w-24 h-24 rounded-full bg-white/10 blur-2xl" />
      <div className="absolute -right-2 -bottom-2 w-16 h-16 rounded-full bg-white/5" />

      <div className="relative flex items-center justify-between">
        <div>
          <p className="text-3xl font-bold text-white">
            {value}{suffix && <span className="text-lg ml-0.5">{suffix}</span>}
          </p>
          <p className="text-sm font-medium text-white/80 mt-1">{label}</p>
        </div>
        <div className={`p-3 rounded-xl ${style.light}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadingTaskId, setLoadingTaskId] = useState<string>();
  const [error, setError] = useState<string>("");
  const [formError, setFormError] = useState<string>("");
  const [editingTask, setEditingTask] = useState<Task>();
  const [showForm, setShowForm] = useState(false);
  const [filter, setFilter] = useState<FilterStatus>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearch = useDebounce(searchQuery, 300);

  // Filter tasks based on search query
  const filteredTasks = useMemo(() => {
    if (!debouncedSearch.trim()) return tasks;
    const query = debouncedSearch.toLowerCase();
    return tasks.filter(
      (task) =>
        task.title.toLowerCase().includes(query) ||
        (task.description && task.description.toLowerCase().includes(query))
    );
  }, [tasks, debouncedSearch]);

  // Calculate stats
  const stats = useMemo(() => {
    const total = tasks.length;
    const pending = tasks.filter((t) => t.status === "pending").length;
    const completed = tasks.filter((t) => t.status === "completed").length;
    const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0;
    return { total, pending, completed, completionRate };
  }, [tasks]);

  // Check authentication and load user
  useEffect(() => {
    const checkAuth = async () => {
      if (!isAuthenticated()) {
        router.push("/signin");
        return;
      }

      // Try to get stored user first
      let currentUser = getStoredUser();

      // Validate with API
      const validatedUser = await getCurrentUser();
      if (!validatedUser) {
        router.push("/signin");
        return;
      }

      currentUser = validatedUser;
      setUser(currentUser);
    };

    checkAuth();
  }, [router]);

  // Load tasks when user is available
  const loadTasks = useCallback(async () => {
    if (!user) return;

    setIsLoading(true);
    setError("");

    try {
      const statusFilter = filter === "all" ? undefined : filter;
      const response = await getTasks(user.id, statusFilter);
      setTasks(response.tasks);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load tasks");
      }
    } finally {
      setIsLoading(false);
    }
  }, [user, filter]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  // Task handlers
  const handleCreateTask = async (data: CreateTaskData | UpdateTaskData) => {
    if (!user) return;
    setFormError("");

    try {
      if (editingTask) {
        // Update existing task
        const response = await updateTask(user.id, editingTask.id, data as UpdateTaskData);
        setTasks((prev) =>
          prev.map((t) => (t.id === editingTask.id ? response.task : t))
        );
        setEditingTask(undefined);
      } else {
        // Create new task (T063)
        const response = await createTask(user.id, data as CreateTaskData);
        setTasks((prev) => [response.task, ...prev]);
        setShowForm(false);
      }
    } catch (err) {
      if (err instanceof Error) {
        setFormError(err.message);
      } else {
        setFormError("Failed to save task");
      }
      throw err; // Re-throw to prevent form clearing
    }
  };

  const handleComplete = async (taskId: string, completed: boolean) => {
    if (!user) return;
    setLoadingTaskId(taskId);

    try {
      const response = await completeTask(user.id, taskId, completed);
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? response.task : t))
      );
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      }
    } finally {
      setLoadingTaskId(undefined);
    }
  };

  const handleDelete = async (taskId: string) => {
    if (!user) return;
    setLoadingTaskId(taskId);

    try {
      await deleteTask(user.id, taskId);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      }
    } finally {
      setLoadingTaskId(undefined);
    }
  };

  const handleEdit = (task: Task) => {
    setEditingTask(task);
    setShowForm(true);
    setFormError("");
  };

  const handleCancelEdit = () => {
    setEditingTask(undefined);
    setShowForm(false);
    setFormError("");
  };

  // Show loading while checking auth
  if (!user) {
    return <Loading message="Loading..." />;
  }

  // Get first name for greeting
  const firstName = user.name?.split(" ")[0] || user.name || "there";

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
      <Header user={user} />

      <main className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Welcome Header */}
        <div className="mb-8 relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-800 via-slate-700 to-slate-800 p-6 sm:p-8 shadow-xl">
          {/* Background decoration */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-purple-500/10 rounded-full blur-3xl" />

          <div className="relative">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">
                {new Date().getHours() < 12 ? "🌅" : new Date().getHours() < 17 ? "☀️" : "🌙"}
              </span>
              <span className="text-sm text-slate-400 font-medium">
                {new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}
              </span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">
              {getGreeting()}, <span className="text-blue-400">{firstName}</span>!
            </h1>
            <p className="text-slate-300 text-lg">
              {stats.pending > 0
                ? `You have ${stats.pending} task${stats.pending !== 1 ? "s" : ""} waiting for you.`
                : stats.completed > 0
                ? "Amazing! You've completed all your tasks. 🎉"
                : "Ready to be productive? Add your first task!"}
            </p>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard
            label="Total Tasks"
            value={stats.total}
            color="blue"
            icon={
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            }
          />
          <StatCard
            label="In Progress"
            value={stats.pending}
            color="amber"
            icon={
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
          />
          <StatCard
            label="Completed"
            value={stats.completed}
            color="emerald"
            icon={
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
          />
          <StatCard
            label="Success Rate"
            value={stats.completionRate}
            color="purple"
            suffix="%"
            icon={
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            }
          />
        </div>

        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl opacity-0 group-focus-within:opacity-100 blur transition-opacity duration-300" />
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search tasks by title or description..."
                className="block w-full pl-12 pr-12 py-4 bg-white border-2 border-slate-100 rounded-xl text-slate-800 placeholder:text-slate-400 focus:border-blue-400 focus:ring-0 focus:outline-none transition-all duration-200 shadow-sm hover:shadow-md"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-red-500 transition-colors"
                >
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          </div>
          {debouncedSearch && (
            <p className="mt-3 text-sm text-slate-500 flex items-center gap-2">
              <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-600 text-xs font-bold">
                {filteredTasks.length}
              </span>
              {filteredTasks.length === 1 ? "result" : "results"} found for &ldquo;{debouncedSearch}&rdquo;
            </p>
          )}
        </div>

        {/* Filter Tabs */}
        <div className="mb-6">
          <nav
            className="inline-flex gap-1 p-1.5 bg-slate-100/80 backdrop-blur-sm rounded-2xl shadow-inner"
            aria-label="Task filter tabs"
          >
            {(["all", "pending", "completed"] as FilterStatus[]).map((status) => {
              const isActive = filter === status;
              const icons = {
                all: (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                  </svg>
                ),
                pending: (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                ),
                completed: (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                ),
              };
              return (
                <button
                  key={status}
                  onClick={() => setFilter(status)}
                  className={`
                    relative flex items-center gap-2 px-5 py-2.5 text-sm font-semibold rounded-xl transition-all duration-300
                    ${isActive
                      ? "bg-white text-slate-800 shadow-lg shadow-slate-200/50"
                      : "text-slate-500 hover:text-slate-700 hover:bg-white/50"
                    }
                  `}
                  aria-current={isActive ? "page" : undefined}
                >
                  <span className={isActive ? "text-blue-500" : ""}>{icons[status]}</span>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                  {status === "pending" && stats.pending > 0 && (
                    <span className={`
                      px-2 py-0.5 text-xs font-bold rounded-full transition-colors
                      ${isActive ? "bg-amber-500 text-white" : "bg-amber-100 text-amber-700"}
                    `}>
                      {stats.pending}
                    </span>
                  )}
                  {status === "completed" && stats.completed > 0 && (
                    <span className={`
                      px-2 py-0.5 text-xs font-bold rounded-full transition-colors
                      ${isActive ? "bg-emerald-500 text-white" : "bg-emerald-100 text-emerald-700"}
                    `}>
                      {stats.completed}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Error Message */}
        {error && (
          <div
            className="mb-6 rounded-xl bg-red-50 border border-red-200 p-4 flex items-center gap-3"
            role="alert"
          >
            <svg className="w-5 h-5 text-red-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <p className="text-sm text-red-700 font-medium">{error}</p>
            <button
              onClick={() => setError("")}
              className="ml-auto text-red-400 hover:text-red-600"
              aria-label="Dismiss error"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        )}

        {/* Add Task Button / Form */}
        <div className="mb-6">
          {showForm ? (
            <div className="relative overflow-hidden bg-white rounded-2xl border border-slate-200 shadow-lg p-6">
              {/* Decorative gradient */}
              <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500" />
              <h3 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
                {editingTask ? (
                  <>
                    <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    Edit Task
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Create New Task
                  </>
                )}
              </h3>
              <TaskForm
                onSubmit={handleCreateTask}
                editingTask={editingTask}
                onCancel={handleCancelEdit}
                error={formError}
              />
            </div>
          ) : (
            <button
              onClick={() => setShowForm(true)}
              className="
                group relative w-full py-5 px-6 overflow-hidden
                bg-gradient-to-r from-blue-500 via-blue-600 to-purple-600
                rounded-2xl text-white font-semibold
                hover:from-blue-600 hover:via-blue-700 hover:to-purple-700
                focus:outline-none focus:ring-4 focus:ring-blue-300/50 focus:ring-offset-2
                transition-all duration-300 shadow-lg shadow-blue-500/25
                hover:shadow-xl hover:shadow-blue-500/30 hover:scale-[1.02]
                flex items-center justify-center gap-3
              "
            >
              {/* Animated shine effect */}
              <div className="absolute inset-0 translate-x-[-100%] group-hover:translate-x-[100%] bg-gradient-to-r from-transparent via-white/20 to-transparent transition-transform duration-700" />
              <svg className="w-6 h-6 relative" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span className="relative text-lg">Add New Task</span>
            </button>
          )}
        </div>

        {/* Task List */}
        <TaskList
          tasks={filteredTasks}
          onComplete={handleComplete}
          onDelete={handleDelete}
          onEdit={handleEdit}
          loadingTaskId={loadingTaskId}
          isLoading={isLoading}
        />
      </main>
    </div>
  );
}
