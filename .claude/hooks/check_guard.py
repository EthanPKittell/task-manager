"""Manual test runner for guard_writes.py. Run from the repo root: python .claude/hooks/check_guard.py"""
import json
import os
import subprocess
import sys

ROOT = os.getcwd()
HOOK = os.path.join(ROOT, ".claude", "hooks", "guard_writes.py")

#(description, tool_name, tool_input, expected exit code)
CASES = [
    #Drill 2 path guard
    ("Write utils/errors.py (relative)", "Write", {"file_path": "utils/errors.py", "content": "x"}, 2),
    ("Edit utils/errors.py (absolute)", "Edit", {"file_path": os.path.join(ROOT, "utils", "errors.py"), "old_string": "a", "new_string": "b"}, 2),
    ("Write into migrations/", "Write", {"file_path": os.path.join(ROOT, "migrations", "versions", "x.py"), "content": "x"}, 2),
    ("Write services/tasks.py (allowed)", "Write", {"file_path": "services/tasks.py", "content": "x = 1"}, 0),
    # xtension 1: Bash guard
    ("DROP TABLE", "Bash", {"command": 'sqlite3 app.db "DROP TABLE tasks;"'}, 2),
    ("truncate table (lowercase)", "Bash", {"command": 'psql -c "truncate table users"'}, 2),
    ("DROP TABLES word is not DROP TABLE", "Bash", {"command": 'echo "DROP TABLESPACE notes"'}, 0),
    ("rm -rf", "Bash", {"command": "rm -rf build"}, 2),
    ("rm -fr", "Bash", {"command": "rm -fr build"}, 2),
    ("rm -r -f", "Bash", {"command": "rm -r -f build"}, 2),
    ("rm -r (no force) allowed", "Bash", {"command": "rm -r build"}, 0),
    ("'farm -rf' is not rm", "Bash", {"command": "echo farm -rf"}, 0),
    ("git push --force", "Bash", {"command": "git push --force origin main"}, 2),
    ("git push -f", "Bash", {"command": "git push -f"}, 2),
    ("git push (normal) allowed", "Bash", {"command": "git push origin main"}, 0),
    ("pytest allowed", "Bash", {"command": "pytest -q"}, 0),
    #Extension 2: content guard
    ("Write postgres URL to services/tasks.py", "Write", {"file_path": "services/tasks.py", "content": 'DB = "postgresql://u:p@localhost/tm"'}, 2),
    ("Edit sqlite URL into services/tasks.py", "Edit", {"file_path": os.path.join(ROOT, "services", "tasks.py"), "old_string": "a", "new_string": 'DB = "sqlite:///tasks.db"'}, 2),
    ("Env var in services/tasks.py allowed", "Write", {"file_path": "services/tasks.py", "content": 'DB = os.environ["DATABASE_URL"]'}, 0),
    #Part B bypass vectors
    ("VECTOR 1: Edit Utils/errors.py (capital U)", "Edit", {"file_path": os.path.join(ROOT, "Utils", "errors.py"), "old_string": "a", "new_string": "b"}, 2),
    ("VECTOR 2: bash heredoc to utils/errors.py", "Bash", {"command": "cat >> utils/errors.py <<'EOF'\nclass RateLimitError(AppError): pass\nEOF"}, 2),
    ("VECTOR 2: sed -i on utils/errors.py", "Bash", {"command": "sed -i 's/400/418/' utils/errors.py"}, 2),
    ("VECTOR 2: python write_text", "Bash", {"command": "python -c \"import pathlib; pathlib.Path('utils/errors.py').write_text('x')\""}, 2),
    ("VECTOR 2: mkdir migrations", "Bash", {"command": "mkdir -p migrations/versions"}, 2),
    ("Reading utils/errors.py via bash allowed", "Bash", {"command": "cat utils/errors.py"}, 0),
    ("2>&1 on a read is not a write", "Bash", {"command": "ruff check utils/errors.py 2>&1 | tail -5"}, 0),
    ("Content guard is case-insensitive too", "Write", {"file_path": os.path.join(ROOT, "Services", "tasks.py"), "content": 'DB = "sqlite:///x.db"'}, 2),
    ("grep utils/errors.py allowed", "Bash", {"command": "grep -n class utils/errors.py"}, 0),
]

failures = 0
for desc, tool, tool_input, expected in CASES:
    payload = json.dumps({"tool_name": tool, "tool_input": tool_input})
    result = subprocess.run([sys.executable, HOOK], input=payload.encode(), capture_output=True, check=False)
    ok = result.returncode == expected
    failures += not ok
    verdict = "PASS" if ok else "FAIL"
    print(f"{verdict}  exit={result.returncode} expected={expected}  {desc}")
print(f"\n{len(CASES) - failures}/{len(CASES)} cases as expected")
