"use client";

/**
 * Task Form Component
 *
 * Phase II: Professional form for creating and editing tasks.
 * Features: Priority, due date, tags, better focus states, accessibility.
 */

import { useState, useEffect, useRef } from "react";
import { z } from "zod";
import type { Task, CreateTaskData, UpdateTaskData, TaskPriority } from "@/lib/api-client";

// Validation schema (T061 - matches backend constraints)
const taskSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(200, "Title must be 200 characters or less"),
  description: z
    .string()
    .max(1000, "Description must be 1000 characters or less")
    .optional()
    .transform((val) => val || undefined),
  priority: z.enum(["low", "medium", "high", "urgent"]).default("medium"),
  due_date: z.string().optional(),
  tags: z.array(z.string()).default([]),
});

interface TaskFormProps {
  onSubmit: (data: CreateTaskData | UpdateTaskData) => Promise<void>;
  editingTask?: Task;
  onCancel?: () => void;
  error?: string;
}

const priorityOptions: { value: TaskPriority; label: string; color: string }[] = [
  { value: "low", label: "Low", color: "text-slate-600" },
  { value: "medium", label: "Medium", color: "text-blue-600" },
  { value: "high", label: "High", color: "text-orange-600" },
  { value: "urgent", label: "Urgent", color: "text-red-600" },
];

export function TaskForm({
  onSubmit,
  editingTask,
  onCancel,
  error: externalError,
}: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TaskPriority>("medium");
  const [dueDate, setDueDate] = useState("");
  const [tagInput, setTagInput] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const titleInputRef = useRef<HTMLInputElement>(null);

  const isEditing = !!editingTask;

  // Populate form when editing
  useEffect(() => {
    if (editingTask) {
      setTitle(editingTask.title);
      setDescription(editingTask.description || "");
      setPriority(editingTask.priority || "medium");
      setDueDate(editingTask.due_date ? editingTask.due_date.split("T")[0] : "");
      setTags(editingTask.tags || []);
    } else {
      setTitle("");
      setDescription("");
      setPriority("medium");
      setDueDate("");
      setTags([]);
    }
  }, [editingTask]);

  // Focus title input on mount
  useEffect(() => {
    if (titleInputRef.current) {
      titleInputRef.current.focus();
    }
  }, []);

  const handleAddTag = () => {
    const trimmedTag = tagInput.trim().toLowerCase();
    if (trimmedTag && !tags.includes(trimmedTag) && tags.length < 10) {
      setTags([...tags, trimmedTag]);
      setTagInput("");
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((tag) => tag !== tagToRemove));
  };

  const handleTagKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddTag();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    // Validate
    const data = {
      title,
      description: description || undefined,
      priority,
      due_date: dueDate ? new Date(dueDate).toISOString() : undefined,
      tags,
    };
    const result = taskSchema.safeParse(data);

    if (!result.success) {
      const fieldErrors: Record<string, string> = {};
      result.error.errors.forEach((err) => {
        if (err.path[0]) {
          fieldErrors[err.path[0] as string] = err.message;
        }
      });
      setErrors(fieldErrors);
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(result.data as CreateTaskData);
      // Clear form on success (only for create, not edit)
      if (!isEditing) {
        setTitle("");
        setDescription("");
        setPriority("medium");
        setDueDate("");
        setTags([]);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const titleCharCount = title.length;
  const descCharCount = description.length;
  const titleNearLimit = titleCharCount > 180;
  const descNearLimit = descCharCount > 900;

  // Get today's date for min attribute
  const today = new Date().toISOString().split("T")[0];

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Title Field */}
      <div className="space-y-1.5">
        <label
          htmlFor="title"
          className="block text-sm font-semibold text-slate-700"
        >
          Title <span className="text-red-500">*</span>
        </label>
        <input
          ref={titleInputRef}
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className={`
            block w-full rounded-lg border-2 px-4 py-2.5 text-slate-900
            placeholder:text-slate-400 transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-offset-1
            disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed
            ${errors.title
              ? "border-red-300 focus:border-red-500 focus:ring-red-200"
              : "border-slate-200 hover:border-slate-300 focus:border-blue-500 focus:ring-blue-200"
            }
          `}
          placeholder="What needs to be done?"
          disabled={isSubmitting}
          aria-describedby={errors.title ? "title-error" : "title-count"}
          aria-invalid={!!errors.title}
          maxLength={200}
        />
        <div className="flex justify-between items-center">
          {errors.title ? (
            <p id="title-error" className="text-sm text-red-600 font-medium" role="alert">
              {errors.title}
            </p>
          ) : (
            <span className="text-xs text-slate-400">Required field</span>
          )}
          <span
            id="title-count"
            className={`text-xs font-medium ${
              titleNearLimit ? "text-amber-600" : "text-slate-400"
            }`}
          >
            {titleCharCount}/200
          </span>
        </div>
      </div>

      {/* Description Field */}
      <div className="space-y-1.5">
        <label
          htmlFor="description"
          className="block text-sm font-semibold text-slate-700"
        >
          Description <span className="text-slate-400 font-normal">(optional)</span>
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
          className={`
            block w-full rounded-lg border-2 px-4 py-2.5 text-slate-900
            placeholder:text-slate-400 transition-all duration-200 resize-none
            focus:outline-none focus:ring-2 focus:ring-offset-1
            disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed
            ${errors.description
              ? "border-red-300 focus:border-red-500 focus:ring-red-200"
              : "border-slate-200 hover:border-slate-300 focus:border-blue-500 focus:ring-blue-200"
            }
          `}
          placeholder="Add more details about this task..."
          disabled={isSubmitting}
          aria-describedby={errors.description ? "desc-error" : "desc-count"}
          aria-invalid={!!errors.description}
          maxLength={1000}
        />
        <div className="flex justify-between items-center">
          {errors.description ? (
            <p id="desc-error" className="text-sm text-red-600 font-medium" role="alert">
              {errors.description}
            </p>
          ) : (
            <span className="text-xs text-slate-400">Add context or notes</span>
          )}
          <span
            id="desc-count"
            className={`text-xs font-medium ${
              descNearLimit ? "text-amber-600" : "text-slate-400"
            }`}
          >
            {descCharCount}/1000
          </span>
        </div>
      </div>

      {/* Priority and Due Date Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Priority Field */}
        <div className="space-y-1.5">
          <label
            htmlFor="priority"
            className="block text-sm font-semibold text-slate-700"
          >
            Priority
          </label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as TaskPriority)}
            disabled={isSubmitting}
            className="
              block w-full rounded-lg border-2 border-slate-200 px-4 py-2.5
              text-slate-900 bg-white
              hover:border-slate-300 focus:border-blue-500
              focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-blue-200
              disabled:bg-slate-50 disabled:cursor-not-allowed
              transition-all duration-200
            "
          >
            {priorityOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Due Date Field */}
        <div className="space-y-1.5">
          <label
            htmlFor="dueDate"
            className="block text-sm font-semibold text-slate-700"
          >
            Due Date <span className="text-slate-400 font-normal">(optional)</span>
          </label>
          <input
            id="dueDate"
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            min={today}
            disabled={isSubmitting}
            className="
              block w-full rounded-lg border-2 border-slate-200 px-4 py-2.5
              text-slate-900 bg-white
              hover:border-slate-300 focus:border-blue-500
              focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-blue-200
              disabled:bg-slate-50 disabled:cursor-not-allowed
              transition-all duration-200
            "
          />
        </div>
      </div>

      {/* Tags Field */}
      <div className="space-y-1.5">
        <label
          htmlFor="tagInput"
          className="block text-sm font-semibold text-slate-700"
        >
          Tags <span className="text-slate-400 font-normal">(optional, max 10)</span>
        </label>
        <div className="flex gap-2">
          <input
            id="tagInput"
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={handleTagKeyDown}
            disabled={isSubmitting || tags.length >= 10}
            placeholder="Add a tag and press Enter"
            className="
              flex-1 rounded-lg border-2 border-slate-200 px-4 py-2.5
              text-slate-900 placeholder:text-slate-400
              hover:border-slate-300 focus:border-blue-500
              focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-blue-200
              disabled:bg-slate-50 disabled:cursor-not-allowed
              transition-all duration-200
            "
          />
          <button
            type="button"
            onClick={handleAddTag}
            disabled={isSubmitting || !tagInput.trim() || tags.length >= 10}
            className="
              px-4 py-2.5 rounded-lg border-2 border-slate-200
              text-slate-600 font-medium
              hover:bg-slate-50 hover:border-slate-300
              focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-slate-300
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-200
            "
          >
            Add
          </button>
        </div>
        {/* Tags display */}
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {tags.map((tag) => (
              <span
                key={tag}
                className="
                  inline-flex items-center gap-1.5 px-3 py-1
                  bg-slate-100 text-slate-700 text-sm font-medium
                  rounded-full
                "
              >
                #{tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  disabled={isSubmitting}
                  className="
                    w-4 h-4 rounded-full flex items-center justify-center
                    text-slate-400 hover:text-slate-600 hover:bg-slate-200
                    transition-colors
                  "
                  aria-label={`Remove tag ${tag}`}
                >
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </span>
            ))}
          </div>
        )}
        <p className="text-xs text-slate-400">
          {tags.length}/10 tags added
        </p>
      </div>

      {/* External Error (T064) */}
      {externalError && (
        <div
          className="rounded-lg bg-red-50 border border-red-200 p-4 flex items-start gap-3"
          role="alert"
        >
          <svg
            className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5"
            fill="currentColor"
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
          <p className="text-sm text-red-700 font-medium">{externalError}</p>
        </div>
      )}

      {/* Buttons */}
      <div className="flex justify-end gap-3 pt-2">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
            className="
              px-5 py-2.5 text-sm font-semibold text-slate-700
              bg-white border-2 border-slate-200 rounded-lg
              hover:bg-slate-50 hover:border-slate-300
              focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-slate-300
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-200
            "
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={isSubmitting}
          className="
            px-5 py-2.5 text-sm font-semibold text-white
            bg-blue-600 border-2 border-blue-600 rounded-lg
            hover:bg-blue-700 hover:border-blue-700
            focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-blue-300
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-all duration-200
            flex items-center gap-2
          "
        >
          {isSubmitting && (
            <svg
              className="animate-spin h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                className="opacity-25"
                cx="12" cy="12" r="10"
                stroke="currentColor" strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          )}
          {isSubmitting
            ? "Saving..."
            : isEditing
            ? "Update Task"
            : "Add Task"}
        </button>
      </div>
    </form>
  );
}
