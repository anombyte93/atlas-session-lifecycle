---
name: sync
description: "Fast save-point: sync all session-context files and MEMORY.md with current progress. Zero questions, zero delay. Use when user says /sync, save progress, save state, sync context, or /sync --full for capability inventory."
user-invocable: true
---

# Sync

> Zero questions. Edit files. Print summary. Done.

## Rules

1. **No questions** — never ask the user anything. Just save.
2. **No subagents** — run entirely in the main thread.
3. **No MCP tools** — direct file reads and edits only (faster).
4. **No narration** — don't announce steps. Just do them.
5. **Touch every file** — even if only adding a timestamp entry.
6. **Speed over perfection** — a rough sync beats no sync.

---

## Execute

Use the current time formatted as `HH:MM DD/MM/YY` for the checkpoint header.

### 0. Touch lifecycle liveness marker

Call `session_hook_touch_sync(project_dir=<cwd>)` via the `atlas-session`
MCP. This stamps `last_sync_at` on
`session-context/.lifecycle-active.json` so the fleet audit script
(`fleet-sync-audit.sh`) can classify session liveness (active/idle/stale).
Backward-compatible: creates the v2 file if it doesn't exist. Non-fatal on
error — never block sync on fleet telemetry.

### 1. Edit `session-context/CLAUDE-activeContext.md`

Append a new section at the end:

```markdown
## [SYNC] {time}

**Accomplished:**
- {bullet list of what was done this session}

**In progress:**
- {what's currently being worked on}

**Next steps:**
- {what comes next}

**Blockers:**
- {any blockers, or "None"}
```

### 2. Edit `session-context/CLAUDE-decisions.md`

Append new decisions made this session. If none, append:

```markdown
## {time}
No new decisions this session.
```

### 3. Edit `session-context/CLAUDE-patterns.md`

Append new patterns discovered. If none, append:

```markdown
## {time}
No new patterns this session.
```

### 4. Edit `session-context/CLAUDE-troubleshooting.md`

Append new issues and solutions. If none, append:

```markdown
## {time}
No new issues this session.
```

### 5. Export tasks to `session-context/CLAUDE-tasks.md`

Call `TaskList`. If any tasks exist (pending, in_progress, or completed):
- Write (overwrite) `session-context/CLAUDE-tasks.md` with:

  ```markdown
  ## Tasks [HH:MM DD/MM/YY]

  ### In Progress
  - [~] #N subject

  ### Pending
  - [ ] #N subject

  ### Completed (this session)
  - [x] #N subject
  ```

If no tasks exist, skip this step (don't create an empty file).

### 6. Update MEMORY.md

Update the auto-memory file at the project memory path with any new learnings from this session. If nothing new, skip this file (memory should stay concise).

### 7. Print summary

Print exactly one block:

```
Synced. {N} files updated.
- Active context: {1-line summary of what was captured}
- Decisions: {count new or "no new"}
- Patterns: {count new or "no new"}
- Troubleshooting: {count new or "no new"}
- Tasks: {N pending, N in_progress exported} or "no tasks"
- Memory: {updated or "no changes"}
```

---

## /sync --full (Capability Inventory)

> Extended sync that includes capability inventory generation.

### Execute

1. Run standard sync flow (Steps 1-6 above).
2. Call `session_capability_inventory(project_dir, force_refresh=True)` — bypasses cache and regenerates inventory even if git unchanged.
3. If `needs_generation == True`: the MCP tool will generate the inventory.
4. Read `CLAUDE-capability-inventory.md` if it exists.

### Print summary

Print the standard sync block above, plus:

```
Capability Inventory: {status}
- MCP Tools: {count}
- Test Coverage: {percentage}
- Critical Untested: {count}
- Inventory: {path}
```
