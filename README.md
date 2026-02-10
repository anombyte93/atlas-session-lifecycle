# Claude Session Init — `/start` Skill for Claude Code

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/anombyte93/claude-session-init/blob/main/LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-8A2BE2)](https://claude.ai/code)

Persistent project memory and lifecycle management for Claude Code. Run `/start` in any directory to bootstrap structured session context, organize files, and manage soul purpose lifecycle across sessions.

---

## What This Solves

Claude Code has no persistent memory between sessions. Every time you start a new conversation, Claude starts from zero. This creates three problems:

1. **No persistent memory** -- You re-explain context, decisions, and progress every session. Claude forgets what you were working on, why you made architectural choices, and what problems you already solved.

2. **Project sprawl** -- Files accumulate at the project root with no organization. Scripts, docs, configs, and logs pile up. New sessions dump more files. The codebase becomes harder to navigate for both you and Claude.

3. **No lifecycle management** -- Projects have goals, but there is no mechanism to track progress toward those goals, verify completion, or transition to new objectives. You manually manage "what is done" and "what is next" in your head.

`/start` solves all three by creating a structured `session-context/` directory with five memory files, auto-organizing project files into clean directory structures, and providing a soul purpose lifecycle with completion verification and context harvesting.

---

## What Changed in v2

**FIXED: Skill file structure** -- Was a flat `.md` file (`skills/start.md`), now uses the correct directory structure (`skills/start/SKILL.md`). Claude Code discovers skills by scanning `<name>/SKILL.md` directories. The old flat file was invisible to skill discovery, making `/start` uninvocable.

**FIXED: Frontmatter** -- Removed invalid fields (`type`, `version`, `triggers`) that are not part of the Claude Code skill spec and were silently ignored. Added the correct fields (`name`, `description`, `user-invocable`) per the Claude Code skill specification.

**FIXED: install.sh** -- Now creates the correct directory structure (`mkdir -p skills/start/` and copies to `SKILL.md`). Also cleans up old flat files from previous installs.

**NEW: Reconcile Mode** -- Lifecycle management for returning to existing projects. Auto-detects whether this is a first run (Init Mode) or a return visit (Reconcile Mode) based on whether `session-context/` exists. Reconcile Mode assesses soul purpose progress, optionally verifies with a doubt agent, and harvests durable knowledge from active context on closure.

**NEW: Agent-driven execution** -- Delegates heavy file operations to Task agents to prevent context death spirals. The main conversation acts as a thin orchestrator. This prevents the compact-reread-compact loop that kills long sessions.

**NEW: Claude `/init` integration** -- Layers governance sections (structure maintenance rules, session context references, immutable template rules, Ralph Loop config) on top of Claude's built-in `/init` output. Defensive caching ensures governance sections survive `/init` regeneration.

**NEW: Ralph Loop onboarding** -- Configurable autonomous execution loop that works toward your soul purpose, checking its own work with doubt agents. Three modes: automatic (launches every `/start`), manual (invoke yourself), or skip.

---

## How It Works

`/start` has two modes, auto-detected from directory state:

### Init Mode (first run)

Triggered when `session-context/` does not exist.

1. Captures your project's soul purpose
2. Detects environment (git, existing files, structure)
3. Bootstraps `session-context/` with 5 memory bank files from templates
4. Scans root-level files and proposes an organization map (scripts, docs, config, logs)
5. Generates or updates `CLAUDE.md` with project structure and governance sections
6. Runs Claude's built-in `/init` to enrich `CLAUDE.md` with codebase analysis
7. Onboards Ralph Loop (automatic, manual, or skip)
8. Seeds active context so the first Reconcile run finds meaningful state

### Reconcile Mode (returning)

Triggered when `session-context/` already exists.

1. Runs Claude's `/init` to refresh `CLAUDE.md` from current codebase state
2. Restores governance sections if `/init` overwrote them
3. Reads soul purpose and active context
4. Self-assesses soul purpose status (clearly incomplete, probably complete, uncertain)
5. Optionally runs doubt agent verification (user chooses)
6. Offers lifecycle decision: close, continue, or redefine soul purpose
7. Harvests durable knowledge from active context on closure (promotes decisions, patterns, troubleshooting entries)
8. Checks Ralph Loop preference and acts accordingly

---

## Target User

AI-first developers, solopreneurs, and consultants who use Claude Code as their primary development tool and want structured project memory that persists across sessions. If you find yourself re-explaining context to Claude every session, or your project roots are a mess of unsorted files, this skill is for you.

---

## Use Cases

1. **New project bootstrap** -- `/start` on a fresh directory captures your soul purpose, organizes existing files into a clean structure, and generates `CLAUDE.md` with project-specific instructions.

2. **Session continuity** -- `/start` on returning to a project reconciles state, checks soul purpose progress, and loads all context so Claude picks up where it left off.

3. **Project lifecycle** -- Close completed soul purposes, harvest durable knowledge (decisions, patterns, troubleshooting) into permanent files, and redefine new objectives.

4. **Multi-project management** -- Each project gets its own `session-context/` with a consistent five-file structure. Switch between projects and Claude immediately has the right context.

---

## User Stories

- *"As a solo developer, I want Claude to remember what I was working on across sessions so I don't waste time re-explaining context."*

- *"As a consultant managing multiple client projects, I want each project to have a consistent memory structure so Claude can pick up where it left off."*

- *"As someone who accumulates files at the project root, I want an automated organizer that categorizes scripts, docs, and configs into a clean structure."*

- *"As a power user of Claude Code, I want lifecycle management for my project goals so I can track completion, verify with doubt agents, and transition to new objectives."*

---

## Installation

```bash
git clone https://github.com/anombyte93/claude-session-init.git
cd claude-session-init
./install.sh
```

This installs:
- The skill to `~/.claude/skills/start/SKILL.md`
- Templates to `~/claude-session-init-templates/`

### Manual Install

```bash
# Create the skill directory (Claude Code requires <name>/SKILL.md structure)
mkdir -p ~/.claude/skills/start

# Copy skill file
cp start.md ~/.claude/skills/start/SKILL.md

# Copy templates
mkdir -p ~/claude-session-init-templates
cp templates/* ~/claude-session-init-templates/
```

---

## Quick Start

In any project directory with Claude Code:

```
/start
```

That is all. The skill auto-detects whether to initialize or reconcile.

---

## Requirements

- [Claude Code](https://claude.ai/code) CLI
- Templates at `~/claude-session-init-templates/` (installed by `install.sh`)
- Git (optional, but recommended -- enables `git mv` for tracked files)

---

## License

MIT
