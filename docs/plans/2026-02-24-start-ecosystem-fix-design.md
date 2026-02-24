# Design: /start Skill Ecosystem Fix

**Date**: 2026-02-24
**Status**: Approved
**Soul Purpose**: Fix workflow inconsistencies — single source of truth, composite MCP tools, graceful degradation

---

## Problem Statement

The /start skill ecosystem has 15 identified issues causing "says one thing, does another" behavior:
- 3 diverged SKILL.md copies (deployed vs repo root vs repo skills)
- 8 sequential MCP calls per /start (400-600ms unnecessary overhead)
- custom.md contradicts SKILL.md on service fallback behavior
- No graceful degradation for external services
- Dead `/ralph-go` references (Soul Loop plugin exists but wasn't referenced correctly)

## Design

### Change 1: Single Source of Truth (DONE)

- `skills/start/SKILL.md` in repo = source of truth
- `~/.claude/skills/start/SKILL.md` = deployment artifact (install script copies)
- Root `SKILL.md` deleted (was redundant third copy)

### Change 2: Composite MCP Tools

Reduce 8 sequential calls to 3 by combining deterministic operations that always run together.

**New composite tools (add alongside existing granular tools):**

| Tool | Combines | When Used |
|------|----------|-----------|
| `session_start(project_dir, directive)` | preflight + validate + read_context + git_summary + classify_brainstorm + check_clutter | First call in /start |
| `session_activate(project_dir, soul_purpose)` | archive + hook_activate + features_read | After soul purpose is decided |
| `session_stop(project_dir, harvest)` | harvest + features_read + hook_deactivate | Settlement flow |

**Kept separate (must run between composites):**
- `session_cache_governance` / `session_restore_governance` — /init runs between them
- `session_init` — only runs in init mode, not reconcile
- `session_ensure_governance` — only runs in init mode

**Flow comparison:**

Before (8 calls):
```
preflight → validate → cache_governance → read_context → git_summary → restore_governance → archive → hook_activate
```

After (3-4 calls):
```
session_start → cache_governance → (/init runs) → restore_governance → session_activate
```

**Implementation notes:**
- FastMCP 2.14.5 — `dict` return type works, no json.dumps wrapper needed
- Each sub-operation result nested under its key in the response dict
- Partial failure handling: each sub-result has its own status field
- Granular tools kept for backward compatibility and exploratory use

### Change 3: custom.md Cleanup

Strip to user preferences only. Remove all workflow overrides that duplicate or contradict SKILL.md.

**Keep:** tone preferences, doubt-before-settlement, CI/CD gap surfacing
**Remove:** MCP check overrides, AtlasCoin handling contradictions, research mandates

### Change 4: Graceful Degradation Policy

Add to SKILL.md after Hard Invariants:

```markdown
## Service Availability

NEVER block on external services. Fallback hierarchy:

| Service | If Unavailable | Action |
|---------|---------------|--------|
| atlas-session MCP | Tool call errors | STOP (required) |
| AtlasCoin | contract_health fails | Continue without bounty |
| Perplexity | Research fails | Context7 + WebSearch fallback |
| Context7 | Doc queries fail | Perplexity only |
| Bitwarden | Vault locked | Tell user, skip credential fetch |
```

### Change 5: MEMORY.md + SKILL.md Updates

- Remove stale `/ralph-go` references from MEMORY.md
- Update SKILL.md to reference Soul Loop plugin correctly
- Add service availability section to SKILL.md

---

## Implementation Plan

### Wave 1: Composite Tools (parallel agents)
- **Agent A**: Add `session_start()` composite to operations.py + tools.py
- **Agent B**: Add `session_activate()` composite to operations.py + tools.py
- **Agent C**: Add `session_stop()` composite to operations.py + tools.py

### Wave 2: Skill + Config Updates (parallel agents)
- **Agent D**: Update SKILL.md — service availability section, update call sequences to use composites
- **Agent E**: Clean custom.md, update MEMORY.md
- **Agent F**: Add tests for composite tools

### Wave 3: Validation
- Run full test suite
- Verify composite tools return correct combined results
- Test graceful degradation (simulate service failures)
