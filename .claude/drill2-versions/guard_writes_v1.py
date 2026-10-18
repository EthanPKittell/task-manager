#!/usr/bin/env python3
"""PreToolUse hook: blocks writes to protected files and directories."""
import json
import os
import sys

#Populated from CLAUDE.md "Do not touch" and DECOMPOSITION.md SA-1..SA-4 constraints.
BLOCKED_PATHS = [
    "utils/errors.py",        #AppError hierarchy - CLAUDE.md Do-not-touch; every SA constraint
    "migrations/",            #Migrations require human review
    ".env",                   #Secrets - hard block
    ".claude/settings.json",  #Hook config - agents must not self-modify
]

PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

def to_rel(file_path: str) -> str:
    """Convert any path (absolute or relative) to a project-relative path with / separators."""
    abs_path = os.path.abspath(os.path.join(PROJECT_DIR, file_path))
    try:
        rel = os.path.relpath(abs_path, PROJECT_DIR)
    except ValueError:            # different drive on Windows -> outside the project
        return abs_path.replace("\\", "/")
    return rel.replace("\\", "/")

def is_blocked(file_path: str) -> tuple[bool, str]:
    """Return (blocked, reason) for the given file path."""
    rel = to_rel(file_path)
    for pattern in BLOCKED_PATHS:
        if pattern.endswith("/"):
            if rel.startswith(pattern):
                return True, f"Protected directory: {pattern}"
        elif rel == pattern:
            return True, f"Protected file: {pattern}"
    return False, ""

def main(): 
    payload = json.loads(sys.stdin.read())
    tool = payload.get("tool_name", "")
    if tool not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)
 
    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path") or tool_input.get("path", "")

    blocked, reason = is_blocked(file_path) 
    if blocked:
        print(f"BLOCKED: {reason}. This file is protected by project policy.", file=sys.stderr)
        print(f"To modify {file_path}, update CLAUDE.md and remove the", file=sys.stderr)
        print("protection after team review.", file=sys.stderr) 
        sys.exit(2) 
    sys.exit(0)

if __name__ == "__main__":
    main()