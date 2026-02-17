# Claude Code Hooks System: Research Summary

**Date**: February 17, 2026
**Researcher**: Claude Code Investigation
**Status**: Complete - Ready for PRD Writing

---

## Executive Summary

The Claude Code hooks system is a mature, well-documented lifecycle automation framework that enables:
- **Deterministic background tasks** at 14 distinct lifecycle points
- **Context preservation** across session compaction
- **Soul purpose enforcement** via Stop hooks with completion signals
- **Quality gates** for agent teams (TeammateIdle, TaskCompleted)
- **Security validation** via PreToolUse hooks
- **Asynchronous background operations** without blocking Claude

The system has been in production since at least 2025, with extensive documentation, examples, and error handling patterns.

---

## Research Questions Answered

### 1. What hook events are available?

**Answer**: 14 lifecycle events supported:

| Session Setup | Agentic Loop | Session Cleanup |
|--------------|--------------|-----------------|
| SessionStart | UserPromptSubmit | PreCompact |
| (none) | PreToolUse | SessionEnd |
| (none) | PermissionRequest | |
| (none) | PostToolUse | |
| (none) | PostToolUseFailure | |
| (none) | Notification | |
| (none) | SubagentStart | |
| (none) | SubagentStop | |
| (none) | Stop | |
| (none) | TeammateIdle | |
| (none) | TaskCompleted | |

**Key insight**: SessionStart is async/informational. Stop is the only blocking event in the response phase, making it ideal for soul purpose enforcement.

---

### 2. What is the hook protocol?

**Answer**: JSON-based request/response over stdin/stdout.

**Input**: Hook receives JSON via stdin with:
- **Common fields** (all events): `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`
- **Event-specific fields**: Varies by event (e.g., `tool_name`, `tool_input` for PreToolUse)

**Output**: Hook returns JSON via stdout (exit 0) with:
- **Universal fields**: `continue`, `stopReason`, `suppressOutput`, `systemMessage`
- **Event-specific fields**: Varies by event

**Example Input** (PreToolUse):
```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/home/user/project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": { "command": "npm test" },
  "tool_use_id": "toolu_01ABC..."
}
```

**Example Output** (blocking decision):
```json
{
  "decision": "block",
  "reason": "Soul purpose incomplete: Build widget with 3 features"
}
```

---

### 3. How do hooks return systemMessage content to inject into Claude's context?

**Answer**: Three strategies:

1. **`additionalContext` field** (JSON):
   - Added discretely without showing hook output
   - Available on: SessionStart, UserPromptSubmit, SubagentStart, PostToolUse, PostToolUseFailure, Stop, SubagentStop, PreCompact
   - Best for: Quiet context injection

2. **`systemMessage` field** (JSON):
   - Shown as warning message to user
   - Available on: All hooks
   - Best for: Important alerts

3. **Plain stdout** (SessionStart, UserPromptSubmit only):
   - Shown as hook output in transcript
   - Must be non-JSON text
   - Best for: Verbose diagnostic output

**Critical for soul purpose**: Use `additionalContext` in SessionStart to restore soul purpose silently, and `systemMessage` in Stop hook to alert user about incomplete work.

---

### 4. How are hooks registered in settings.local.json?

**Answer**: Three-level nested JSON structure:

```json
{
  "hooks": {
    "EVENT_NAME": [
      {
        "matcher": "filter_pattern_or_empty",
        "hooks": [
          {
            "type": "command|prompt|agent",
            "command": "script_path_or_prompt",
            "timeout": 600,
            "statusMessage": "Spinner text",
            "async": false
          }
        ]
      }
    ]
  }
}
```

**Nesting levels**:
1. **Top-level key**: Event name (SessionStart, Stop, etc.)
2. **Matcher group**: Filter conditions (regex pattern or empty)
3. **Hook handler**: Shell command, LLM prompt, or agent

**Configuration precedence** (highest to lowest):
1. Managed settings (org policy)
2. Command-line args
3. `.claude/settings.local.json` (project-local)
4. `.claude/settings.json` (shared project)
5. `~/.claude/settings.json` (user-global)
6. Plugin hooks
7. Skill/agent frontmatter

**Location strategy**:
- Development/testing: `.claude/settings.local.json`
- Team-wide: `.claude/settings.json`
- All projects: `~/.claude/settings.json`

---

### 5. What's the timeout behavior?

**Answer**: Configurable per hook, 10-minute default for commands.

| Hook type | Default timeout | Behavior on timeout |
|-----------|-----------------|-------------------|
| Command | 600s (10 min) | Non-blocking error (stderr shown only) |
| Prompt | 30s | Treated as "no decision" (allow through) |
| Agent | 60s | Treated as "no decision" (allow through) |
| Async command | 600s | Background process killed silently |

**Configuration**:
```json
{
  "type": "command",
  "command": "script.sh",
  "timeout": 120  // 2 minutes
}
```

**Recommendation for soul purpose**: Set Stop hook timeout to 5-10 seconds max. Long waits break UX.

---

### 6. Can hooks block events? Which events?

**Answer**: Yes, but only specific events can be blocked:

### Blockable Events

| Event | Can block? | Blocking method | Effect |
|-------|-----------|-----------------|--------|
| **SessionStart** | No | N/A | N/A (informational) |
| **UserPromptSubmit** | Yes | `decision: "block"` or exit 2 | Prompt erased, not processed |
| **PreToolUse** | Yes | `permissionDecision: "deny"` or exit 2 | Tool call prevented |
| **PermissionRequest** | Yes | `decision.behavior: "deny"` or exit 2 | Permission denied |
| **PostToolUse** | No | N/A | N/A (tool ran already) |
| **PostToolUseFailure** | No | N/A | N/A |
| **Notification** | No | N/A | N/A |
| **SubagentStart** | No | N/A | N/A |
| **SubagentStop** | Yes | `decision: "block"` or exit 2 | Subagent continues |
| **Stop** | Yes | `decision: "block"` or exit 2 | Claude continues (re-injects reason) |
| **TeammateIdle** | Yes | exit 2 only | Teammate continues (stderr feedback) |
| **TaskCompleted** | Yes | exit 2 only | Task not marked complete |
| **PreCompact** | No | N/A | N/A (informational) |
| **SessionEnd** | No | N/A | N/A (cleanup) |

### Critical: Stop Hook Pattern for Soul Purpose

```bash
#!/bin/bash

HOOK_INPUT=$(cat)
STOP_HOOK_ACTIVE=$(echo "$HOOK_INPUT" | jq -r '.stop_hook_active')

# CRITICAL: Prevent infinite loops
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
  exit 0  # Allow stop, don't block again
fi

# Check soul purpose completion
if [ ! -f ".claude/soul-complete.txt" ]; then
  PURPOSE=$(cat .claude/soul-purpose.txt)
  echo "{\"decision\": \"block\", \"reason\": \"Soul purpose: $PURPOSE\"}"
  exit 0
fi

exit 0  # Soul complete, allow stop
```

**Key safety feature**: `stop_hook_active` field prevents infinite loops. Always check this before blocking Stop events.

---

## Research Findings

### 1. Hooks are Deterministic

Hooks are **not LLM-based by default**. They're shell scripts with JSON I/O. This means:
- No hallucination risk
- Predictable behavior
- Fast execution
- Ideal for system lifecycle management

(Optional: Prompt hooks and agent hooks available for complex decision logic)

### 2. Session Message Injection is Event-Dependent

Different events support different injection methods:
- **SessionStart**: Best for restoring context (supports `additionalContext`)
- **PreCompact**: Can save state before compaction (supports `additionalContext`)
- **Stop**: Can alert user about incomplete work (supports `systemMessage` + `additionalContext`)

**Soul purpose workflow**:
1. SessionStart injects soul purpose silently via `additionalContext`
2. Stop blocks until completion condition met, uses `systemMessage` to show progress

### 3. Exit Codes Control Blocking

| Exit | Behavior | JSON processed? |
|-----|----------|-----------------|
| 0 | Success | Yes |
| 2 | Blocking error | No |
| Other | Non-blocking error | No |

**Critical**: Exit 2 rejects JSON. Use exit 0 + JSON `decision: "block"` for proper decision flow.

### 4. Matcher Patterns are Regex

Matchers use full regex syntax:
- `"Bash"` - exact match
- `Edit|Write` - alternation
- `mcp__.*__write.*` - pattern matching
- `""` or `"*"` - match all

**For soul purpose**: Don't need matcher (or use empty matcher) on SessionStart, Stop, PreCompact.

### 5. Async Hooks Don't Block

Async hooks (`"async": true`) run in background:
- Claude continues immediately
- Results delivered on next turn
- Cannot return blocking decisions
- Useful for: background tests, deployments, logging

**Not suitable for soul purpose enforcement** (need synchronous blocking).

### 6. Special Case: SessionStart Environment

SessionStart hooks have exclusive access to `CLAUDE_ENV_FILE` variable:
- Can persist environment variables across Bash commands
- Write `export VAR=value` to this file
- Other hook events don't have this variable

---

## Integration with Existing /start Skill

### Current State

The `/start` skill (SKILL.md) is a linear bootstrapper that:
1. Runs preflight (detect init vs reconcile)
2. Asks user questions
3. Creates session-context files
4. Calls `/init` to refresh CLAUDE.md
5. Runs brainstorm / reconciliation
6. Creates bounty on AtlasCoin

### Hooks Extension Opportunity

With hooks, the skill can automate:

| Lifecycle point | Hook event | Purpose |
|-----------------|-----------|---------|
| Session resume | SessionStart | Silently restore soul purpose + active context |
| Before stop | Stop | Block if soul purpose incomplete |
| Before compaction | PreCompact | Preserve critical session state |
| Agent team work | TeammateIdle, TaskCompleted | Enforce quality gates |

The skill's `/start` command remains the entry point for user-driven decisions. Hooks handle the background automation.

---

## Decision Log for PRD Writers

### What to document in PRD:

1. **Hook event priorities** for soul purpose:
   - SessionStart (context restoration)
   - Stop (enforcement)
   - PreCompact (state preservation)

2. **Configuration strategy**:
   - Where to place hooks (`.claude/settings.local.json` for dev)
   - How to structure multi-event hooks
   - Timeout recommendations

3. **Soul purpose completion signal**:
   - How Claude indicates completion (e.g., `<soul-complete>PURPOSE</soul-complete>` tags)
   - How Stop hook detects signal in transcript
   - Deactivation logic

4. **Error handling**:
   - JSON validation (test with jq)
   - Timeout expectations
   - Infinite loop prevention

5. **Async operations**:
   - When to use async vs sync
   - How async results are delivered
   - Limitations (no blocking)

6. **Integration points**:
   - How hooks interact with /start skill
   - How hooks work with agent teams
   - How hooks preserve context across compaction

---

## Files Created

1. **CLAUDE_CODE_HOOKS_TECHNICAL_REFERENCE.md** (1,000+ lines)
   - Complete technical specification
   - All 14 events documented
   - Protocol details (JSON, exit codes, matchers)
   - Configuration examples
   - Troubleshooting guide
   - Ready for PRD reference

2. **HOOKS_RESEARCH_SUMMARY.md** (this file)
   - High-level findings
   - Questions answered
   - Decision log for PRD
   - Integration opportunities

---

## Sources

All information verified against official documentation:

- [Claude Code Hooks Reference](https://code.claude.com/docs/en/hooks)
- [Claude Code Settings Guide](https://code.claude.com/docs/en/settings)
- [Claude Code Hooks Guide](https://code.claude.com/docs/en/hooks-guide)
- [Session Hooks Implementation Plan](2026-02-13-session-hooks-implementation.md)

---

## Next Steps

With this research complete, the PRD can now:

1. **Define hook responsibilities** - Which events to implement, which to skip
2. **Specify configuration** - Where hooks live, how they're registered
3. **Document completion criteria** - How to verify hooks work correctly
4. **Plan task breakdown** - Task 1-8 from implementation plan can be refined
5. **Set timeline** - Hooks are well-understood, straightforward to implement

**Estimated implementation effort**: 2-3 working days for all 8 tasks (including tests)
