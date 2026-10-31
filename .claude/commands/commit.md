---
description: Review the diff, then commit after my approval
allowed-tools: Bash(git status *) Bash(git diff *) Bash(git add *) Bash(git commit *)
disable-model-invocation: true
---
## Current changes
!`git status --short`
!`git diff HEAD`

Review the changes above for:
- print() or breakpoint() calls in application code
- TODO or FIXME comments added in this diff
- commented-out code

If you find any, list each one with its file and line, and stop.
Otherwise, propose ONE conventional commit message (type(scope): subject,
imperative mood, under 72 characters) and wait for my approval.
Only after I approve: stage the changed files and run git commit.
