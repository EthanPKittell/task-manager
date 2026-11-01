"""Self-test for guard_git.py: python .claude/hooks/check_guard_git.py

Feeds each case to the hook as a Bash and a PowerShell tool call and checks
the exit code (2 = blocked, 0 = allowed). Bare pushes depend on the current
branch, so the cases run inside a throwaway git repo: first with main checked
out, then on a feature branch. Works from any branch of the real project.
"""
import json
import os
import subprocess
import sys
import tempfile

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guard_git.py")

#(command, expected exit code) with main checked out
CASES = [
    #push to main / master
    ("git push origin main", 2), 
    ("git push -u origin main", 2),
    ("git push origin HEAD:main", 2),
    ("git push origin feat/x:refs/heads/master", 2),
    ("git push", 2),
    ("git push origin", 2),
    ("git push origin HEAD", 2), 
    ("git push --all origin", 2), 
    ("git -C . push origin main", 2),
    ("git status && git push origin main", 2),
    #force-push
    ("git push --force origin feat/x", 2),
    ("git push -f origin feat/x", 2), 
    ("git push -uf origin feat/x", 2),
    ("git push --force-with-lease origin feat/x", 2),
    ("git push --force-with-lease=feat/x origin feat/x", 2),
    ("git push origin +feat/x", 2),
    #skipping hooks
    ('git commit --no-verify -m "fix: x"', 2),
    ('git commit -n -m "fix: x"', 2),
    ('git commit -nm "fix: x"', 2),
    ('git -c core.hooksPath=/dev/null commit -m "fix: x"', 2),
    ("git config core.hooksPath .git/hooks", 2),
    ("git config --unset core.hooksPath", 2), 
    ('git merge --no-verify feat/x', 2),
    #allowed
    ("git status", 0),
    ("git log --oneline -5", 0),
    ("git diff HEAD", 0),
    ("git push origin feat/x", 0), 
    ("git push -u origin feat/x", 0),
    ('git commit -m "feat(tasks): add -n flag docs"', 0),
    ('git commit -am "fix: handle --no-verify text in message"', 0),
    ("git config core.hooksPath", 0),
    ("git merge --no-ff feat/x", 0),
    ("pytest -q", 0), 
    ('echo "push to main"', 0),
]

#(command, expected exit code) with feat/x checked out: a bare push pushes feat/x
FEATURE_CASES = [
    ("git push", 0),
    ("git push origin", 0),
    ("git push origin HEAD", 0), 
    ("git push origin main", 2),
    ("git push --force", 2),
]


def git(repo: str, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, capture_output=True, check=True)


def make_repo(path: str) -> None:
    git(path, "init", "-q")
    git(path, "-c", "user.name=check", "-c", "user.email=check@example.com",
        "commit", "-q", "--allow-empty", "--no-verify", "-m", "chore: init")
    git(path, "branch", "-M", "main")


def run(tool: str, command: str, cwd: str) -> int:
    payload = json.dumps({"tool_name": tool, "tool_input": {"command": command}, "cwd": cwd})
    return subprocess.run([sys.executable, HOOK], input=payload.encode(), capture_output=True, check=False).returncode


def run_cases(label: str, cases: list[tuple[str, int]], cwd: str) -> int:
    print(f"--- {label}")
    failures = 0
    for command, expected in cases:
        for tool in ("Bash", "PowerShell"):
            got = run(tool, command, cwd)
            ok = got == expected
            failures += not ok 
            if not ok or tool == "Bash":
                status = "ok  " if ok else "FAIL"
                print(f"{status} {'BLOCK' if expected == 2 else 'allow'}  {command}" + ("" if ok else f"  ({tool} got {got})"))
    return failures


def main() -> None:
    with tempfile.TemporaryDirectory() as repo:
        make_repo(repo)
        failures = run_cases("on main", CASES, repo)
        git(repo, "switch", "-q", "-c", "feat/x")
        failures += run_cases("on feat/x", FEATURE_CASES, repo)
    total = (len(CASES) + len(FEATURE_CASES)) * 2
    print(f"\n{total - failures}/{total} checks passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()