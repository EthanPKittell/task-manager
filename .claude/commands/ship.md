---
description: Check the diff for debug code, run the tests, then commit after my approval
allowed-tools: Bash(git status *) Bash(git diff *) Bash(git add *) Bash(pytest -q)
disable-model-invocation: true
---
## Current changes
!`git status --short`
!`git diff HEAD`

Work through these steps in order and stop at the first one that fails.
 
1. Nothing to ship? If the status above is empty, say "Nothing to ship." and stop.
2. Debug check. Look only at lines this diff adds (lines starting with "+"), plus the full
   contents of any untracked file ("??" in the status; read it, since "git diff HEAD" does not 
   show untracked files). Flag:
   - "print(" or "breakpoint(" calls in application code: "app.py", "init_db.py", "routes/",
     "services/", "schemas/", "utils/". Skip "tests/" and ".claude/hooks/", where printing is 
     intentional (hooks report on stdout/stderr)
   - new "TODO" or "FIXME" comments
   - commented-out code (a "#" line that is a Python statement, such as "# return x" or "# print(y)")
   If you find any, list each as "file:line: problem" and stop. Do not fix them.
3. **Tests.** Run "pytest -q". If anything fails or errors, show the failure summary and stop.
   Do not change any code or test to make it pass.
4. **Propose a message.** Propose exactly ONE commit message following "## Git Conventions" in 
   CLAUDE.md: "type(scope): subject", an allowed type and scope, imperative mood, first line at
   most 72 characters. Show it with its character count, then stop and wait for my approval.
5. **Commit, only after I approve.** Stage exactly the files listed in the status above with
   "git add <files>" (never "git add -A" or "git add ."), then run "git commit -m "<message>"".
   Claude Code will ask me to confirm the commit; that prompt is the approval gate. If the
   commit-msg hook rejects the message, show its error and propose a corrected message. 
   Finish by showing "git log --oneline -1".

Never run "git push", never use "--no-verify" or "--amend", and never edit ".githooks/".
