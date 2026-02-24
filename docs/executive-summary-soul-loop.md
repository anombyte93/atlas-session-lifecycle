# Soul Loop Plugin - Executive Summary

**Date**: 2026-02-21
**Author**: AI Engineering Team
**Status**: Implementation Complete, All Tests Passing
**Decision Required**: Approve for production / Request changes / Scrap

---

## Executive Summary

The Soul Loop Plugin implements **hierarchical backpressure gates** for AI-assisted development. It prevents the AI from entering infinite loops while maintaining flexibility for iterative development.

**Bottom Line Up Front (BLUF)**: A lightweight guardrail system that enforces quality constraints without breaking legitimate iteration workflows. Ready for production use.

---

## Problem Statement

When using AI for iterative development (e.g., "Fix this bug", "Refactor this module"), the AI can:

1. **Loop infinitely** without completing the task
2. **Claim completion** without verifying tests pass
3. **Generate low-quality output** without feedback mechanisms
4. **Lose track** of iteration depth and progress

Existing solutions (Ralph Loop) enable iteration but lack **quality gates**—they loop self-referentially without checking if the work is actually improving.

---

## Solution: Hierarchical Gate System

Soul Loop wraps AI iterations in a **deterministic constraint system**:

```
Critical (Hard Block) → Quality (Soft Warning) → Progressive (Friction) → Agentic (Allow Exit)
```

### Gate Hierarchy

| Priority | Gate | Type | Action | Example |
|----------|------|------|--------|---------|
| **Critical** | Max iterations reached | HARD BLOCK | Stop immediately | "3 iterations reached, exiting" |
| **Critical** | 10+ consecutive failures | HARD BLOCK | Manual intervention required | "Too many failures, human review needed" |
| **Quality** | Test failures | SOFT WARNING | Continue with warning | "Tests failing, fix before claiming done" |
| **Progressive** | 5+ soft failures | FRICTION | Warn user | "5 failures detected, consider review" |
| **Agentic** | Completion promise matched | ALLOW EXIT | Graceful stop | User outputs `<promise>Done</promise>` |

**Design Rationale**: This follows Geoffrey Huntley's "Engineering Backpressure" principle—deterministic constraints (90%) before agentic freedom (10%).

---

## Architecture

### Plugin Structure

```
~/.claude/plugins/soul-loop/
├── hooks/soul-loop-stop.sh     # Gate enforcement (runs each turn)
├── scripts/setup-soul-loop.sh  # State initialization
├── commands/                   # /soul-loop, /cancel-soul
└── .claude-plugin/plugin.json  # Plugin metadata
```

### State File

```yaml
---
iteration: 2
max_iterations: 20
completion_promise: "All tests passing"
soul_purpose: "Fix authentication bug"
intensity: "medium"
---
# Current progress and context
```

Location: `session-context/soul-loop-state.md` (per-project)

---

## Usage

### Basic Usage

```bash
/soul-loop "Fix authentication bug" --intensity small
```

### Intensity Presets

| Intensity | Max Iterations | Completion Promise | Use Case |
|-----------|----------------|-------------------|----------|
| Small | 5 | "All tests passing" | Quick fixes |
| Medium | 20 | "All tests passing and feature claims verified" | Standard features |
| Long | 100 | "Must validate with 3x doubt agents and 1x finality agent" | Complex systems |

### Completion

User outputs the completion promise to exit early:

```
<promise>All tests passing</promise>
```

The hook detects this tag and allows graceful exit.

---

## Test Results

All 6 test categories **PASSING**:

| Test | Result | Notes |
|------|--------|-------|
| Max iterations gate | ✓ | Stops at configured limit |
| Progressive failure gate | ✓ | Hard stop at 10 failures |
| Progressive warning gate | ✓ | Warning at 5 failures |
| Completion promise detection | ✓ | Exits on promise match |
| No state file handling | ✓ | Clean exit when inactive |
| State corruption recovery | ✓ | Removes and continues |

---

## Integration Points

| Component | Integration | Status |
|-----------|-------------|--------|
| `/start` skill | Auto-invokes based on intensity | ✓ Complete |
| `/stop` skill | Cleans up state files | ✓ Complete |
| Ralph Loop | Compatible (different use case) | ✓ |
| Hookify | May conflict (known, documented) | ⚠️  See docs |

---

## Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Hook conflicts (e.g., hookify) | Low | Documented resolution in README |
| Test flakiness causing false warnings | Low | Soft warnings allow continuation |
| State file corruption | Low | Auto-detect and recover |
| Max iterations too restrictive | Low | User-configurable per invocation |

---

## Recommendation

**APPROVE for production use.**

**Rationale**:
1. Lightweight (< 200 lines of bash)
2. All tests passing
3. Backpressure prevents runaway AI behavior
4. Exit conditions are well-defined
5. Integration with existing workflow is seamless

**Next Steps**:
1. Merge to `main`
2. Document in team wiki
3. Monitor usage patterns for 2 weeks
4. Gather feedback from users

---

## Appendix: Technical Details

### Stop Hook Flow

```
[User input]
    ↓
[Stop hook triggered]
    ↓
[Parse state file]
    ↓
[Critical gates] → Fail? → Hard stop
    ↓ Pass
[Quality gates] → Fail? → Soft warning
    ↓
[Progressive gates] → 5+ failures? → Warning
                      → 10+ failures? → Hard stop
    ↓
[Agentic gate] → Promise matched? → Allow exit
    ↓ No match
[Increment iteration]
    ↓
[Block with feedback] → [AI continues]
```

### Key Design Decisions

1. **Separate plugin from soul-purpose skill**: Enables reusability and independent lifecycle
2. **Soft blocks for quality gates**: Test frameworks can be flaky; allow AI to self-correct
3. **Progressive friction (5→10)**: Balances autonomy with safety
4. **Promise tag for exit**: Human-controlled termination condition

---

**Document**: `docs/executive-summary-soul-loop.md`
**Version**: 1.0
**Reviewed by**: [Pending]
**Approved by**: [Pending]
