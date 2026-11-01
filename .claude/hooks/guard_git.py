#!/usr/bin/env python3
"""PreToolUse hook (PA8 Task 1.3b): blocks git commands that must never run.

Registered in .claude/settings.json for the Bash and PowerShell tools (Claude
Code on Windows runs shell commands through either one). Reads the tool call
as JSON on stdin; the command is at tool_input.command.

Blocks (exit 2, one-line reason on stderr):
  - pushing to main or master (explicit refspec, HEAD/bare push while on
    main/master, --all, --mirror)
  - force-pushing (--force, -f, --force-with-lease, --force-if-includes,
    or a +refspec)
  - skipping hooks (--no-verify anywhere, git commit -n)
  - bypassing the commit-msg hook by overriding core.hooksPath
Everything else passes through untouched (exit 0).
"""
import json
import os
import re
import shlex
import subprocess
import sys

PROTECTED = {"main", "master"}
SEPARATORS = re.compile(r"^[;&|()]+$")
GIT_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
PUSH_OPTS_WITH_VALUE = {"--repo", "-o", "--push-option", "--receive-pack", "--exec"}


def tokenize(command: str) -> list[str]:
    """Split a shell command into tokens, keeping quoted strings whole."""
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()")
        lexer.whitespace_split = True 
        return list(lexer)
    except ValueError:  #unbalanced quotes, PowerShell backticks, etc.
        return command.replace(";", " ; ").replace("|", " | ").split()


def is_git(token: str) -> bool:
    name = token.replace("\\", "/").rsplit("/", 1)[-1].lower()
    return name in ("git", "git.exe")


def git_invocations(tokens: list[str]):
    """Yield (global_opts, subcommand, args) for every git call in the command."""
    for i, tok in enumerate(tokens):
        if not is_git(tok):
            continue
        j, global_opts = i + 1, []
        while j < len(tokens) and tokens[j].startswith("-") and not SEPARATORS.match(tokens[j]):
            opt = tokens[j]
            global_opts.append(opt)
            if opt in GIT_OPTS_WITH_VALUE and j + 1 < len(tokens):
                global_opts.append(tokens[j + 1])
                j += 1
            j += 1
        if j >= len(tokens) or SEPARATORS.match(tokens[j]): 
            continue
        sub = tokens[j]
        args = []
        for tok2 in tokens[j + 1:]:
            if SEPARATORS.match(tok2) or is_git(tok2):
                break
            args.append(tok2)
        yield global_opts, sub, args


def current_branch(cwd: str, global_opts: list[str]) -> str | None:
    """Return the checked-out branch, honouring git -C <path>."""
    run_dir = cwd
    if "-C" in global_opts:
        idx = global_opts.index("-C")
        if idx + 1 < len(global_opts):
            run_dir = os.path.join(cwd, global_opts[idx + 1])
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=run_dir, capture_output=True, text=True, timeout=5, check=False,
        )
    except (OSError, subprocess.SubprocessError): 
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def ref_name(ref: str) -> str:
    ref = ref.lstrip("+")
    for prefix in ("refs/heads/", "heads/"):
        if ref.startswith(prefix):
            return ref[len(prefix):]
    return ref


def check_push(args: list[str], cwd: str, global_opts: list[str]) -> str | None:
    positional, skip = [], False
    for k, arg in enumerate(args):
        if skip:
            skip = False
            continue 
        if arg in PUSH_OPTS_WITH_VALUE:
            skip = True
            continue
        if arg.startswith("--force") or arg == "-f":
            return "force-push is not allowed"
        if re.fullmatch(r"-[A-Za-z]+", arg) and "f" in arg[1:]:
            return "force-push is not allowed"
        if arg in ("--all", "--mirror", "--branches"):
            return "pushing every branch would push main"
        if arg.startswith("-"):
            continue
        positional.append(arg)

    refspecs = positional[1:]  #positional[0] is the remote
    for spec in refspecs:
        if spec.startswith("+"):
            return f"force-push via +refspec ({spec}) is not allowed"
        src, _, dst = spec.partition(":")
        target = ref_name(dst or src) 
        if target == "HEAD":
            target = current_branch(cwd, global_opts) or "main"
        if target in PROTECTED:
            return f"pushing to {target} is not allowed; push a feature branch and merge locally"

    if not refspecs:  #bare `git push` / `git push origin` pushes the current branch
        branch = current_branch(cwd, global_opts)
        if branch is None:
            return "could not determine the current branch; refusing a bare git push"
        if branch in PROTECTED:
            return f"bare git push while on {branch} would push {branch}"
    return None


def check_command(command: str, cwd: str) -> str | None:
    tokens = tokenize(command)
    for global_opts, sub, args in git_invocations(tokens):
        for opt in global_opts:
            if opt.lower().startswith("core.hookspath"):
                return "overriding core.hooksPath would bypass the commit-msg hook"
        if "--no-verify" in args:
            return "--no-verify would skip the commit-msg hook"
        if sub == "commit":
            skip_next = False
            for arg in args:
                if skip_next:
                    skip_next = False
                    continue
                if arg in ("-m", "-F", "-C", "-c", "--message", "--file", "--author"):
                    skip_next = True
                    continue 
                if re.fullmatch(r"-[A-Za-z]+", arg) and "n" in arg[1:]:
                    return "git commit -n (--no-verify) would skip the commit-msg hook"
        if (
            sub == "config"
            and any(a.lower() == "core.hookspath" for a in args)
            and (len([a for a in args if not a.startswith("-")]) > 1 or "--unset" in args)
        ):
            return "changing core.hooksPath would disable the commit-msg hook"
        if sub == "push":
            reason = check_push(args, cwd, global_opts)
            if reason:
                return reason
    return None


def main() -> None:
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace"))
    except json.JSONDecodeError:
        sys.exit(0)
    if payload.get("tool_name") not in ("Bash", "PowerShell"):
        sys.exit(0)
    command = (payload.get("tool_input") or {}).get("command", "")
    cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    reason = check_command(command, cwd)
    if reason:
        print(f"BLOCKED by guard_git.py: {reason}.", file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
