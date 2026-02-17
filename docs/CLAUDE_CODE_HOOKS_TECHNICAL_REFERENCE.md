# Claude Code Hooks System: Technical Reference

**Last Updated**: February 17, 2026
**Sources**: Claude Code official documentation (https://code.claude.com/docs/en/hooks), Claude Code settings guide (https://code.claude.com/docs/en/settings)

---

## Quick Overview

Claude Code hooks are user-defined shell commands or LLM prompts that execute automatically at specific points in Claude Code's lifecycle. They enable session management automation, context preservation across compaction, soul purpose enforcement, and quality gates.

---

## Part 1: Hook Events

### All Hook Events (14 total)

Claude Code fires hooks at these lifecycle points:

| Event | When it fires | Can block? | Key use cases |
|-------|---------------|-----------|---------------|
| **SessionStart** | When a session begins or resumes | No | Load context, set environment variables, session state restoration |
| **UserPromptSubmit** | When user submits a prompt, before processing | Yes | Validate prompts, add context conditionally, block certain inputs |
| **PreToolUse** | Before a tool call executes | Yes | Permission enforcement, security validation, modify tool input |
| **PermissionRequest** | When permission dialog appears | Yes | Auto-approve/deny tool calls, modify input, apply permission rules |
| **PostToolUse** | After a tool succeeds | No | Logging, validation, inject context based on output |
| **PostToolUseFailure** | After a tool fails | No | Error logging, provide corrective feedback |
| **Notification** | When Claude Code sends notifications | No | Route notifications, alert on permission prompts |
| **SubagentStart** | When a subagent is spawned | No | Inject context into subagent, track agent creation |
| **SubagentStop** | When a subagent finishes | Yes | Enforce quality gates before agent stops |
| **Stop** | When Claude finishes responding | Yes | Enforce soul purpose completion, prevent stopping until conditions met |
| **TeammateIdle** | Before agent team teammate goes idle | Yes | Enforce team-level quality gates before teammate pauses |
| **TaskCompleted** | When a task is marked complete | Yes | Enforce test/lint requirements before task closes |
| **PreCompact** | Before context compaction | No | Save conversation, inject critical context before compression |
| **SessionEnd** | When session terminates | No | Cleanup, logging, state persistence |

### SessionStart in Detail

**When it fires**: On every session start (new, resumed, cleared, or post-compaction)

**Matcher values**:
- `startup` - New session
- `resume` - `/resume`, `--resume`, or `--continue`
- `clear` - `/clear` command
- `compact` - After auto or manual compaction

**Input schema**:
```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default|plan|acceptEdits|dontAsk|bypassPermissions",
  "hook_event_name": "SessionStart",
  "source": "startup|resume|clear|compact",
  "model": "claude-sonnet-4-5-20250929",
  "agent_type": "optional-agent-name"
}
```

**Output options**:
- Plain text stdout → added as context to Claude's conversation
- JSON with `additionalContext` → added discretely without showing hook output
- `systemMessage` (JSON field) → shown as warning to user

**Special capability**: `CLAUDE_ENV_FILE` environment variable available. Write `export VAR=value` lines to persist environment across subsequent Bash commands.

**Timeout**: Default 600 seconds (10 minutes), configurable per hook

---

### Stop in Detail (Critical for Soul Purpose Enforcement)

**When it fires**: When Claude finishes responding (unless interrupted by user)

**Input schema**:
```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default|plan|acceptEdits|dontAsk|bypassPermissions",
  "hook_event_name": "Stop",
  "stop_hook_active": true|false
}
```

**Output options**:
- Exit 0, no JSON → Allow Claude to stop
- Exit 0 with JSON `{"decision": "block", "reason": "..."}` → Prevent stop, re-inject reason as next prompt
- Exit 2 → Block stop (stderr fed to Claude)

**Critical field**: `stop_hook_active` is `true` if Claude is continuing due to this hook. Check this to prevent infinite loops.

**Decision control**:
```json
{
  "decision": "block",
  "reason": "Soul purpose not complete: Build a widget with 3 features"
}
```

---

### PreCompact in Detail

**When it fires**: Before context compaction (manual `/compact` or automatic when context fills)

**Matcher values**:
- `manual` - User ran `/compact`
- `auto` - Automatic compaction triggered

**Input schema**:
```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default|plan|acceptEdits|dontAsk|bypassPermissions",
  "hook_event_name": "PreCompact",
  "trigger": "manual|auto",
  "custom_instructions": "user-provided /compact instructions or empty"
}
```

**Output options**:
- JSON with `systemMessage` → Re-injected into compressed context
- `additionalContext` field → Added to compressed context

**Use case**: Preserve soul purpose and active task state across compaction. The injected context becomes available immediately after compaction completes.

---

## Part 2: Hook Protocol

### JSON Input/Output Model

All hooks receive JSON via stdin with:
- **Common fields**: `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`
- **Event-specific fields**: Varies by event type (see event details above)

All hooks can return JSON via stdout (on exit 0) with:
- **Universal fields**: `continue`, `stopReason`, `suppressOutput`, `systemMessage`
- **Event-specific fields**: Varies by event (see below)

### Exit Codes

| Exit code | Meaning | Effect |
|-----------|---------|--------|
| **0** | Success | Parse stdout for JSON control fields |
| **2** | Blocking error | Stderr fed to Claude as reason, action blocked (effect depends on event) |
| **Other** | Non-blocking error | Stderr shown in verbose mode only, execution continues |

### JSON Output Fields (Universal)

Available on all hooks:

| Field | Type | Effect |
|-------|------|--------|
| `continue` | boolean | Default `true`. If `false`, Claude stops entirely after hook runs. Overrides event-specific decisions |
| `stopReason` | string | Message shown to user when `continue` is `false`. NOT shown to Claude |
| `suppressOutput` | boolean | Default `false`. If `true`, hides hook stdout from verbose mode |
| `systemMessage` | string | Warning message shown to user. Different from `additionalContext` |

### Decision Control Patterns

Not all hooks support blocking. The pattern depends on event type:

**Pattern 1: Top-level `decision` field** (UserPromptSubmit, PostToolUse, PostToolUseFailure, Stop, SubagentStop)
```json
{
  "decision": "block",
  "reason": "Explanation shown to Claude"
}
```

**Pattern 2: `hookSpecificOutput` with `permissionDecision`** (PreToolUse)
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask",
    "permissionDecisionReason": "Explanation",
    "updatedInput": { "field": "new_value" },
    "additionalContext": "Context for Claude"
  }
}
```

**Pattern 3: `hookSpecificOutput` with `decision.behavior`** (PermissionRequest)
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow|deny",
      "updatedInput": { "field": "new_value" },
      "updatedPermissions": [...],
      "message": "Explanation"
    }
  }
}
```

**Pattern 4: Exit codes only** (TeammateIdle, TaskCompleted)
- No JSON allowed. Exit 0 to allow, exit 2 to block (stderr feedback).

### Session Message Injection

Hooks can inject content into Claude's context in two ways:

1. **`additionalContext`** (JSON field):
   - Discrete, doesn't show hook output
   - Available on SessionStart, UserPromptSubmit, SubagentStart, PostToolUse, PostToolUseFailure, Stop, SubagentStop

2. **`systemMessage`** (JSON field):
   - Shown as warning to user
   - Available on all hooks

3. **Plain stdout** (SessionStart, UserPromptSubmit only):
   - Shown as hook output in transcript
   - Non-JSON text added as context

### Matcher Syntax (Pattern Matching)

The `matcher` field in hook configuration is a **regex string** that filters when hooks fire:

| Event type | Matches on | Example matchers |
|------------|-----------|------------------|
| PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest | Tool name | `Bash`, `Edit|Write`, `mcp__.*`, `Read` |
| SessionStart | Session source | `startup`, `resume`, `clear`, `compact` |
| SessionEnd | Exit reason | `clear`, `logout`, `prompt_input_exit`, `other` |
| Notification | Notification type | `permission_prompt`, `idle_prompt`, `auth_success` |
| SubagentStart, SubagentStop | Agent type | `Explore`, `Plan`, `Bash`, or custom agent name |
| PreCompact | Compaction trigger | `manual`, `auto` |
| UserPromptSubmit, Stop, TeammateIdle, TaskCompleted | No matcher support | Always fires |

**Matcher syntax**:
- `"*"`, `""`, or omit → Match all
- `Edit|Write` → Match either tool (regex alternation)
- `Notebook.*` → Match tools starting with "Notebook" (regex pattern)
- `mcp__memory__.*` → Match all tools from MCP memory server

---

## Part 3: Hook Configuration

### Configuration Locations (Precedence Order)

| Location | Scope | Shared? | Gitignored? |
|----------|-------|---------|-------------|
| Managed policy settings | Organization-wide | Yes | N/A (admin-controlled) |
| Command-line args | Current session only | No | N/A |
| `.claude/settings.local.json` | Single project, current user | No | Yes |
| `.claude/settings.json` | Single project, all collaborators | Yes | No |
| `~/.claude/settings.json` | All projects, current user | No | No |
| Plugin `hooks/hooks.json` | When plugin enabled | Yes | N/A |
| Skill/agent frontmatter YAML | While component active | Yes | N/A |

**Precedence**: Managed > CLI args > Local > Project > User > Plugin > Skill/Agent

### JSON Structure

Hooks are nested three levels deep:

```json
{
  "hooks": {
    "EVENT_NAME": [
      {
        "matcher": "filter_pattern_or_empty",
        "hooks": [
          {
            "type": "command|prompt|agent",
            "command": "script_path",
            "timeout": 600,
            "statusMessage": "Custom spinner text"
          }
        ]
      }
    ]
  }
}
```

### Hook Handler Types

**Command hooks** (`type: "command"`):
- Executes a shell script
- Script receives JSON via stdin
- Script outputs JSON on exit 0 for decisions
- Fields: `command` (required), `async` (optional), `timeout`, `statusMessage`

**Prompt hooks** (`type: "prompt"`):
- Sends hook input + prompt to Claude model
- Model returns `{"ok": true/false, "reason": "..."}`
- Cannot block on most events (unless structured for specific events)
- Fields: `prompt` (required), `model` (optional), `timeout` (default 30s)

**Agent hooks** (`type: "agent"`):
- Spawns a subagent with prompt and tool access
- Subagent can read files, search, verify conditions
- Returns `{"ok": true/false, "reason": "..."}`
- Fields: `prompt` (required), `model` (optional), `timeout` (default 60s)

### Example: Complete Hook Configuration

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/session-hooks.sh session-start",
            "timeout": 5,
            "statusMessage": "Session lifecycle check"
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
            "command": "~/.claude/hooks/session-hooks.sh stop",
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
            "command": "~/.claude/hooks/session-hooks.sh pre-compact",
            "timeout": 3,
            "statusMessage": "Preserving session context"
          }
        ]
      }
    ]
  }
}
```

### Path Reference Variables

Use these to make paths portable across machines and projects:

- `$CLAUDE_PROJECT_DIR` - Project root directory (quote for spaces: `"$CLAUDE_PROJECT_DIR"`)
- `${CLAUDE_PLUGIN_ROOT}` - Plugin root directory (if hook is in a plugin)
- `$HOME` or `~` - User home directory

---

## Part 4: Practical Patterns

### Pattern 1: SessionStart for Context Injection

**Goal**: Restore session state when resuming

```bash
#!/bin/bash
# hooks/session-start.sh

# Read hook input
HOOK_INPUT=$(cat)
SOURCE=$(echo "$HOOK_INPUT" | jq -r '.source')

# On resume, inject previous context
if [ "$SOURCE" = "resume" ]; then
  if [ -f ".claude/session-context.md" ]; then
    CONTEXT=$(cat .claude/session-context.md)
    echo "{\"additionalContext\": \"$CONTEXT\"}"
  fi
fi

exit 0
```

### Pattern 2: Stop Hook for Soul Purpose Enforcement

**Goal**: Prevent Claude from stopping until soul purpose is complete

```bash
#!/bin/bash
# hooks/soul-purpose-check.sh

HOOK_INPUT=$(cat)
STOP_HOOK_ACTIVE=$(echo "$HOOK_INPUT" | jq -r '.stop_hook_active')

# Prevent infinite loops
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
  exit 0
fi

# Check if soul purpose is complete
if [ ! -f ".claude/soul-complete.txt" ]; then
  SOUL_PURPOSE=$(cat .claude/soul-purpose.txt 2>/dev/null || echo "Unknown")
  echo "{\"decision\": \"block\", \"reason\": \"Soul purpose not complete: $SOUL_PURPOSE\"}"
  exit 0
fi

exit 0
```

### Pattern 3: PreCompact for Context Preservation

**Goal**: Save critical state before compaction, re-inject after

```bash
#!/bin/bash
# hooks/pre-compact.sh

# Read critical context files
SOUL_PURPOSE=""
OPEN_TASKS=""

if [ -f ".claude/soul-purpose.txt" ]; then
  SOUL_PURPOSE=$(cat .claude/soul-purpose.txt)
fi

if [ -f ".claude/open-tasks.txt" ]; then
  OPEN_TASKS=$(cat .claude/open-tasks.txt | head -3)
fi

# Output as systemMessage to be re-injected
MSG="SOUL: $SOUL_PURPOSE | TASKS: $OPEN_TASKS"
echo "{\"systemMessage\": \"$MSG\"}"

exit 0
```

### Pattern 4: PreToolUse for Security Validation

**Goal**: Block dangerous commands

```bash
#!/bin/bash
# hooks/security-check.sh

HOOK_INPUT=$(cat)
TOOL_NAME=$(echo "$HOOK_INPUT" | jq -r '.tool_name')
COMMAND=$(echo "$HOOK_INPUT" | jq -r '.tool_input.command // empty')

if [ "$TOOL_NAME" = "Bash" ]; then
  if echo "$COMMAND" | grep -qE "rm -rf|: \(\) \{|fork\(\)"; then
    echo "{\"hookSpecificOutput\": {\"hookEventName\": \"PreToolUse\", \"permissionDecision\": \"deny\", \"permissionDecisionReason\": \"Dangerous command blocked\"}}"
    exit 0
  fi
fi

exit 0
```

### Pattern 5: Async Hook for Background Tasks

**Goal**: Run tests after file write, report results asynchronously

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/run-tests.sh",
            "async": true,
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

```bash
#!/bin/bash
# hooks/run-tests.sh

# Runs asynchronously, doesn't block Claude

TEST_RESULT=$(npm test 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "{\"systemMessage\": \"Tests passed\"}"
else
  echo "{\"systemMessage\": \"Tests failed: $TEST_RESULT\"}"
fi
```

---

## Part 5: Event-to-Blocker Matrix

Quick reference for which events can block and how:

| Event | Can block? | Blocking method | Effect when blocked |
|-------|-----------|-----------------|-------------------|
| **SessionStart** | No | N/A | N/A (informational only) |
| **UserPromptSubmit** | Yes | `decision: "block"` or exit 2 | Prompt erased, not processed |
| **PreToolUse** | Yes | `permissionDecision: "deny"` or exit 2 | Tool call prevented |
| **PermissionRequest** | Yes | `decision.behavior: "deny"` or exit 2 | Permission denied |
| **PostToolUse** | No | N/A (tool already ran) | N/A |
| **PostToolUseFailure** | No | N/A | N/A |
| **Notification** | No | N/A | N/A |
| **SubagentStart** | No | N/A | N/A |
| **SubagentStop** | Yes | `decision: "block"` or exit 2 | Subagent continues |
| **Stop** | Yes | `decision: "block"` or exit 2 | Claude continues |
| **TeammateIdle** | Yes | exit 2 (stderr feedback) | Teammate continues |
| **TaskCompleted** | Yes | exit 2 (stderr feedback) | Task not marked complete |
| **PreCompact** | No | N/A | N/A (informational) |
| **SessionEnd** | No | N/A | N/A (cleanup only) |

---

## Part 6: Timeout Behavior

### Default Timeouts

| Hook type | Default timeout |
|-----------|-----------------|
| Command hooks | 600 seconds (10 minutes) |
| Prompt hooks | 30 seconds |
| Agent hooks | 60 seconds |
| Async hooks | 10 minutes (configurable) |

### Timeout Configuration

Set per hook in settings:

```json
{
  "type": "command",
  "command": "script.sh",
  "timeout": 120  // seconds
}
```

When timeout expires:
- Hook execution terminates
- For sync hooks: treated as non-blocking error
- For async hooks: background process killed
- Execution continues (except for blocking events that require output)

---

## Part 7: JSON Validation & Error Handling

### JSON Output Rules

1. **Must exit 0** for JSON to be processed. Exit 2 ignores JSON.
2. **Shell startup output** can break JSON parsing. Redirect shell profile output:
   ```bash
   #!/bin/bash
   # Ensure clean stdout
   set -e
   exec 2>/dev/null  # Suppress startup messages
   # ... rest of hook
   ```
3. **Only one JSON object** per stdout. Multiple lines = parse failure.

### Common Errors

| Problem | Cause | Fix |
|---------|-------|-----|
| "JSON validation failed" | Shell startup text before JSON | Suppress startup output in hook script |
| Hook doesn't fire | Matcher doesn't match | Check matcher regex against actual values |
| Hook runs but decision ignored | Wrong exit code (not 0) or wrong JSON structure | Verify exit 0 and event-specific JSON fields |
| Infinite Stop loop | `stop_hook_active` check missing | Check `stop_hook_active` before blocking |

---

## Part 8: MCP Tool Matching

Hooks work with MCP (Model Context Protocol) tools. MCP tools use naming: `mcp__<server>__<tool>`

### Examples

- `mcp__memory__create_entities` - Memory server
- `mcp__filesystem__read_file` - Filesystem server
- `mcp__github__search_repositories` - GitHub server

### Matchers for MCP

```json
{
  "matcher": "mcp__memory__.*"  // All memory tools
}
```

```json
{
  "matcher": "mcp__.*__write.*"  // Any write tools from any server
}
```

---

## Part 9: Hook Registration in settings.local.json

### File Location
- `~/.claude/settings.local.json` - User-level hooks (all projects)
- `.claude/settings.local.json` - Project-level hooks (this project only)
- `.claude/settings.json` - Shared project hooks (committed to git)

### Minimal Example

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Session started' | logger"
          }
        ]
      }
    ]
  }
}
```

### Full Example with Multiple Events

```json
{
  "permissions": {
    "allow": ["Bash(npm run *)"],
    "deny": ["Bash(rm *)"]
  },
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/session-start.sh",
            "timeout": 5,
            "statusMessage": "Initializing session"
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "auto",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/pre-compact.sh",
            "timeout": 3
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
    ]
  }
}
```

---

## Part 10: Debugging and Troubleshooting

### Enable Debug Mode

```bash
claude --debug
```

Output shows:
- Which hooks matched
- Exit codes and stdout/stderr
- JSON parsing results
- Decision enforcement

### Verbose Mode

Press `Ctrl+O` in Claude Code to see hook execution details in transcript.

### Common Issues

**Hook not firing**:
- Check matcher pattern (test with `echo "value" | grep -E "pattern"`)
- Verify hook event name and configuration location
- Run `claude --debug` to confirm matcher evaluation

**JSON parsing fails**:
- Print only JSON to stdout (no shell startup text)
- Validate JSON with `echo '...' | jq .`
- Redirect stderr: `exec 2>/dev/null`

**Infinite Stop loop**:
- Add `stop_hook_active` check
- Ensure exit code 0 on success
- Test with `--debug` to see hook invocations

**Hook timeout too short**:
- Increase `timeout` value in settings
- Profile script execution time: `time script.sh < input.json`

---

## Part 11: Hook Lifecycle in Diagram

```
Session Start
    ↓
SessionStart hook fires
    ↓
[Claude processes prompts in loop]
    ↓
UserPromptSubmit hook fires
    ↓
Claude decides on tool call
    ↓
PreToolUse hook fires (can block)
    ↓
Tool executes
    ↓
PostToolUse or PostToolUseFailure hook fires
    ↓
Claude finishes response
    ↓
Stop hook fires (can block)
    ↓
[Repeat loop if Stop hook blocks]
    ↓
User exits or context fills
    ↓
PreCompact hook fires (can save context)
    ↓
[Context compaction happens]
    ↓
SessionEnd hook fires
```

---

## Part 12: Key Takeaways for PRD Writers

1. **Hooks run deterministically**: No AI judgment in hook logic. Pure control flow.
2. **Session injection strategy**: Use `additionalContext` (discrete) vs `systemMessage` (user-visible) carefully.
3. **Timeout budgets**: SessionStart and Stop should complete in <5 seconds to avoid UX delays.
4. **Stop hook + soul purpose**: Requires `stop_hook_active` check to prevent infinite loops.
5. **Async hooks**: Good for background tests/deploys. Cannot block or return decisions.
6. **Event matchers**: Use regex for precise filtering (e.g., `Edit|Write` for file modifications).
7. **MCP tool integration**: Hooks work with MCP tools using `mcp__<server>__<tool>` naming.
8. **Configuration precedence**: Local > Project > User. Test locally before committing shared hooks.
9. **Error handling**: Always test JSON output with `jq` and confirm exit codes.
10. **Async communication**: Async hook results injected on next conversation turn, not immediately.

---

## References

- [Claude Code Hooks Reference](https://code.claude.com/docs/en/hooks)
- [Claude Code Settings Guide](https://code.claude.com/docs/en/settings)
- [Claude Code Hooks Guide](https://code.claude.com/docs/en/hooks-guide)
- [Session Hooks Implementation Plan](/home/anombyte/Hermes/Projects/_Soul_Purpose_Skill_/docs/plans/2026-02-13-session-hooks-implementation.md)
