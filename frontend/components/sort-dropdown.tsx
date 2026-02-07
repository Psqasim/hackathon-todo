"use client";

/**
 * Sort Dropdown Component
 *
 * Provides sorting functionality for tasks with persistent preferences.
 * Phase 5: Added for US5 - Real-Time Search and Filter
 */

import { useState, useEffect } from "react";

export type SortOption = "due_date" | "priority" | "created_at" | "title";
export type SortOrder = "asc" | "desc";

interface SortDropdownProps {
  onSortChange: (sortBy: SortOption, sortOrder: SortOrder) => void;
}

const SORT_OPTIONS: { value: SortOption; label: string; icon: React.ReactNode }[] = [
  {
    value: "due_date",
    label: "Due Date",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
  },
  {
    value: "priority",
    label: "Priority",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
      </svg>
    ),
  },
  {
    value: "created_at",
    label: "Created Date",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  {
    value: "title",
    label: "Title",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
      </svg>
    ),
  },
];

export function SortDropdown({ onSortChange }: SortDropdownProps) {
  // Load saved preferences from localStorage
  const [sortBy, setSortBy] = useState<SortOption>("created_at");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");
  const [isOpen, setIsOpen] = useState(false);

  // Load preferences on mount
  useEffect(() => {
    const savedSortBy = localStorage.getItem("taskSortBy") as SortOption | null;
    const savedSortOrder = localStorage.getItem("taskSortOrder") as SortOrder | null;

    if (savedSortBy) setSortBy(savedSortBy);
    if (savedSortOrder) setSortOrder(savedSortOrder);
  }, []);

  // Notify parent and save preferences when sort changes
  useEffect(() => {
    onSortChange(sortBy, sortOrder);
    localStorage.setItem("taskSortBy", sortBy);
    localStorage.setItem("taskSortOrder", sortOrder);
  }, [sortBy, sortOrder, onSortChange]);

  const handleSortByChange = (value: SortOption) => {
    setSortBy(value);
    setIsOpen(false);
  };

  const toggleSortOrder = () => {
    setSortOrder(sortOrder === "asc" ? "desc" : "asc");
  };

  const currentOption = SORT_OPTIONS.find((opt) => opt.value === sortBy);

  return (
    <div className="flex items-center gap-2">
      {/* Sort By Dropdown */}
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-white border-2 border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:border-blue-300 hover:bg-slate-50 transition-all duration-200 shadow-sm hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500/20"
        >
          <svg className="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
          </svg>
          <span>Sort by:</span>
          <span className="flex items-center gap-1.5 text-blue-600 font-semibold">
            {currentOption?.icon}
            {currentOption?.label}
          </span>
          <svg
            className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* Dropdown Menu */}
        {isOpen && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 z-10"
              onClick={() => setIsOpen(false)}
            />

            {/* Menu */}
            <div className="absolute left-0 mt-2 w-56 bg-white border-2 border-slate-200 rounded-xl shadow-xl z-20 overflow-hidden">
              {SORT_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  onClick={() => handleSortByChange(option.value)}
                  className={`
                    w-full flex items-center gap-3 px-4 py-3 text-sm font-medium transition-colors
                    ${sortBy === option.value
                      ? "bg-blue-50 text-blue-600"
                      : "text-slate-700 hover:bg-slate-50"
                    }
                  `}
                >
                  <span className={sortBy === option.value ? "text-blue-500" : "text-slate-400"}>
                    {option.icon}
                  </span>
                  <span className="flex-1 text-left">{option.label}</span>
                  {sortBy === option.value && (
                    <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </button>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Sort Order Toggle */}
      <button
        onClick={toggleSortOrder}
        className="inline-flex items-center justify-center w-10 h-10 bg-white border-2 border-slate-200 rounded-xl text-slate-600 hover:border-blue-300 hover:bg-slate-50 transition-all duration-200 shadow-sm hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500/20"
        title={sortOrder === "asc" ? "Ascending" : "Descending"}
      >
        {sortOrder === "asc" ? (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
          </svg>
        ) : (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        )}
      </button>
    </div>
  );
}
