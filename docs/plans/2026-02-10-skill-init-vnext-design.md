# Skill Init vNext — Design Document

**Date**: 2026-02-10
**Status**: Approved
**Source Spec**: chatGPTConvo.md

---

## 1. What This Is

Skill Init vNext evolves the `/start` skill from a one-time project bootstrapper into a **single skill with two operational modes**: Init and Reconcile. It adds lifecycle management for soul purpose, active context harvesting, and an optional doubt-agent verification step — all while remaining **fully passive** (user-invoked only).

## 2. Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Architecture | Single SKILL.md, two modes | Simpler to maintain, one entry point. Mode auto-detected from `session-context/` existence. |
| Event triggers | Manual only (`/start`) | Zero unsolicited behavior. Skill is invisible unless invoked. |
| Completion protocol | Self-assess + optional doubt agent | Quick self-check is free. Doubt agent only suggested when "probably complete." User always decides. |
| Ralph Loop | One-time onboarding (automatic/manual/skip) | Doesn't assume user wants it. Preference saved to CLAUDE.md. |
| Claude /init integration | Conditional ordering | Init mode: our bootstrap THEN /init (need structure first). Reconcile mode: /init THEN our reconciliation (refresh CLAUDE.md first). |

## 3. Hard Invariants

These hold at all times, in both modes:

1. **User authority is absolute** — AI never closes a soul purpose
2. **Zero unsolicited behavior** — skill only runs when user types `/start`
3. **Human-visible memory only** — all state in files, nothing hidden
4. **Idempotent** — safe to run multiple times
5. **Templates are immutable** — never edited in `~/claude-session-init-templates/`
6. **Reconcile mode is audit, not rewrite** — targeted changes only

## 4. Mode Detection

```
if session-context/ does NOT exist:
    → Init Mode
else:
    → Reconcile Mode
```

No flags, no arguments. The user just runs `/start`.

## 5. Init Mode (First Run)

### Flow

```
1.  Ask soul purpose
2.  Detect environment (git, files, structure)
3.  Bootstrap session-context/ (copy 5 templates, write soul purpose)
4.  Scan & categorize root files (skip if ≤10 files)
5.  Propose organization map → user approves/edits/skips
6.  Execute moves (git mv or mv)
7.  Generate CLAUDE.md from template
8.  Run Claude's built-in /init (now there's structure to analyze)
9.  Ralph Loop onboarding (explain → automatic/manual/skip → save)
10. If Ralph Loop = automatic → launch it
```

### What stays from current skill
- Steps 1-7 are unchanged from the current SKILL.md
- Same file category detection rules
- Same template system
- Same idempotency guarantees

### What's new in Init Mode
- Step 8: Claude `/init` integration (runs AFTER bootstrap)
- Steps 9-10: Ralph Loop onboarding replaces auto-launch

## 6. Reconcile Mode (Subsequent Runs)

### Flow

```
1.  Run Claude's built-in /init (refresh CLAUDE.md from codebase)
2.  Read soul purpose + active context
3.  Quick self-assessment:
    - clearly_incomplete → skip to step 6
    - probably_complete → go to step 4
    - uncertain → go to step 4
4.  Suggest doubt agent verification (user accepts or skips)
5.  Present user decision:
    - Close → harvest active context, promote to durable files, clear, archive purpose
    - Continue → no changes
    - Redefine → harvest, ask for new purpose
6.  Check Ralph Loop preference in CLAUDE.md
7.  If automatic → launch Ralph Loop
```

### Self-Assessment Criteria

The AI reads `CLAUDE-soul-purpose.md` and `CLAUDE-activeContext.md` and checks:

| Signal | Assessment |
|--------|-----------|
| Open tasks remain, active blockers present | `clearly_incomplete` |
| Success criteria appear met, no open TODOs, artifacts exist | `probably_complete` |
| Mixed signals, some done / some unclear | `uncertain` |

This is pure file reading + reasoning. No agents, no extra cost.

### Doubt Agent Escalation

Only triggered for `probably_complete` or `uncertain`. The skill **suggests**, never auto-invokes:

> "Soul purpose appears potentially complete. Want me to run a doubt verification before we decide?"

If yes → invoke `doubt-agent` with soul purpose, success criteria, current artifacts.
If no → skip to user decision.

### User Decision (Always Final)

Three options via `AskUserQuestion`:
- **Close soul purpose** — triggers harvest flow
- **Continue** — keep working, no changes
- **Redefine** — harvest old context, ask for new purpose

If the user picks "Continue," nothing changes. Zero pressure.

## 7. Active Context Harvesting

Triggered when user closes or redefines a soul purpose.

### Flow

```
1. Read CLAUDE-activeContext.md fully
2. Scan for durable content:
   - Decisions → promote to CLAUDE-decisions.md
   - Patterns → promote to CLAUDE-patterns.md
   - Issues solved → promote to CLAUDE-troubleshooting.md
3. Present proposed promotions as summary
4. User approves
5. Append promoted content to durable files
6. Clear CLAUDE-activeContext.md back to template state
7. Archive closed soul purpose:
   - Append to CLAUDE-soul-purpose.md with [CLOSED] marker and date
8. If Close → ask for new soul purpose (or leave blank)
   If Redefine → ask for new soul purpose immediately
```

### Promotion Rules

- Only promote content that is **finalized** (not provisional)
- Decisions must have rationale (not just "we decided X")
- Patterns must have been reused at least once
- Troubleshooting entries must have verified solutions
- When in doubt, leave content unharvested (user can manually promote later)

## 8. Ralph Loop Onboarding

One-time onboarding during Init Mode only.

### Explanation (shown to user)

> "Ralph Loop is an iterative execution loop that works toward your soul purpose autonomously, checking its own work with doubt agents. It's useful for complex multi-step projects where you want Claude to keep pushing forward without constant prompting."

### Options

- **Automatic** — Ralph Loop launches every time `/start` runs
- **Manual** — Installed but only runs when you invoke it yourself
- **Skip** — Not installed. Can be added later.

### Persistence

Choice saved to CLAUDE.md under a `## Ralph Loop` section:

```markdown
## Ralph Loop

**Mode**: automatic | manual | skip
```

On Reconcile Mode, the skill reads this preference and acts accordingly.
No re-asking. User edits CLAUDE.md directly to change preference.

## 9. Claude /init Integration

### Why

Claude's built-in `/init` command analyzes the codebase and generates/updates CLAUDE.md. Our skill layers governance (session-context, soul purpose, lifecycle rules) on top of what `/init` produces.

### Ordering Logic

| Mode | Order | Reason |
|------|-------|--------|
| Init | Our bootstrap → then `/init` | `/init` needs structure to analyze. Our bootstrap creates that structure. |
| Reconcile | `/init` first → then our reconciliation | Codebase exists. Let `/init` refresh CLAUDE.md before we layer our governance. |

### Implementation

The skill invokes Claude's `/init` as a step in its flow. The `/init` output enriches CLAUDE.md; our skill then ensures the governance sections (Structure Maintenance Rules, Session Context Files, Immutable Template Rules, Ralph Loop) are present.

## 10. Memory File Roles (Unchanged)

| File | Role | Lifecycle |
|------|------|-----------|
| `CLAUDE-activeContext.md` | Volatile working memory | Ephemeral, scoped to one soul purpose |
| `CLAUDE-soul-purpose.md` | Governing objective | Updated on purpose change/close |
| `CLAUDE-decisions.md` | Durable decision log (ADR-style) | Append-only |
| `CLAUDE-patterns.md` | Reusable abstractions | Grows slowly |
| `CLAUDE-troubleshooting.md` | Known issues + fixes | Append-only |
| `CLAUDE.md` | Governance contract | Changes rarely |

## 11. What This Design Prevents

- **Context drift** — reconciliation audits files on demand
- **Active context rot** — harvesting clears stale working memory
- **Premature AI stopping** — AI never closes soul purpose
- **Infinite AI execution** — user can close/redefine at any checkpoint
- **Redundant files** — each file has a role + lifecycle + enforcement
- **Annoying interruptions** — skill is 100% passive, user-invoked only

## 12. Implementation Scope

Changes to SKILL.md:
1. Add mode detection logic (init vs reconcile)
2. Add reconcile mode flow (steps 1-7 of reconcile)
3. Add self-assessment logic
4. Add doubt agent suggestion step
5. Add harvest flow
6. Add Ralph Loop onboarding (replaces auto-launch)
7. Add Claude `/init` integration at correct position per mode
8. Update rules section with new invariants

Files unchanged:
- All 6 templates in `~/claude-session-init-templates/`
- Memory file roles and structure

## 13. Agent-Driven Execution (Mandatory)

All skill operations MUST be delegated to Task agents. The skill's main conversation thread acts as a thin orchestrator only.

### Why

Reading and writing large files (session-context files, CLAUDE.md, source code) directly in the main conversation causes context death spirals — compact → re-read → fills context → compact → repeat. Agents have their own context windows and don't pollute the main thread.

### Rules

1. **NEVER read files >150 lines directly in the main skill flow**
2. **Delegate ALL file reading, analysis, and editing to Task agents**
3. **Main conversation holds the plan, dispatches agents, tracks progress**
4. **Each agent gets**: specific instructions, file paths, clear edit requirements
5. **Agents return**: short summary of what changed (file, what was done)
6. **Parallel agents where dependencies allow** — e.g. populating active context and generating CLAUDE.md can run simultaneously

### Agent Dispatch Pattern

Init Mode parallelization:
- Wave 1: Bootstrap session-context (single agent — sequential file copies)
- Wave 2 (parallel): Populate active context + Generate CLAUDE.md
- Wave 3: Run Claude /init (must wait for CLAUDE.md to exist)
- Wave 4: Ralph Loop onboarding (interactive, main thread)

Reconcile Mode parallelization:
- Wave 1: Run Claude /init
- Wave 2: Read soul purpose + active context (single agent)
- Wave 3: Self-assessment (main thread — lightweight reasoning)
- Wave 4 (if needed): Doubt agent verification
- Wave 5 (if closing): Harvest agent (reads active context, proposes promotions)

### Impact on Skill Design

The SKILL.md instructions must explicitly tell Claude to use Task agents for file operations rather than reading/writing directly. This is a structural requirement, not a suggestion.
