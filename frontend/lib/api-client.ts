/**
 * API Client for Todo Application
 *
 * Phase II: Typed API client with JWT attachment for task operations.
 * Phase II Enhancement: Added priority, due_date, tags, recurring fields.
 */

import { getToken, clearAuth } from "./auth-client";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types
export type TaskPriority = "low" | "medium" | "high" | "urgent";
export type RecurrencePattern = "daily" | "weekly" | "monthly" | "yearly";

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: "pending" | "completed";
  priority: TaskPriority;
  due_date: string | null;
  tags: string[];
  is_recurring: boolean;
  recurrence_pattern: RecurrencePattern | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface CreateTaskData {
  title: string;
  description?: string;
  priority?: TaskPriority;
  due_date?: string;
  tags?: string[];
  is_recurring?: boolean;
  recurrence_pattern?: RecurrencePattern;
}

export interface UpdateTaskData {
  title?: string;
  description?: string;
  priority?: TaskPriority;
  due_date?: string;
  tags?: string[];
  is_recurring?: boolean;
  recurrence_pattern?: RecurrencePattern;
}

export interface TaskListResponse {
  tasks: Task[];
}

export interface SingleTaskResponse {
  task: Task;
}

export interface DeleteTaskResponse {
  deleted: boolean;
  task_id: string;
}

export interface TaskFilters {
  status?: "pending" | "completed";
  priority?: TaskPriority;
  sort?: "created_at" | "due_date" | "priority" | "title";
  order?: "asc" | "desc";
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Make an authenticated API request
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // Handle session expiration (T045)
  if (response.status === 401) {
    clearAuth();
    if (typeof window !== "undefined") {
      window.location.href = "/signin";
    }
    throw new ApiError("Session expired", 401, "Please sign in again");
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.detail || `Request failed with status ${response.status}`,
      response.status,
      errorData.detail
    );
  }

  return response.json() as Promise<T>;
}

// ============================================================================
// Task API Functions
// ============================================================================

/**
 * Get all tasks for a user with optional filters
 */
export async function getTasks(
  userId: string,
  status?: "pending" | "completed",
  filters?: TaskFilters
): Promise<TaskListResponse> {
  const params = new URLSearchParams();

  if (status) {
    params.append("status", status);
  }
  if (filters?.priority) {
    params.append("priority", filters.priority);
  }
  if (filters?.sort) {
    params.append("sort", filters.sort);
  }
  if (filters?.order) {
    params.append("order", filters.order);
  }

  const queryString = params.toString();
  const endpoint = `/api/users/${userId}/tasks${queryString ? `?${queryString}` : ""}`;

  return apiRequest<TaskListResponse>(endpoint);
}

/**
 * Get a single task
 */
export async function getTask(
  userId: string,
  taskId: string
): Promise<SingleTaskResponse> {
  return apiRequest<SingleTaskResponse>(`/api/users/${userId}/tasks/${taskId}`);
}

/**
 * Create a new task
 */
export async function createTask(
  userId: string,
  data: CreateTaskData
): Promise<SingleTaskResponse> {
  return apiRequest<SingleTaskResponse>(`/api/users/${userId}/tasks`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * Update a task
 */
export async function updateTask(
  userId: string,
  taskId: string,
  data: UpdateTaskData
): Promise<SingleTaskResponse> {
  return apiRequest<SingleTaskResponse>(`/api/users/${userId}/tasks/${taskId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/**
 * Delete a task
 */
export async function deleteTask(
  userId: string,
  taskId: string
): Promise<DeleteTaskResponse> {
  return apiRequest<DeleteTaskResponse>(`/api/users/${userId}/tasks/${taskId}`, {
    method: "DELETE",
  });
}

/**
 * Toggle task completion
 */
export async function completeTask(
  userId: string,
  taskId: string,
  completed: boolean
): Promise<SingleTaskResponse> {
  return apiRequest<SingleTaskResponse>(
    `/api/users/${userId}/tasks/${taskId}/complete`,
    {
      method: "PATCH",
      body: JSON.stringify({ completed }),
    }
  );
}
