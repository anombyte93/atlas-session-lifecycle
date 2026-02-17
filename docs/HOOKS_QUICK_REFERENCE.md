# Claude Code Hooks: Quick Reference Card

**For rapid PRD writing and implementation planning**

---

## The 6 Critical Facts

| Fact | Details |
|------|---------|
| **14 events available** | SessionStart, Stop, PreCompact are most relevant for soul purpose |
| **JSON protocol** | stdin/stdout, exit 0 = success, exit 2 = blocking error |
| **Only 6 events can block** | UserPromptSubmit, PreToolUse, PermissionRequest, Stop, SubagentStop, TeammateIdle, TaskCompleted |
| **Stop hook has `stop_hook_active` flag** | MUST check to prevent infinite loops |
| **3 injection strategies** | `additionalContext` (discrete), `systemMessage` (visible), plain stdout |
| **Timeout defaults** | 600s (command), 30s (prompt), 60s (agent) |

---

## The 3 Core Events for Soul Purpose

### 1. SessionStart
```json
{
  "matcher": "startup|resume|compact",
  "hooks": [{
    "type": "command",
    "command": "~/.claude/hooks/session-start.sh",
    "timeout": 5,
    "statusMessage": "Restoring session context"
  }]
}
```

**Output**:
```json
{
  "additionalContext": "Soul purpose: Build the widget | Open tasks: 3"
}
```

**Use**: Silently restore soul purpose and task list on session resume

---

### 2. Stop
```json
{
  "matcher": "",
  "hooks": [{
    "type": "command",
    "command": "~/.claude/hooks/stop-check.sh",
    "timeout": 5
  }]
}
```

**Input**:
```json
{
  "hook_event_name": "Stop",
  "stop_hook_active": false|true
}
```

**Output (blocking)**:
```json
{
  "decision": "block",
  "reason": "Soul purpose incomplete: Build widget (3 features done, 1 remaining)"
}
```

**Output (allow)**:
```
// exit 0 with no JSON
```

**Use**: Prevent Claude from stopping until soul purpose complete. Check `stop_hook_active` to avoid infinite loops.

---

### 3. PreCompact
```json
{
  "matcher": "auto|manual",
  "hooks": [{
    "type": "command",
    "command": "~/.claude/hooks/pre-compact.sh",
    "timeout": 3
  }]
}
```

**Output**:
```json
{
  "systemMessage": "Context about to compress. Soul purpose: Build widget | Active tasks: task-1, task-2"
}
```

**Use**: Preserve critical state before context compaction. Injected content survives compression.

---

## Quick Event Comparison

| Event | Fires when | Can block? | Typical use | Output field |
|-------|-----------|-----------|------------|--------------|
| **SessionStart** | Session begins | No | Restore context | `additionalContext` |
| **UserPromptSubmit** | User submits prompt | Yes | Validate input | `decision: "block"` |
| **PreToolUse** | Before tool runs | Yes | Security checks | `permissionDecision: "deny"` |
| **PermissionRequest** | Before permission dialog | Yes | Auto-approve/deny | `decision.behavior: "deny"` |
| **PostToolUse** | After tool succeeds | No | Log, feedback | `additionalContext` |
| **PostToolUseFailure** | After tool fails | No | Error handling | `additionalContext` |
| **Notification** | Notification sent | No | Route alerts | `additionalContext` |
| **SubagentStart** | Subagent spawned | No | Inject context | `additionalContext` |
| **SubagentStop** | Subagent finishes | Yes | Quality gate | `decision: "block"` |
| **Stop** | Claude finishes | Yes | Enforce completion | `decision: "block"` |
| **TeammateIdle** | Teammate pauses | Yes | Quality gate | exit 2 (stderr) |
| **TaskCompleted** | Task marked done | Yes | Test requirement | exit 2 (stderr) |
| **PreCompact** | Before compression | No | Preserve state | `systemMessage` |
| **SessionEnd** | Session closes | No | Cleanup | (none) |

---

## Stop Hook Pattern (Copy-Paste Template)

```bash
#!/bin/bash
# .claude/hooks/stop-check.sh

HOOK_INPUT=$(cat)

# CRITICAL: Check if Stop hook already active (prevents infinite loops)
STOP_HOOK_ACTIVE=$(echo "$HOOK_INPUT" | jq -r '.stop_hook_active')
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
  # Allow stop, don't block again
  exit 0
fi

# Check completion condition
SOUL_PURPOSE=""
if [ -f ".claude/soul-purpose.txt" ]; then
  SOUL_PURPOSE=$(cat .claude/soul-purpose.txt)
fi

# Example: Check if soul purpose file exists and is complete
if [ -z "$SOUL_PURPOSE" ] || [ ! -f ".claude/soul-complete.txt" ]; then
  # Block stop, tell Claude why
  echo "{
    \"decision\": \"block\",
    \"reason\": \"Soul purpose not complete: $SOUL_PURPOSE\"
  }"
  exit 0
fi

# Soul purpose complete, allow stop
exit 0
```

---

## Configuration File Template

**.claude/settings.local.json**:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|compact",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/session-start.sh",
            "timeout": 5,
            "statusMessage": "Restoring session context"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/stop-check.sh",
            "timeout": 5
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "auto|manual",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/pre-compact.sh",
            "timeout": 3,
            "statusMessage": "Preserving session context"
          }
        ]
      }
    ]
  }
}
```

---

## JSON Exit Code Decision Matrix

| Situation | Exit code | JSON | Result |
|-----------|-----------|------|--------|
| Allow action | 0 | (none) | Proceed normally |
| Allow + inject context | 0 | `{"additionalContext": "..."}` | Proceed + context added |
| Block action | 0 | `{"decision": "block", "reason": "..."}` | Block + show reason |
| Error (non-blocking) | 1, 3, ... | (ignored) | Show stderr, proceed |
| Error (blocking) | 2 | (ignored) | Block with stderr as reason |

**Golden rule**: To block, exit 0 with JSON decision. Exit 2 ignores JSON.

---

## Matcher Patterns (Regex)

| Pattern | Matches | Example |
|---------|---------|---------|
| `""` or `"*"` | Everything | All events |
| `"Bash"` | Exact tool name | Bash tool only |
| `"Edit\|Write"` | Multiple (regex OR) | Edit or Write tools |
| `"Notebook.*"` | Prefix pattern | Notebook, NotebookEdit, etc. |
| `"mcp__memory__.*"` | MCP server tools | All memory server tools |
| `"mcp__.*__write.*"` | Pattern across servers | Any write tool from any MCP server |

**For soul purpose**: Use `""` (empty matcher) on SessionStart, Stop, PreCompact since they fire once per session.

---

## Timeout Tuning

| Hook | Recommended timeout | Reason |
|------|-------------------|--------|
| SessionStart | 5s | User perception: fast startup |
| Stop | 5-10s | User perception: prevent hanging |
| PreCompact | 3-5s | Automated, can be quick |
| PreToolUse | 10s | Security check should be fast |
| PostToolUse | 30s | Can do work (tests, linting) |
| Async hooks | 120s | Background, user not waiting |

---

## Injection Strategy Quick Guide

| Goal | Event | Field | Example |
|------|-------|-------|---------|
| Restore soul purpose silently | SessionStart | `additionalContext` | `"Soul purpose: Build widget"` |
| Alert user about stop block | Stop | `systemMessage` | `"⚠ Soul purpose incomplete"` |
| Save state before compaction | PreCompact | `systemMessage` | `"Saving: 3 open tasks"` |
| Add debug info to response | Stop | `additionalContext` | `"Tasks remaining: [list]"` |
| Show error message | PostToolUseFailure | `additionalContext` | `"Build failed: [error details]"` |

---

## Common Mistakes to Avoid

| Mistake | Impact | Fix |
|---------|--------|-----|
| Don't check `stop_hook_active` | Infinite loop in Stop hook | Add: `if [ "$STOP_HOOK_ACTIVE" = "true" ]; then exit 0; fi` |
| Return JSON with exit 2 | JSON ignored | Use exit 0 for JSON decisions |
| Shell startup text before JSON | JSON parse error | Add `exec 2>/dev/null` to hook script |
| No `jq` error handling | Crashes on invalid JSON | Use `jq -r '.field // "default"'` |
| Timeout too short | Hook killed mid-execution | SessionStart/Stop: min 5s |
| Wrong event for blocking | No effect | Only these can block: UserPromptSubmit, PreToolUse, PermissionRequest, Stop, SubagentStop, TeammateIdle, TaskCompleted |
| Matcher doesn't match | Hook never fires | Test with: `echo "value" \| grep -E "pattern"` |

---

## Testing Checklist

- [ ] Hook script is executable: `chmod +x ~/.claude/hooks/script.sh`
- [ ] JSON output is valid: `echo '{}' \| jq .`
- [ ] Matcher pattern matches expected values (test with grep)
- [ ] Exit code is 0 for success, 2 for blocking errors
- [ ] Timeout is reasonable for expected execution time
- [ ] `stop_hook_active` is checked in Stop hook
- [ ] No shell startup text before JSON (test with `sh -x script.sh`)
- [ ] Configuration is valid JSON: `jq . ~/.claude/settings.local.json`
- [ ] Hooks registered in correct settings.local.json location
- [ ] Run with `claude --debug` to see hook firing

---

## Configuration Precedence (Read Top to Bottom)

1. Managed settings (org policy)
2. CLI arguments (`--hooks`)
3. `.claude/settings.local.json` (project-local, **for testing**)
4. `.claude/settings.json` (shared project, **for team**)
5. `~/.claude/settings.json` (user-global)
6. Plugin hooks
7. Skill/agent frontmatter

**Strategy**: Develop in `.local.json`, commit to `.claude/settings.json` when ready.

---

## Key Insights for PRD

1. **Hooks are deterministic** - No LLM involved by default. Predictable behavior.
2. **Soul purpose enforcement requires Stop hook** - Only event that can block Claude finishing.
3. **State preservation needs PreCompact** - Critical for multi-session workflows.
4. **SessionStart runs on every resume** - Opportunity to restore context silently.
5. **Async hooks don't block** - Good for background tests, not for enforcement.
6. **Matcher patterns are regex** - Powerful filtering, but test your patterns.
7. **10-minute timeout is generous** - Can safely run long operations.
8. **MCP tools work with hooks** - Full `mcp__<server>__<tool>` support.
9. **Three injection strategies** - Choose based on visibility needs (silent vs alert).
10. **Stop hook infinite loop risk** - Must check `stop_hook_active` flag always.

---

## Reference Documentation

- Full technical reference: `CLAUDE_CODE_HOOKS_TECHNICAL_REFERENCE.md`
- Research summary: `HOOKS_RESEARCH_SUMMARY.md`
- Implementation plan: `2026-02-13-session-hooks-implementation.md`
- Official docs: https://code.claude.com/docs/en/hooks
