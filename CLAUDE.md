# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Project**: Atlas Session Lifecycle — Session management skill for Claude Code
**Goal**: Two-mode session lifecycle manager with soul purpose tracking, context harvesting, and settlement protocol.
**Stack**: Claude Code Skills (Markdown-defined), MCP (atlas-session), Python

### What This Is

A Claude Code skill (`/start`) that manages session lifecycle. Auto-detects mode from directory state:

- **Init Mode** (first run): `session-context/` absent. Captures soul purpose, bootstraps session context, organizes files, generates CLAUDE.md with governance sections, onboards Ralph Loop.
- **Reconcile Mode** (subsequent runs): `session-context/` present. Reads soul purpose + active context, self-assesses completion, presents Close/Continue/Redefine decision, harvests context on closure.

### Key Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Complete skill definition (root copy) |
| `skills/start/SKILL.md` | Skill definition (subdirectory copy, kept in sync) |
| `install.sh` | Interactive installer with wizard |
| `session-init.py` | Python backend for file operations |
| `v1/SKILL.md` | Legacy v1 skill (monolithic) |
| `templates/` | Immutable session-context templates |

### Architecture

**Mode detection**: `session-context/` absent → Init, present → Reconcile.

**MCP-first**: Session operations call `atlas-session` MCP tools directly. No agent team ceremony for state management.

**Optional integrations**: Zai MCP (cost optimization, not yet public) and AtlasCoin (bounty tracking) are documented as optional appendices. The core skill works without either.

### Hard Invariants

1. **User authority is absolute** — AI never closes a soul purpose. Only suggests; user decides.
2. **Zero unsolicited behavior** — Skill only runs when user types `/start`.
3. **Human-visible memory only** — All state lives in files.
4. **Idempotent** — Safe to run multiple times.
5. **Templates are immutable** — Never edit files in `templates/`.

---

## Development

### Installation

```bash
# Skill mode (default)
bash install.sh

# Plugin mode
bash install.sh --plugin

# See all options
bash install.sh --help
```

### Testing

- Run `/start` in a fresh project (Init mode)
- Run `/start` in an existing project (Reconcile mode)
- Verify `bash -n install.sh` passes (syntax check)
- Verify both SKILL.md copies are identical: `diff SKILL.md skills/start/SKILL.md`

---

## Contributing

- Keep both SKILL.md copies in sync (root and `skills/start/`)
- Templates in `templates/` are immutable — never edit them
- Session context files (`session-context/`) are user-generated, not tracked in git
