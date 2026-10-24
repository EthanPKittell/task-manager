"""Create and seed tasks.db for the Week 7 MCP project (PA7).

Builds a SQLite database from the in-memory TASKS and USERS dictionaries in
services/, converting them to the columns PA7 expects:

    id | title | status | assigned_to | due_date | priority

status is one of "open", "in_progress" or "completed" (done=True becomes
"completed", done=False becomes "open"). assigned_to holds the user's name,
looked up from user_id.

Usage (from the task-manager folder):
    python init_db.py

Running it again rebuilds tasks.db from scratch, which resets any changes
made through the MCP server.
"""

import os
import sqlite3

from services.tasks import TASKS
from services.users import USERS

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.db")

SCHEMA = """
CREATE TABLE tasks (
    id          INTEGER PRIMARY KEY,
    title       TEXT    NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'open'
                        CHECK (status IN ('open', 'in_progress', 'completed')),
    assigned_to TEXT,
    due_date    TEXT,
    priority    INTEGER NOT NULL DEFAULT 3 CHECK (priority BETWEEN 1 AND 5)
);
"""

#Due dates for the three tasks already in services/tasks.py, which have none.
EXISTING_DUE_DATES = {1: "2026-10-28", 2: "2026-11-03", 3: "2026-10-20"}

#Extra tasks so every status has rows and there is more than one open task
#to mark completed in the Part 2b transcript.
EXTRA_TASKS = [
    ("Write unit tests",        "open",        "Alice", "2026-11-05", 2),
    ("Fix login bug",           "open",        "Bob",   "2026-10-30", 1),
    ("Update README",           "open",        "Alice", "2026-11-10", 4),
    ("Review pull request #14", "in_progress", "Bob",   "2026-10-27", 2),
    ("Refactor task routes",    "in_progress", "Alice", "2026-11-07", 3),
    ("Set up CI pipeline",      "completed",   "Bob",   "2026-10-15", 3),
    ("Plan sprint 8",           "open",        "Bob",   "2026-11-12", 3),
]


def build_rows() -> list[tuple]:
    """Convert the in-memory tasks to rows and append the extra seed tasks."""
    rows = []
    for task in sorted(TASKS.values(), key=lambda t: t["id"]):
        user = USERS.get(task["user_id"])
        rows.append((
            task["id"],
            task["title"],
            "completed" if task["done"] else "open",
            user["name"] if user else None,
            EXISTING_DUE_DATES.get(task["id"]),
            task["priority"],
        ))
    next_id = max(TASKS) + 1
    for offset, (title, status, assigned_to, due_date, priority) in enumerate(EXTRA_TASKS):
        rows.append((next_id + offset, title, status, assigned_to, due_date, priority))
    return rows


def main() -> None:
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA)
        rows = build_rows()
        conn.executemany(
            "INSERT INTO tasks (id, title, status, assigned_to, due_date, priority) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()
        counts = conn.execute(
            "SELECT status, COUNT(*) FROM tasks GROUP BY status ORDER BY status"
        ).fetchall()
    finally:
        conn.close()
    print(f"Created {DB_PATH} with {len(rows)} tasks:")
    for status, n in counts:
        print(f"  {status:<12} {n}")


if __name__ == "__main__":
    main()
