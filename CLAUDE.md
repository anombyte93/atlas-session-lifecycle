# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Project**: Skill Init vNext — Session Lifecycle Skill for Claude Code
**Goal**: Evolve the `/start` skill from a one-time bootstrapper into a two-mode session lifecycle manager with soul purpose completion protocol, active context harvesting, and Claude `/init` integration.
**Stack**: Claude Code Skills (Markdown-defined), MCP, Task Agents

### What This Is

This repo contains a single Claude Code skill (`SKILL.md`) that users invoke via `/start`. The skill auto-detects which mode to run based on directory state:

- **Init Mode** (first run): `session-context/` does NOT exist. Captures soul purpose, bootstraps session-context files from immutable templates, organizes project files, generates CLAUDE.md with governance sections, runs Claude's built-in `/init`, onboards Ralph Loop (automatic/manual/skip).
- **Reconcile Mode** (subsequent runs): `session-context/` DOES exist. Refreshes CLAUDE.md via Claude `/init`, reads soul purpose + active context, self-assesses completion status, optionally suggests doubt agent verification, presents user with Close/Continue/Redefine decision, harvests active context on closure.

The previous version of the skill (`SKILL-current.md`) was a linear bootstrapper with no lifecycle management. The vNext (`SKILL.md`) adds the reconciliation loop, soul purpose lifecycle, and agent-driven execution.

### Key Files

| File | Purpose |
|------|---------|
| `SKILL.md` | The deliverable -- complete skill definition (~870 lines) |
| `SKILL-current.md` | Previous skill version (reference only) |
| `chatGPTConvo.md` | Original design conversation transcript |
| `docs/plans/2026-02-10-skill-init-vnext-design.md` | Approved design document |
| `session-context/` | Memory bank files managed by the skill |

### Hard Invariants

1. **User authority is absolute** -- AI NEVER closes a soul purpose. Only suggests; user decides.
2. **Zero unsolicited behavior** -- Skill ONLY runs when user types `/start`. No hooks, no proactive triggers.
3. **Human-visible memory only** -- All state lives in files. Nothing hidden in chat memory.
4. **Idempotent** -- Safe to run multiple times. Re-running does not corrupt state.
5. **Templates are immutable** -- NEVER edit files in `~/claude-session-init-templates/`. Copy only.
6. **Reconcile mode is audit, not rewrite** -- Targeted changes only. Do not regenerate what already exists.

### Two-Mode Architecture

**Mode detection** is automatic from directory state:
```
if session-context/ does NOT exist → Init Mode
if session-context/ DOES exist     → Reconcile Mode
```

**Claude `/init` ordering differs by mode**:
| Mode | Order | Reason |
|------|-------|--------|
| Init | Our bootstrap THEN `/init` | `/init` needs structure to analyze first |
| Reconcile | `/init` first THEN our reconciliation | Codebase exists; let `/init` refresh CLAUDE.md before we layer governance |

**Agent-driven execution**: All file I/O is delegated to Task agents in waves. The main conversation thread is a thin orchestrator that holds the plan, dispatches agents, and tracks progress. This prevents context death spirals from reading large files directly.

---

## Structure Maintenance Rules

> These rules ensure the project stays organized across sessions.

- **CLAUDE.md** stays at root (Claude Code requirement)
- **SKILL-current.md** stays at root (active skill definition, frequently referenced)
- **Session context** files live in `session-context/` - NEVER at root
- **Design plans and architecture docs** go in `docs/plans/`
- **Documentation** (.md guides, reports, references) go in `docs/`
- **Scripts** (.sh, .py, .js, .ts) go in `scripts/<category>/` when created
- **Config** files (.json, .yaml, .toml) go in `config/` unless framework-required at root
- **Logs** go in `logs/`
- When creating new files, place them in the correct category directory
- Do NOT dump new files at root unless they are actively being worked on
- Periodically review root for stale files and move to correct category

---

## Session Context Files (MUST maintain)

After every session, update these files in `session-context/` with timestamp and reasoning:

- `session-context/CLAUDE-activeContext.md` - Current session state, goals, progress
- `session-context/CLAUDE-decisions.md` - Architecture decisions and rationale
- `session-context/CLAUDE-patterns.md` - Established code patterns and conventions
- `session-context/CLAUDE-troubleshooting.md` - Common issues and proven solutions

**Entry Format**:
```markdown
## HH:MM DD/MM/YY
### REASON
Who:
What:
When:
Where:
Why:
How:
References:
Git Commit:
Potential Issues to face:
```

---

## Design Requirements

> These constraints govern how all skill operations are implemented.

- **All skill operations MUST be delegated to Task agents** (parallel where dependencies allow)
- **Main conversation = thin orchestrator only** -- it holds the plan, dispatches agents, and tracks progress
- **Agents return short summaries, not full file contents** -- e.g. "Updated session-context/CLAUDE-activeContext.md lines 12-30 with new goal state"
- Never read large files (>150 lines) directly in the main conversation; delegate reads to Task agents
- After compact events, recover state via `git diff --stat` and `git log --oneline -5` instead of re-reading source files
- Wave-based execution: if a plan touches 3+ files, dispatch parallel agents grouped by dependency order

---

## Common Commands

### Research
```bash
mcp-cli call perplexity-api-free/perplexity_pro_search '{"query": "<your research query>"}'
```

### Git
```bash
git status
git diff --stat
git log --oneline -5
```

### MCP Discovery
```bash
mcp-cli tools
mcp-cli info <server>/<tool>
```

---

## Current Status

### DONE
- Initial project structure created
- Session context files bootstrapped
- Design plan drafted and approved (`docs/plans/2026-02-10-skill-init-vnext-design.md`)
- Current skill definition captured (`SKILL-current.md`)
- Original design conversation preserved (`chatGPTConvo.md`)
- Full SKILL.md implemented with both Init and Reconcile modes (~870 lines)
- Agent-driven execution pattern documented (wave-based dispatch)
- Soul purpose completion protocol (self-assess -> optional doubt -> user decides)
- Active context harvesting flow with promotion rules
- Ralph Loop onboarding (automatic/manual/skip replaces auto-launch)
- Claude /init integration with governance section caching/restoration
- Session context validation and repair logic for Reconcile mode

### NEED TO DO
- Test skill across multiple projects and session scenarios
- Verify idempotency (run /start multiple times without corruption)

### RECENTLY COMPLETED
- Validate design doc against final implementation (verified by 3x doubt agents)
- Deploy: overwrite original skill at `~/.claude/skills/start/SKILL.md` with vNext (deployed, diff confirmed identical)
- End-to-end test of Reconcile flow (ran live: self-assess, doubt agent, harvest)

### CRITICAL WARNINGS
- Do NOT edit template files in `~/claude-session-init-templates/` -- templates are immutable source-of-truth
- Do NOT read large files directly in main conversation -- delegate to Task agents
- The current `/start` skill is a working bootstrapper -- do not break it while evolving it
- SKILL.md is the deliverable; SKILL-current.md is reference only

---

## Workflow Before Completing Tasks

1. Use 3 explore agents to understand the issue
2. Invoke `superpower:brainstorm` skill
3. Invoke PLAN mode to create a plan
4. Invoke `prd-taskmaster` skill for task breakdown backed by DEEP research
5. Invoke debugger in parallel if not a sequential task
6. After each parent task: invoke `@doubt-agent` and `@finality-agent` to verify
7. Loop until task complete and verified working from user feedback

**Research**: Use `perplexity-api-free` for comprehensive DEEP research before any work.

---

## Ralph Loop Variables

When user invokes `/ralph-wiggum:ralph-loop`:

```bash
--completion-promise "Must validate sequentially with 3x @doubt agents and 1x finality agent"
--max-iterations 5
```

**Mode**: manual (user triggers each iteration explicitly; no automatic looping)

---

## User Commands

### `/ralph-wiggum:ralph-loop <prompt>`
Starts Ralph Loop with variables from Ralph Loop Variables section above.
Mode is **manual** -- the user controls when each iteration begins.

### `state`
Shows what has been done, what needs to be done, and recent content from context files.
Also updates `session-context/CLAUDE-activeContext.md`, `session-context/CLAUDE-decisions.md`, `session-context/CLAUDE-patterns.md`, `session-context/CLAUDE-troubleshooting.md` if they haven't been updated.

---

## Architecture Decisions

See `session-context/CLAUDE-decisions.md` for full decision log.

---

## Troubleshooting

See `session-context/CLAUDE-troubleshooting.md` for full troubleshooting guide.

---

## IMMUTABLE TEMPLATE RULES

> **DO NOT** edit the template files in `~/claude-session-init-templates/`
> Templates are immutable source-of-truth. Only edit the copies in your project.
