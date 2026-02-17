# PRD: Session Lifecycle Hooks + Zai Integration + PR Automation

**Author:** Atlas AI
**Date:** 2026-02-17
**Status:** Draft
**Version:** 1.0
**Taskmaster Optimized:** Yes

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Goals & Success Metrics](#goals--success-metrics)
4. [User Stories](#user-stories)
5. [Functional Requirements](#functional-requirements)
6. [Non-Functional Requirements](#non-functional-requirements)
7. [Technical Considerations](#technical-considerations)
8. [Implementation Roadmap](#implementation-roadmap)
9. [Out of Scope](#out-of-scope)
10. [Open Questions & Risks](#open-questions--risks)
11. [Validation Checkpoints](#validation-checkpoints)
12. [Appendix: Task Breakdown Hints](#appendix-task-breakdown-hints)

---

## Executive Summary

The `/start` skill's session context (soul purpose, active context, decisions, patterns) is lost every time Claude's context compacts or a new session begins, requiring manual `/start` invocations to recover. We're implementing automatic lifecycle hooks (SessionStart, Stop, PreCompact) that re-inject session context at key events, Zai MCP integration to delegate expensive operations to cheap GLM agents (~90% cost reduction), and PR automation baked into the settlement flow so closing a soul purpose automatically creates a pull request. This transforms `/start` from a manual bootstrapper into an always-on session lifecycle system.

---

## Problem Statement

### Current Situation

The `/start` skill works but has three critical gaps:

1. **Context amnesia**: When Claude's context compacts (frequent in long sessions), all session state is lost. The user must manually run `/start` again to recover. Between compactions, Claude forgets the soul purpose, active tasks, and session decisions.

2. **Expensive operations**: Brainstorming, coding, and research tasks run on Claude Max (Opus/Sonnet), costing ~$0.05-0.15 per operation. The Zai MCP server exists with cheap GLM agents (~10x cheaper) but isn't integrated.

3. **Manual PR workflow**: When a soul purpose is completed, the user must manually create a PR. This should be automatic — closing a purpose should trigger branch push + PR creation.

### User Impact
- **Who is affected:** Developers using Claude Code with the /start skill
- **How they're affected:** Lost context mid-session, expensive token usage, manual PR ceremony
- **Severity:** High — context loss causes repeated work, cost adds up, PR friction breaks flow

### Business Impact
- **Cost of problem:** ~70-80% unnecessary Claude Max token usage on operations that could use cheap models
- **Opportunity cost:** Every manual `/start` re-invocation costs 2-3 minutes and burns tokens re-reading files
- **Strategic importance:** Makes the session lifecycle system production-quality and sellable

### Why Solve This Now?
- Phase 1 (MCP-first rewrite) is complete — the plumbing exists
- Zai MCP server is built and working
- Claude Code hooks system is mature and well-documented
- Existing design doc covers the hooks architecture (docs/plans/2026-02-13-session-hooks-implementation.md)

---

## Goals & Success Metrics

### Goal 1: Automatic Context Survival
- **Description:** Session context (soul purpose, active context, decisions) automatically re-injected into Claude's memory at SessionStart and PreCompact events
- **Metric:** Number of manual `/start` invocations needed per session
- **Baseline:** 2-3 per long session (after each compaction)
- **Target:** 0-1 per session (only initial invocation)
- **Measurement Method:** Count `/start` invocations in session transcripts

### Goal 2: Cost Reduction via Zai Delegation
- **Description:** Expensive brainstorming and coding operations delegated to cheap Zai GLM agents
- **Metric:** Claude Max token usage for delegatable operations
- **Baseline:** 100% of operations use Claude Max
- **Target:** <30% of operations use Claude Max (only decisions and user interaction)
- **Measurement Method:** Compare Zai agent spawns vs direct Claude operations

### Goal 3: Zero-Friction PR Creation
- **Description:** Closing a soul purpose via settlement flow automatically creates a PR
- **Metric:** Manual steps required to create PR after soul purpose completion
- **Baseline:** 5-7 manual steps (push, create PR, write description, etc.)
- **Target:** 0 manual steps (automatic on settlement)
- **Measurement Method:** Settlement flow includes PR creation

---

## User Stories

### Story 1: Automatic Context Recovery on Session Start

**As a** developer starting a new Claude Code session,
**I want** my session context (soul purpose, active tasks, decisions) automatically loaded,
**So that** Claude immediately knows what I'm working on without me running `/start`.

**Acceptance Criteria:**
- [ ] SessionStart hook fires automatically when Claude Code session begins
- [ ] Hook reads session-context files and injects summary as systemMessage
- [ ] Claude sees soul purpose, open tasks, and recent progress in its context
- [ ] Hook completes in <2 seconds (no perceptible delay)
- [ ] Hook exits gracefully if session-context/ doesn't exist (no errors)
- [ ] `/start` still works as manual invocation for full lifecycle operations

**Task Breakdown Hint:**
- Task 1: Add hook-session-start subcommand to session-init.py (~3h)
- Task 2: Create session-hooks.sh shell wrapper (~2h)
- Task 3: Register SessionStart hook in settings.local.json (~1h)
- Task 4: Test SessionStart hook end-to-end (~2h)

**Dependencies:** None (can start immediately)

### Story 2: Context Survival Through Compaction

**As a** developer in a long Claude Code session,
**I want** my soul purpose and active context to survive context compaction,
**So that** Claude doesn't forget what we're working on mid-session.

**Acceptance Criteria:**
- [ ] PreCompact hook fires before Claude compresses context
- [ ] Hook re-injects soul purpose + open task count + recent progress as systemMessage
- [ ] After compaction, Claude retains awareness of current soul purpose
- [ ] Hook completes in <1 second
- [ ] Hook handles missing session-context/ gracefully

**Task Breakdown Hint:**
- Task 5: Add hook-pre-compact subcommand to session-init.py (~2h)
- Task 6: Register PreCompact hook in settings.local.json (~1h)
- Task 7: Test PreCompact hook with forced compaction (~2h)

**Dependencies:** Story 1 (shell wrapper from Task 2)

### Story 3: Soul Purpose Enforcement on Stop

**As a** developer ending a Claude Code session,
**I want** Claude to remind me about unfinished soul purpose before closing,
**So that** I don't accidentally abandon work in progress.

**Acceptance Criteria:**
- [ ] Stop hook fires when user ends session
- [ ] If active soul purpose exists and no completion signal found, hook blocks stop
- [ ] Hook presents reminder: "Soul purpose '[X]' is still active. Close anyway?"
- [ ] User can override (force close) or continue working
- [ ] If soul purpose is complete (settlement done), stop proceeds normally
- [ ] Hook checks for `<soul-complete>` tags in transcript

**Task Breakdown Hint:**
- Task 8: Add hook-stop subcommand to session-init.py (~3h)
- Task 9: Add hook-activate/hook-deactivate state management (~2h)
- Task 10: Register Stop hook in settings.local.json (~1h)
- Task 11: Test Stop hook blocking and override (~2h)

**Dependencies:** Story 1 (shell wrapper from Task 2)

### Story 4: Zai Agent Delegation for Brainstorming

**As a** developer using `/start` for brainstorming,
**I want** brainstorming delegated to cheap Zai agents when available,
**So that** I save ~90% on Claude Max token costs for brainstorming.

**Acceptance Criteria:**
- [ ] SKILL.md checks if Zai MCP tools are available at runtime
- [ ] For standard/full brainstorms: spawns Zai agent with brainstorm context
- [ ] For lightweight brainstorms: main Claude handles directly (cheap enough)
- [ ] If Zai unavailable: falls back to superpowers:brainstorming skill
- [ ] Zai brainstorm output presented to user for refinement
- [ ] Main Claude makes final judgment on soul purpose

**Task Breakdown Hint:**
- Task 12: Add Zai detection logic to SKILL.md (~1h)
- Task 13: Implement Zai brainstorm delegation pattern in SKILL.md (~3h)
- Task 14: Test Zai brainstorm with live Zai MCP server (~2h)
- Task 15: Test fallback when Zai unavailable (~1h)

**Dependencies:** None (can run parallel to hooks work)

### Story 5: Zai Agent Delegation for Implementation Work

**As a** developer with implementation tasks from PRD/TaskMaster,
**I want** coding work delegated to cheap Zai agents in isolated worktrees,
**So that** I save costs and get parallel execution with safe isolation.

**Acceptance Criteria:**
- [ ] When Zai available: implementation tasks spawn Zai agents instead of Claude Task agents
- [ ] Each Zai agent runs in worktree isolation (safe git branches)
- [ ] Main Claude monitors status and reviews diffs before accepting
- [ ] If Zai unavailable: falls back to Claude Agent Teams pattern
- [ ] File ownership prevents conflicts between parallel Zai agents

**Task Breakdown Hint:**
- Task 16: Update Work Execution section in SKILL.md for Zai pattern (~3h)
- Task 17: Test Zai implementation delegation with real task (~3h)
- Task 18: Test fallback to Claude Agent Teams when Zai unavailable (~1h)

**Dependencies:** Story 4 (Zai detection from Task 12)

### Story 6: Automatic PR on Settlement

**As a** developer closing a soul purpose,
**I want** a PR automatically created from my feature branch to main,
**So that** I don't need to manually push and create PRs.

**Acceptance Criteria:**
- [ ] Settlement flow checks if on a feature branch (not main)
- [ ] Pushes current branch to remote with -u flag
- [ ] Creates PR via `gh pr create` with auto-generated title and body
- [ ] PR body includes: soul purpose, commits summary, features verified count
- [ ] If already on main or no remote: skips PR creation with notification
- [ ] User can skip PR creation if they prefer

**Task Breakdown Hint:**
- Task 19: Add PR creation step to Settlement Flow in SKILL.md (~3h)
- Task 20: Test PR creation with real branch and gh CLI (~2h)
- Task 21: Test edge cases (already on main, no remote, existing PR) (~1h)

**Dependencies:** None (can run parallel to hooks and Zai)

---

## Functional Requirements

### Must Have (P0) - Critical for Launch

#### REQ-001: SessionStart Hook
**Description:** Claude Code hook that fires on session start, reads session-context files, and injects summary into Claude's context via systemMessage.

**Acceptance Criteria:**
- [ ] `session-init.py hook-session-start` reads soul purpose + active context
- [ ] Returns JSON with `systemMessage` containing session summary
- [ ] Completes in <2 seconds
- [ ] Exits 0 on all error paths (never blocks session start)
- [ ] Handles missing session-context/ directory

**Technical Specification:**
```python
# session-init.py hook-session-start subcommand
# Input: project_dir from hook stdin JSON
# Output: {"decision": "approve", "systemMessage": "Session context: ..."}
```

**Dependencies:** None

#### REQ-002: PreCompact Hook
**Description:** Hook that fires before context compaction, re-injecting soul purpose and task state so it survives compression.

**Acceptance Criteria:**
- [ ] `session-init.py hook-pre-compact` extracts soul purpose + open task count
- [ ] Returns JSON with `systemMessage` for context re-injection
- [ ] Completes in <1 second
- [ ] Only injects if soul purpose is active (not "(No active soul purpose)")

**Dependencies:** REQ-001 (shared shell wrapper)

#### REQ-003: Stop Hook with Soul Purpose Enforcement
**Description:** Hook that fires on session stop, blocking if active soul purpose exists without completion signal.

**Acceptance Criteria:**
- [ ] `session-init.py hook-stop` checks for active soul purpose
- [ ] Checks transcript for `<soul-complete>` tags
- [ ] If purpose active and no completion: returns `{"decision": "block", "reason": "..."}`
- [ ] If purpose complete or no purpose: returns `{"decision": "approve"}`
- [ ] Checks `stop_hook_active` to prevent infinite loops
- [ ] State managed via `.claude/session-lifecycle.local.md`

**Dependencies:** REQ-001 (shared shell wrapper), REQ-004 (state management)

#### REQ-004: Hook State Management (activate/deactivate)
**Description:** Subcommands to toggle Stop hook enforcement via state file.

**Acceptance Criteria:**
- [ ] `hook-activate --soul-purpose "X"` creates `.claude/session-lifecycle.local.md`
- [ ] `hook-deactivate` removes the state file
- [ ] State file contains: active flag, soul purpose, started_at timestamp
- [ ] `/start` calls activate after brainstorm; settlement calls deactivate

**Dependencies:** None

#### REQ-005: Shell Wrapper Script
**Description:** Single `session-hooks.sh` that routes hook events to Python subcommands.

**Acceptance Criteria:**
- [ ] Receives event type as $1, reads stdin for hook JSON
- [ ] Routes: session-start → hook-session-start, stop → hook-stop, pre-compact → hook-pre-compact
- [ ] Exits 0 on all error paths
- [ ] Sources project_dir from hook input JSON or falls back to $PWD

**Dependencies:** REQ-001, REQ-002, REQ-003

#### REQ-006: Hook Registration
**Description:** Register all three hooks in `~/.claude/settings.local.json`.

**Acceptance Criteria:**
- [ ] SessionStart hook registered with 5-second timeout
- [ ] Stop hook registered with 10-second timeout
- [ ] PreCompact hook registered with 3-second timeout
- [ ] Existing hooks preserved (auto-enroll-guardian.sh, bw-auto-unlock.sh)

**Dependencies:** REQ-005

### Should Have (P1) - Important but Not Blocking

#### REQ-007: Zai MCP Brainstorm Delegation
**Description:** Detect Zai MCP availability and delegate standard/full brainstorms to cheap Zai agents.

**Acceptance Criteria:**
- [ ] SKILL.md checks for `mcp__zaiMCP__zai_spawn_agent` tool at runtime
- [ ] Standard/full brainstorms spawn Zai agent with shared isolation
- [ ] Lightweight brainstorms handled by main Claude directly
- [ ] Fallback to superpowers:brainstorming if Zai unavailable
- [ ] Zai agent output presented for user refinement

**Dependencies:** None (parallel work)

#### REQ-008: Zai MCP Work Delegation
**Description:** Replace Claude Agent Teams with Zai agent spawns for implementation work.

**Acceptance Criteria:**
- [ ] Implementation tasks spawn Zai agents with worktree isolation
- [ ] Main Claude monitors via zai_agent_status and reviews diffs
- [ ] Falls back to Claude Agent Teams if Zai unavailable
- [ ] File ownership enforced naturally via worktree isolation

**Dependencies:** REQ-007 (Zai detection logic)

#### REQ-009: PR Automation in Settlement
**Description:** Settlement flow automatically creates PR when closing a soul purpose.

**Acceptance Criteria:**
- [ ] Checks if on feature branch (not main/master)
- [ ] Pushes branch to remote
- [ ] Creates PR via `gh pr create` with structured body
- [ ] PR body includes soul purpose, commit summary, feature count
- [ ] Skips gracefully if on main, no remote, or PR exists
- [ ] User can skip PR creation

**Dependencies:** None (parallel work)

### Nice to Have (P2) - Future Enhancement

#### REQ-010: SKILL.md Slimming
**Description:** Refactor SKILL.md to remove manual script calls now handled by hooks.

**Dependencies:** REQ-001 through REQ-006

#### REQ-011: Zai Research Delegation
**Description:** Delegate research tasks to Zai agents with shared isolation.

**Dependencies:** REQ-007

---

## Non-Functional Requirements

### Performance
- SessionStart hook: <2 seconds
- PreCompact hook: <1 second
- Stop hook: <5 seconds (includes transcript scan)
- Zai agent spawn: <3 seconds for response (agent runs async)

### Reliability
- All hooks exit 0 on error (never block session)
- Zai unavailable: graceful fallback to current behavior
- PR creation fails: notify user, don't block settlement

### Security
- Hook scripts don't read or transmit credentials
- Zai agents receive only task description (no secrets)
- PR automation uses existing `gh` authentication

### Compatibility
- Works with Claude Code's hook system (14 event types)
- Preserves existing hooks (guardian, bitwarden)
- Zai integration optional (works without it)

---

## Technical Considerations

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Session                       │
│                                                              │
│  SessionStart  ──→  session-hooks.sh  ──→  session-init.py  │
│  PreCompact    ──→  session-hooks.sh  ──→  session-init.py  │
│  Stop          ──→  session-hooks.sh  ──→  session-init.py  │
│                                                              │
│  /start skill  ──→  atlas-session MCP ──→  session context  │
│                ──→  Zai MCP (optional) ──→  cheap agents    │
│                                                              │
│  Settlement    ──→  gh pr create      ──→  GitHub PR        │
└─────────────────────────────────────────────────────────────┘
```

**Key principle:** Hooks handle automatic plumbing (deterministic). /start skill handles judgment (AI decisions). Zai handles cheap work. Main Claude handles expensive decisions only.

### Key Files

| File | Purpose |
|------|---------|
| `~/.claude/skills/start/SKILL.md` | Skill definition (deployed) |
| `~/.claude/skills/start/session-init.py` | Python script for deterministic operations |
| `~/.claude/hooks/session-hooks.sh` | Shell wrapper for all lifecycle hooks |
| `~/.claude/settings.local.json` | Hook registration |
| `.claude/session-lifecycle.local.md` | Stop hook state file (per-project) |
| `session-context/*.md` | Session context files (per-project) |

### Hook Protocol

**Input (stdin JSON):**
```json
{
  "session_id": "abc-123",
  "project_dir": "/path/to/project",
  "event": "SessionStart"
}
```

**Output (stdout JSON):**
```json
{
  "decision": "approve",
  "systemMessage": "Session context: Soul purpose is 'Build feature X'. 3 tasks open, 2 completed."
}
```

**Blocking output (Stop hook):**
```json
{
  "decision": "block",
  "reason": "Soul purpose 'Build feature X' is still active. Complete or close it first."
}
```

---

## Implementation Roadmap

### Phase 1: Hook Infrastructure (Tasks 1-6)
**Goal:** Working SessionStart, Stop, PreCompact hooks

### Phase 2: Zai Integration (Tasks 7-10)
**Goal:** Brainstorm + implementation delegation to Zai agents

### Phase 3: PR Automation (Tasks 11-12)
**Goal:** Automatic PR creation on settlement

### Phase 4: Integration + Polish (Tasks 13-15)
**Goal:** End-to-end testing, SKILL.md updates, PR creation

---

## Out of Scope

1. **Phase 3 (Interactive installer wizard)** — separate follow-up PR
2. **Phase 4 (Co-pilot personality)** — separate follow-up PR
3. **AtlasCoin bounty changes** — existing bounty system works as-is
4. **Hook-based Ralph Loop** — Ralph Loop continues to use Skill tool invocation
5. **Multi-project session switching** — single project per session

---

## Open Questions & Risks

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Hook timeout in large projects | Medium | Low | Set generous timeouts, optimize Python reads |
| Zai MCP not running | High | Low | Graceful fallback to current behavior |
| Stop hook annoys users | Medium | Medium | Clear messaging, easy override, deactivate option |
| PR creation fails | Low | Low | Notify user, don't block settlement |
| Context injection too verbose | Medium | Medium | Keep systemMessage <500 chars, summary only |

---

## Validation Checkpoints

### Checkpoint 1: After Hook Infrastructure
- [ ] SessionStart hook injects context on new session
- [ ] PreCompact hook preserves soul purpose through compaction
- [ ] Stop hook blocks with active soul purpose
- [ ] All hooks exit gracefully on errors

### Checkpoint 2: After Zai Integration
- [ ] Zai brainstorm produces usable output
- [ ] Fallback works when Zai unavailable
- [ ] Cost reduction measurable

### Checkpoint 3: After PR Automation
- [ ] Settlement creates PR automatically
- [ ] PR body is well-structured
- [ ] Edge cases handled (on main, no remote)

---

## Appendix: Task Breakdown Hints

### Hook Infrastructure (6 tasks, ~14h)
1. Add hook-session-start to session-init.py (3h)
2. Add hook-pre-compact to session-init.py (2h)
3. Add hook-stop to session-init.py (3h)
4. Add hook-activate/hook-deactivate to session-init.py (2h)
5. Create session-hooks.sh shell wrapper (2h)
6. Register hooks in settings.local.json (2h)

### Zai Integration (4 tasks, ~8h)
7. Add Zai detection to SKILL.md (1h)
8. Implement Zai brainstorm delegation in SKILL.md (3h)
9. Update Work Execution section for Zai pattern in SKILL.md (3h)
10. Test Zai integration + fallback (1h)

### PR Automation (2 tasks, ~5h)
11. Add PR creation step to Settlement Flow in SKILL.md (3h)
12. Test PR creation with real branch (2h)

### Integration + Polish (3 tasks, ~5h)
13. Update SKILL.md to integrate hooks (remove redundant manual calls) (2h)
14. Sync repo SKILL.md with deployed version (1h)
15. Create PR from feature/mcp-zai-architecture to main (2h)

### Parallelizable Tasks
- Tasks 1-4 (Python subcommands) can run in parallel
- Tasks 7-9 (Zai SKILL.md changes) can run parallel to hooks
- Tasks 11-12 (PR automation) can run parallel to hooks and Zai
- Tasks 5-6 (wrapper + registration) depend on Tasks 1-4
- Tasks 13-15 (integration) depend on all prior tasks

**Total: 15 tasks, ~32 hours estimated**
**Critical path: Tasks 1-4 → 5-6 → 13 → 14 → 15**
