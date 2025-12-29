-- Migration: Add new task fields (priority, due_date, tags, is_recurring, recurrence_pattern)

-- Add priority column with default 'medium'
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'medium';

-- Add due_date column
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date TIMESTAMP WITH TIME ZONE;

-- Add tags column as JSON array
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS tags JSON DEFAULT '[]';

-- Add is_recurring column with default false
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT FALSE;

-- Add recurrence_pattern column
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_pattern VARCHAR(20);

-- Update any NULL priority values to 'medium'
UPDATE tasks SET priority = 'medium' WHERE priority IS NULL;

-- Update any NULL tags values to empty array
UPDATE tasks SET tags = '[]' WHERE tags IS NULL;

-- Update any NULL is_recurring values to false
UPDATE tasks SET is_recurring = FALSE WHERE is_recurring IS NULL;
