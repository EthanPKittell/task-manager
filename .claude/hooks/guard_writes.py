#!/usr/bin/env python3
"""PreToolUse hook: blocks protected file writes, destructive Bash commands,
and hardcoded DB connection strings."""
import json
import os
import re
import sys

#Populated from CLAUDE.md "Do not touch" and DECOMPOSITION.md SA-1..SA-4 constraints.
BLOCKED_PATHS = [
    "utils/errors.py",        #AppError hierarchy - CLAUDE.md Do-not-touch; every SA constraint
    "migrations/",            #Migrations require human review
    ".env",                   #Secrets - hard block
    ".claude/settings.json",  #Hook config - agents must not self-modify
    ".claude/hooks/",
]

#Extension 1: destructive Bash commands (word-boundary / token-level regexes).
BLOCKED_COMMANDS = [
    (re.compile(r"\b(DROP|TRUNCATE)\s+TABLE\b", re.IGNORECASE),
     "destructive SQL (DROP/TRUNCATE TABLE)"),
    (re.compile(r"(?<![\w-])rm\s+(-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*|-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*)(?=\s|$)"),
     "recursive force delete (rm -rf)"),
    (re.compile(r"(?<![\w-])rm\s+(-r|-R|--recursive)\s+(-f|--force)(?=\s|$)|(?<![\w-])rm\s+(-f|--force)\s+(-r|-R|--recursive)(?=\s|$)"),
     "recursive force delete (rm -r -f)"),
    (re.compile(r"\bgit\s+push\b.*(--force\b|--force-with-lease\b|(?<![\w-])-f(?=\s|$))"),
     "git force-push (rewrites shared history on GitHub)"),
]

#Extension 2: content guard - files Claude may write, but never with a hardcoded DB URL.
CONTENT_GUARDED = ["services/tasks.py"]
CONNECTION_STRING = re.compile(r"postgresql(\+\w+)?://|sqlite:///", re.IGNORECASE)

PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())


def to_rel(file_path: str) -> str:
    """Convert any path (absolute or relative) to a project-relative path with / separators."""
    abs_path = os.path.abspath(os.path.join(PROJECT_DIR, file_path))
    try:
        rel = os.path.relpath(abs_path, PROJECT_DIR)
    except ValueError:  #different drive on Windows -> outside the project
        return abs_path.replace("\\", "/")
    return rel.replace("\\", "/")


def path_key(file_path: str) -> str:
    """Project-relative path folded to lower case for comparison.

    Windows paths are case-insensitive, so Utils/errors.py is the same file as
    utils/errors.py. Folding on every OS only ever blocks more, never less.
    """
    return to_rel(file_path).casefold()


def is_blocked(file_path: str) -> tuple[bool, str]:
    """Return (blocked, reason) for the given file path."""
    key = path_key(file_path)
    for pattern in BLOCKED_PATHS:
        folded = pattern.casefold()
        if pattern.endswith("/"):
            if key.startswith(folded):
                return True, f"Protected directory: {pattern}"
        elif key == folded:
            return True, f"Protected file: {pattern}"
    return False, ""


def check_bash(command: str) -> tuple[bool, str]:
    """Return (blocked, reason) for a Bash command."""
    for regex, reason in BLOCKED_COMMANDS:
        if regex.search(command):
            return True, f"Prohibited command: {reason}"
    return False, ""


#Vector 2 fix: shell operations that create or modify files.
WRITE_OPS = re.compile(
    r">|\btee\b|\bsed\s+(-\w*\s+)*-i|\b(cp|mv|rm|touch|mkdir|truncate|dd)\b"
    r"|write_text|write_bytes|open\([^)]*['\"][wax+]|Set-Content|Add-Content|Out-File|New-Item",
    re.IGNORECASE,
)


def bash_writes_protected(command: str) -> tuple[bool, str]:
    """Return (blocked, reason) if a Bash command writes to a protected path."""
    cmd = command.replace("\\", "/").casefold()
    cmd = re.sub(r"\d*>&\d|\d*>\s*/dev/null", " ", cmd)  #2>&1, >/dev/null are not file writes
    if not WRITE_OPS.search(cmd):
        return False, ""
    for pattern in BLOCKED_PATHS:
        name = re.escape(pattern.casefold().rstrip("/"))
        if re.search(rf"(?<![\w.-]){name}(?![\w-])", cmd):
            return True, f"Bash write to protected path: {pattern}"
    return False, ""


def new_content(tool: str, tool_input: dict) -> str:
    """Return the text a Write/Edit/MultiEdit call is about to put into the file."""
    if tool == "Write":
        return tool_input.get("content", "")
    if tool == "Edit":
        return tool_input.get("new_string", "")
    return "\n".join(e.get("new_string", "") for e in tool_input.get("edits", []))


def block(lines: list[str]) -> None:
    for line in lines:
        print(line, file=sys.stderr)
    sys.exit(2)


def main() -> None:
    payload = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace"))
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})

    if tool == "Bash":
        command = tool_input.get("command", "")
        blocked, reason = check_bash(command)
        if not blocked:
            blocked, reason = bash_writes_protected(command)  #Vector 2 fix
        if blocked:
            block([f"BLOCKED: {reason}.", "Run this yourself outside Claude if it is really needed."])
        sys.exit(0)

    if tool not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    file_path = tool_input.get("file_path") or tool_input.get("path", "")
    blocked, reason = is_blocked(file_path)
    if blocked:
        block([f"BLOCKED: {reason}. This file is protected by project policy.",
               f"To modify {file_path}, update CLAUDE.md and remove the",
               "protection after team review."])

    if path_key(file_path) in [p.casefold() for p in CONTENT_GUARDED] and CONNECTION_STRING.search(new_content(tool, tool_input)):
        block([f"BLOCKED: hardcoded database connection string in {to_rel(file_path)}.",
               "Connection strings must come from environment variables,",
               'e.g. os.environ["DATABASE_URL"], never a postgresql:// or sqlite:/// literal.'])
    sys.exit(0)


if __name__ == "__main__":
    main()
