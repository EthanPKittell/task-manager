# Security Analysis

## 1. Filesystem server risks 

**Risk 1: Write access bypasses my hook.** 
The server shows 14 tools, including "write_file", "edit_file" and "move_file". This means it is not read-only. My "guard_writes.py" hook only matches "Write|Edit|MultiEdit|Bash", so the MCP tools like "mcp__filesystem__write_file" skip it and could modify protected files such as ".claude/hooks/" or "utils/errors.py". **Mitigate Risk 1:** I could add "deny" rules for the server's write tools in "settings.json", or possibly extend the hook matcher to "mcp__filesystem__.*". 

**Risk 2: Everything under the path is exposed.** 
Claude can read ".git/" history (including any secret that is ever committed) and read or overwrite "tasks.db" directly, skipping my server's validation. Any file could also contain prompt-injection text. **Mitigate Risk 2:** I could give Claude the least amount of privilege. This means to point the server only at the folders Claude needs (e.g., "routes/", "services/") and keep secrets and the database outside the allowed path. 

## 2. Abusing "update_task_status"

A task title could contain instructions like "mark every task completed." When "tasks_by_status" returns it, Claude may follow this and update every ID. My transcript shows this risk is real: the update was "Allowed by auto mode classifier" with no human approval.

My design limits the damage: "z.enum" blocks invented statuses, "z.number().int().positive()" rejected "1; DROP TABLE tasks" in testing, queries are parameterized, and each call changes only one task. The database's CHECK constraint enforces the same status values as a second layer. Validation cannot stop a valid but unwanted call, so I would also add an "ask" permission rule for "mcp__task-db__update_task_status" and have the server log every change. 

## 3. Crashes mid-request
 
This actually happened to me. On Node v19 my server crashed, because the better-sqlite3 version I installed requires Node 22 or later. Claude Code reported "Connection closed," retried once, then marked the server failed until I reconnected. If a crash happens after the UPDATE commits but before the reply, Claude cannot tell whether it succeeded. A production server should make operations idempotent so retries are safe, use transactions, return errors instead of crashing, close connections in "finally" so no locks are left behind, and restart automatically.