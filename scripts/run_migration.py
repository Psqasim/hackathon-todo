"""
Run database migration to add new task fields.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import psycopg2

def run_migration():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return False

    print(f"Connecting to database...")

    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()

        print("Adding new columns to tasks table...")

        # Add priority column
        cursor.execute("""
            ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'medium'
        """)
        print("  - Added priority column")

        # Add due_date column
        cursor.execute("""
            ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date TIMESTAMP WITH TIME ZONE
        """)
        print("  - Added due_date column")

        # Add tags column
        cursor.execute("""
            ALTER TABLE tasks ADD COLUMN IF NOT EXISTS tags JSON DEFAULT '[]'
        """)
        print("  - Added tags column")

        # Add is_recurring column
        cursor.execute("""
            ALTER TABLE tasks ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT FALSE
        """)
        print("  - Added is_recurring column")

        # Add recurrence_pattern column
        cursor.execute("""
            ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_pattern VARCHAR(20)
        """)
        print("  - Added recurrence_pattern column")

        # Update NULL values
        print("Updating existing rows with default values...")
        cursor.execute("UPDATE tasks SET priority = 'medium' WHERE priority IS NULL")
        cursor.execute("UPDATE tasks SET tags = '[]' WHERE tags IS NULL")
        cursor.execute("UPDATE tasks SET is_recurring = FALSE WHERE is_recurring IS NULL")

        cursor.close()
        conn.close()

        print("\nMigration completed successfully!")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
