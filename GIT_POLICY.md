# GIT_POLICY.md: task-manager team (4 developers, all using Claude Code)

Every rule names the mechanism that backs it. **Enforced** mechanisms (git hook, Claude Code hook, permission setting) work no matter what the model does. **Advisory** ones (CLAUDE.md, the "/ship" instructions) depend on Claude following them, so anything that matters is also backed by an enforced mechanism or human review.

**Setup, once per clone:** "git config core.hooksPath .githooks". Git doesn't copy config when you clone, so without this step the commit-msg hook doesn't run. ".gitattributes" keeps ".githooks/*" as LF so the hook runs on Windows. The Claude Code hooks and "/ship" come with the repo in ".claude/".

## 1. Branches and commits

| Rule | Mechanism |
|---|---|
| Work on "feat/<topic>", "fix/<topic>" or "docs/<topic>"; Claude Code worktrees are "worktree-<name>". No feature or fix commits directly on "main". | CLAUDE.md (advisory) + human review at merge | 
| Subject is "type(scope): subject" or "type: subject", type in feat/fix/docs/refactor/test/chore, first line <= 72 characters. | **commit-msg git hook** (rejects anything else, from any tool) |
| Scope is one of "tasks", "users", "tags", "api", "errors", "claude", "git"; imperative mood. | CLAUDE.md + "/ship" proposal step (advisory) |
| Commit through "/ship": it checks application code for debug leftovers, runs "pytest -q", proposes one message and waits. | Slash command (advisory checks) |
| A commit happens only after a human approves it. | **Permission setting:** "git commit" is not in "/ship"'s "allowed-tools", so Claude Code asks every time. Answer "Yes", never "Yes, don't ask again", which would save a permanent allow rule and remove the gate. | 
| One logical change per commit; tests go in the same commit as the code they cover. | CLAUDE.md (advisory) + human review |
| Never push to "main"/"master", force-push, skip hooks ("--no-verify", "commit -n") or change "core.hooksPath". | **Claude Code hook** "guard_git.py" (Bash and PowerShell tools) |
| Claude never edits ".githooks/", ".claude/hooks/", ".claude/settings.json" or ".git/config". | **Claude Code hook** "guard_writes.py" ("BLOCKED_PATHS") | 

## 2. Attribution

**Decision: keep the "Co-Authored-By: Claude ..." trailer.** On a team where all four of us use Claude Code, the trailer tells a reviewer which commits were written with Claude, which helps when deciding how closely to read a diff. It costs one line per commit. The argument against it, a noisier history, matters less here than being able to trace who wrote what. 

**Where it's configured:** Claude Code's "attribution" setting. It's on by default, so we leave it unset. If we ever drop the trailer, the change goes in the shared ".claude/settings.json" (committed, so it applies to everyone), not in personal "~/.claude/settings.json" files. **Mechanism:** permission/settings file, plus human review, because "guard_writes.py" blocks Claude from editing that file. The trailer itself is written by Claude, so it's advisory; the commit-msg hook doesn't check for it.

## 3. Parallel worktrees vs sequential work

| Rule | Mechanism |
|---|---|
| Use parallel worktrees ("claude --worktree <name>") when features touch different files or functions. | Human decision at planning |
| When two parallel features change the **same function** (e.g. both add filters to "list_tasks"), agree the shared interface at plan review before coding: new parameters keyword-only, called by name. Otherwise work sequentially. | Human review at the plan-mode gate | 
| Push "main" before creating worktrees (they branch from "origin/main"). | Human step |
| Exit a worktree session with **Keep** until its branch is merged; removing the worktree deletes the branch. | Human step | 

Why: in PA8, archiving and due dates both added a second positional parameter to "list_tasks"; neither session could see the other. Making both keyword-only at plan review turned the signature conflict into a clean union, and the merge still took about 25 minutes across 6 conflict blocks. For small features that both rewrite one function, sequential work is usually cheaper.

## 4. Review and merge rules

| Rule | Mechanism |
|---|---|
| Merge locally with "git merge --no-ff <branch>" and keep git's default "Merge branch ..." message. | CLAUDE.md (advisory); commit-msg hook allows only that non-conventional form |
| **A second team member reviews** any merge that involved conflict resolution, before it is pushed. The author writes a short merge report: each conflict, both sides' intent, the chosen behavior and why. | Human review | 
| **A second team member reviews** any change that modifies or deletes an existing test. The reviewer checks that it still tests the same thing. Claude must stop and ask instead of editing a test to make something pass. | Human review + CLAUDE.md |
| Changes to ".claude/", ".githooks/", CLAUDE.md or "utils/errors.py" need a reviewer and are made by a person; Claude can't write the protected ones. | Human review + "guard_writes.py" |
| Before completing a merge: full "pytest -q" passes, the test count did not drop, "git diff --check" prints nothing, no "<<<<<<<" markers remain. Check that shared closing lines git moved outside the conflict markers didn't leave a test with no assertions. | Human review (the reviewer reruns these) |
| During conflict resolution, Claude explains each side and proposes a resolution **without editing until a person approves**; the person decides the final behavior. | CLAUDE.md / prompt (advisory) + human review | 
| Only a person pushes "main", after the review above. | **"guard_git.py"** blocks Claude; human review for people |