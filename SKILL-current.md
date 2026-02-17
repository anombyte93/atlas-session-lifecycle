---
name: start
description: "Unified project initialization: bootstraps session context into session-context/, organizes existing files into a professional structure, generates/updates CLAUDE.md with maintenance rules, and launches Ralph Loop. Use when user says /start, /init, bootstrap session, initialize session, or organize project."
user-invocable: true
---

# Session Init Skill

> Unified project initialization: bootstraps session context into `session-context/`, organizes existing files into a professional structure, generates/updates CLAUDE.md with maintenance rules, and launches Ralph Loop.

## Overview

This skill performs deterministic session initialization + project organization:
1. Capture soul purpose from user
2. Detect environment (git, existing files, existing structure)
3. Bootstrap `session-context/` with memory bank templates
4. Scan & categorize existing root-level files
5. Propose organization map for user approval
6. Execute file moves
7. Generate/update CLAUDE.md with structure + maintenance rules
8. Load context silently and launch Ralph Loop

## Rules

- Act as pure bootstrap + organizer - no governance or decision authority
- All state lives in files, not chat memory
- Idempotent per session directory - safe to run multiple times
- If `session-context/` files exist, do NOT overwrite unless explicitly instructed
- If project is already organized (few files at root), skip Steps 4-6
- **NEVER** edit template files in `~/claude-session-init-templates/` - they are immutable
- Confirm nothing except the organization map (Step 5). Execute deterministically otherwise.

## Templates

**Source**: `~/claude-session-init-templates/`

These are IMMUTABLE template files. Copy them, never edit them:
- `CLAUDE-activeContext.md` - Session state tracker
- `CLAUDE-decisions.md` - Architecture decision log
- `CLAUDE-patterns.md` - Code patterns and conventions
- `CLAUDE-soul-purpose.md` - Soul purpose placeholder
- `CLAUDE-troubleshooting.md` - Issue resolution guide
- `CLAUDE-mdReference.md` - CLAUDE.md template (rename to CLAUDE.md on copy)

---

## Execution

### STEP 1 — SOUL PURPOSE

Use the AskUserQuestion tool to ask:

```yaml
question: "What is the soul purpose of this project?"
header: "Purpose"
options: []
multiSelect: false
```

Store the response verbatim as `SOUL_PURPOSE`.

---

### STEP 2 — DETECT ENVIRONMENT

Run these checks silently (do NOT report to user):

```bash
# Is this a git repo?
git rev-parse --git-dir 2>/dev/null && echo "GIT=true" || echo "GIT=false"

# Does session-context/ already exist?
[ -d session-context ] && echo "SESSION_CTX=exists" || echo "SESSION_CTX=missing"

# Does CLAUDE.md already exist?
[ -f CLAUDE.md ] && echo "CLAUDE_MD=exists" || echo "CLAUDE_MD=missing"

# Count root-level files (excluding directories, hidden files, CLAUDE.md)
ls -1p | grep -v / | grep -v "^CLAUDE" | wc -l
```

Set internal flags:
- `IS_GIT`: true/false (determines `git mv` vs `mv`)
- `HAS_SESSION_CTX`: true/false (skip bootstrap if exists)
- `HAS_CLAUDE_MD`: true/false (generate vs update)
- `ROOT_FILE_COUNT`: number (skip organization if <= 10)

---

### STEP 3 — BOOTSTRAP SESSION CONTEXT

**If `session-context/` does NOT exist**:

```bash
mkdir -p session-context
```

Copy templates into `session-context/`:
```bash
cp ~/claude-session-init-templates/CLAUDE-activeContext.md session-context/
cp ~/claude-session-init-templates/CLAUDE-decisions.md session-context/
cp ~/claude-session-init-templates/CLAUDE-patterns.md session-context/
cp ~/claude-session-init-templates/CLAUDE-troubleshooting.md session-context/
cp ~/claude-session-init-templates/CLAUDE-soul-purpose.md session-context/
```

**If old CLAUDE-* files exist at root** (from previous /start runs):
Migrate them into `session-context/` instead of overwriting:
```bash
# Only move if they exist at root AND session-context/ versions don't exist
for f in CLAUDE-activeContext.md CLAUDE-decisions.md CLAUDE-patterns.md CLAUDE-troubleshooting.md CLAUDE-soul-purpose.md; do
  [ -f "$f" ] && [ ! -f "session-context/$f" ] && mv "$f" session-context/
  [ -f "$f" ] && [ -f "session-context/$f" ] && rm "$f"  # remove root copy if session-context version exists
done
```

**Write soul purpose** to `session-context/CLAUDE-soul-purpose.md`:

Open `session-context/CLAUDE-soul-purpose.md` and replace its contents with:
```markdown
# Soul Purpose

{{SOUL_PURPOSE}}
```

Ensure `SOUL_PURPOSE` is fully resolved to user's actual text.

**VERIFY**: Run `ls session-context/` - should see 5 files.

---

### STEP 4 — SCAN & CATEGORIZE

**Skip this step if `ROOT_FILE_COUNT` <= 10** (project is already clean).

Scan all files at root level. Auto-detect categories by extension and naming:

**Category Map**:
| Pattern | Target Directory | Subcategory Logic |
|---------|-----------------|-------------------|
| `.sh`, `.bash` | `scripts/` | By purpose: ssh/, setup/, diagnostics/, fixes/ |
| `.ps1` | `scripts/` | By purpose: ssh/, setup/, diagnostics/, network/, fixes/ |
| `.py`, `.js`, `.ts` | `scripts/` | By purpose or `src/` if app code |
| `.md` (README-*, GUIDE-*, HOW-*) | `docs/guides/` | |
| `.md` (REPORT-*, AUDIT-*, SUMMARY-*) | `docs/reports/` | |
| `.md` (QUICK-START*, SETUP-*) | `docs/quickstart/` | |
| `.md` (CONTRACT-*, FULFILLMENT-*) | `docs/contract/` | |
| `.md` (HANDOVER-*, HANDOFF-*, CLIENT-*) | `docs/handover/` | |
| `.txt` (quick-start, setup) | `docs/quickstart/` | |
| `.txt` (diagnostic, report) | `docs/reports/` | |
| `.json`, `.yaml`, `.toml` | `config/` | Unless framework-required at root |
| `.log` | `logs/` | |

**Files that ALWAYS stay at root**:
- `CLAUDE.md` (Claude Code requirement)
- `README.md` (convention)
- `LICENSE`, `LICENSE.md`
- `contract.md` (or primary SOW/spec file)
- `package.json`, `package-lock.json`, `pnpm-lock.yaml` (Node.js convention)
- `.gitignore`, `.env`, `.env.example`
- `Makefile`, `Dockerfile`, `docker-compose.yml`
- `tsconfig.json`, `vite.config.*`, `next.config.*`
- Any file the user explicitly marks as "keep at root"

**Subcategory detection for scripts**:
- Name contains `connect`, `ssh`, `remote` → `scripts/ssh/`
- Name contains `setup`, `install`, `create`, `init` → `scripts/setup/`
- Name contains `diagnose`, `analyze`, `scan`, `audit` → `scripts/diagnostics/`
- Name contains `network`, `process`, `close` → `scripts/network/`
- Name contains `fix`, `repair`, `permission` → `scripts/fixes/`
- Default → `scripts/misc/`

Build a proposed move map as a data structure:
```
{
  "source_file": "target_directory",
  ...
}
```

---

### STEP 5 — PROPOSE ORGANIZATION MAP

Present the proposed moves to the user using AskUserQuestion:

```yaml
question: "Here's the proposed file organization. [SHOW MAP AS TABLE]. Approve or edit?"
header: "Organize"
options:
  - label: "Approve"
    description: "Move all files as proposed"
  - label: "Edit"
    description: "I want to change some placements before moving"
  - label: "Skip"
    description: "Don't reorganize, just bootstrap session context"
multiSelect: false
```

**If "Edit"**: Ask which files to change, update the map, re-present.
**If "Skip"**: Jump to Step 7.
**If "Approve"**: Continue to Step 6.

---

### STEP 6 — EXECUTE MOVES

Create all target directories first:
```bash
# Extract unique directories from the move map and create them
mkdir -p [all unique target directories]
```

Move files using appropriate command:
- **If `IS_GIT=true` AND file is tracked**: Use `git mv source target`
- **If `IS_GIT=false` OR file is untracked**: Use `mv source target`

Execute all moves. Do NOT ask for confirmation (user already approved in Step 5).

**VERIFY**: `ls` each target directory to confirm files landed correctly.

---

### STEP 7 — GENERATE/UPDATE CLAUDE.md

**If `CLAUDE.md` does NOT exist**:

Copy from template and populate:
```bash
cp ~/claude-session-init-templates/CLAUDE-mdReference.md ./CLAUDE.md
```

Then fill in the `[placeholder]` sections:
- `[Project Name]` → Infer from directory name or ask user
- `[Primary objective]` → Use `SOUL_PURPOSE`
- Project Structure section → Generate from actual directory contents
- Ralph Loop Variables → Set `--completion-promise` from soul purpose context

**If `CLAUDE.md` already exists**:

Ask user which update approach they prefer:

```yaml
question: "CLAUDE.md exists. How should I update the path references?"
header: "Update mode"
options:
  - label: "Patch paths (Recommended)"
    description: "Find-and-replace old file paths with new locations. Preserves all content."
  - label: "Rebuild structure section"
    description: "Regenerate the Project Structure section from actual directory state. Preserves everything else."
  - label: "Skip"
    description: "Don't touch CLAUDE.md"
multiSelect: false
```

**For either update mode**, ALWAYS ensure these sections exist in CLAUDE.md:

1. **Project Structure** - Reflects actual directory layout
2. **Structure Maintenance Rules** - The following block MUST be present:

```markdown
## Structure Maintenance Rules

> These rules ensure the project stays organized across sessions.

- **CLAUDE.md** stays at root (Claude Code requirement)
- **Session context** files live in `session-context/` - NEVER at root
- **Scripts** (.sh, .ps1, .py, .js, .ts) go in `scripts/<category>/`
- **Documentation** (.md, .txt guides/reports) go in `docs/<category>/`
- **Config** files (.json, .yaml, .toml) go in `config/` unless framework-required at root
- **Logs** go in `logs/`
- When creating new files, place them in the correct category directory
- Do NOT dump new files at root unless they are actively being worked on
- Periodically review root for stale files and move to correct category
```

3. **Session Context Files** - References use `session-context/` prefix:
```markdown
## Session Context Files (MUST maintain)

After every session, update these files in `session-context/` with timestamp and reasoning:

- `session-context/CLAUDE-activeContext.md` - Current session state, goals, progress
- `session-context/CLAUDE-decisions.md` - Architecture decisions and rationale
- `session-context/CLAUDE-patterns.md` - Established code patterns and conventions
- `session-context/CLAUDE-troubleshooting.md` - Common issues and proven solutions
```

4. **Immutable Template Rules** - Append at bottom if not present:
```markdown
## IMMUTABLE TEMPLATE RULES

> **DO NOT** edit the template files in `~/claude-session-init-templates/`
> Templates are immutable source-of-truth. Only edit the copies in your project.
```

---

### STEP 8 — LOAD CONTEXT & LAUNCH

**Silently read and internalize** contents of:
- `CLAUDE.md`
- `session-context/CLAUDE-activeContext.md`
- `session-context/CLAUDE-decisions.md`
- `session-context/CLAUDE-patterns.md`
- `session-context/CLAUDE-soul-purpose.md`
- `session-context/CLAUDE-troubleshooting.md`

**Do not** summarize to user.
**Do not** ask clarifying questions.
Treat these files as authoritative session state.

**Extract Ralph Loop variables** from `CLAUDE.md`:
- Goal or Mission
- Constraints
- Loop limits or stopping conditions
- Required tools or modes

If variables present, bind automatically.
If variables missing, use safe defaults inferred from `SOUL_PURPOSE`.

**Immediately invoke**:
```
/ralph-wiggum:ralph-loop
```

Run using:
- Extracted variables from CLAUDE.md
- `SOUL_PURPOSE` value as part of mission context
- All loaded session-context files as persistent memory

**Do not** explain what you are doing.
**Do not** restate configuration.
Proceed directly into Ralph Loop execution.
