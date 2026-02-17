# Session Lifecycle Hooks Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Convert the /start skill's deterministic Python scripts into Claude Code hooks (SessionStart, Stop, PreCompact) so session lifecycle management runs automatically in the background.

**Architecture:** Hybrid Shell + Python. A single shell script (`session-hooks.sh`) acts as the entry point for all hook events. It receives the event name as `$1`, reads hook JSON from stdin, and delegates to `session-init.py` with new hook-specific subcommands. Output is JSON matching Claude Code's hook protocol (`decision`, `reason`, `systemMessage`). State tracked in `.claude/session-lifecycle.local.md`.

**Tech Stack:** Bash (hook entry point), Python 3 (session-init.py), Claude Code hooks system (settings.local.json)

---

## Task 1: Add `hook-session-start` subcommand to session-init.py

**Files:**
- Modify: `/home/anombyte/.claude/skills/start/session-init.py:606-660` (argparse setup)
- Modify: `/home/anombyte/.claude/skills/start/session-init.py` (new function after line 601)

**Context:** This subcommand combines preflight + validate + cache-governance + restore-governance + read-context into a single call. It runs on every SessionStart event and returns a `systemMessage` with session state. Must complete in <2 seconds.

**Step 1: Write the new `cmd_hook_session_start` function**

Add after the `cmd_archive` function (after line 601). This function:
1. Calls `cmd_preflight` logic internally (detect init vs reconcile mode)
2. If reconcile mode: runs validate, cache-governance, restore-governance, read-context
3. If init mode: only runs preflight (full init requires AI judgment via /start)
4. Returns JSON with `systemMessage` containing session state summary

```python
def cmd_hook_session_start(args):
    """Hook handler for SessionStart — runs lifecycle checks silently."""
    import io
    from contextlib import redirect_stdout

    # Capture preflight output instead of printing
    f = io.StringIO()
    # Reuse preflight detection logic
    mode = "init" if not Path(SESSION_DIR).is_dir() else "reconcile"

    if mode == "init":
        # Init mode: just report that /start is needed
        _out({
            "systemMessage": "Session lifecycle: No session-context/ found. User should run /start to initialize.",
            "status": "needs_init"
        })
        return

    # Reconcile mode: run deterministic operations
    # 1. Validate session files
    repaired = []
    ok_files = []
    for sf in SESSION_FILES:
        p = Path(SESSION_DIR) / sf
        if not p.exists() or p.stat().st_size == 0:
            tmpl = Path(TEMPLATE_DIR) / sf
            if tmpl.exists():
                import shutil
                shutil.copy2(str(tmpl), str(p))
                repaired.append(sf)
            else:
                repaired.append(f"{sf} (no template)")
        else:
            ok_files.append(sf)

    # 2. Read soul purpose + active context
    soul_file = Path(SESSION_DIR) / "CLAUDE-soul-purpose.md"
    soul_purpose = ""
    if soul_file.exists():
        content = soul_file.read_text()
        lines = content.strip().split("\n")
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("<!--"):
                continue
            if "[CLOSED]" in stripped:
                break
            soul_purpose = stripped
            break

    active_file = Path(SESSION_DIR) / "CLAUDE-activeContext.md"
    active_summary = ""
    open_tasks = []
    if active_file.exists():
        ac_content = active_file.read_text()
        # Extract open tasks
        for line in ac_content.split("\n"):
            if "[ ]" in line:
                open_tasks.append(line.strip().lstrip("- "))

        # Brief summary (first 3 non-empty, non-heading lines)
        summary_lines = []
        for line in ac_content.split("\n"):
            s = line.strip()
            if s and not s.startswith("#") and not s.startswith("<!--") and not s.startswith("---"):
                summary_lines.append(s)
                if len(summary_lines) >= 3:
                    break
        active_summary = " | ".join(summary_lines)

    # Build system message
    parts = []
    if soul_purpose and soul_purpose != "(No active soul purpose)":
        parts.append(f"Soul purpose: {soul_purpose}")
    else:
        parts.append("No active soul purpose")

    if open_tasks:
        parts.append(f"Open tasks: {len(open_tasks)}")
    if repaired:
        parts.append(f"Repaired files: {', '.join(repaired)}")
    if active_summary:
        parts.append(f"Context: {active_summary}")

    _out({
        "systemMessage": " | ".join(parts),
        "status": "ok",
        "mode": mode,
        "soul_purpose": soul_purpose,
        "open_tasks": len(open_tasks),
        "repaired": repaired
    })
```

**Step 2: Register the subcommand in argparse**

Add to the argparse section (around line 636):

```python
subparsers.add_parser("hook-session-start", help="SessionStart hook handler")
```

Add to the commands dict:

```python
"hook-session-start": cmd_hook_session_start,
```

**Step 3: Test the new subcommand manually**

Run: `cd /home/anombyte/Hermes/soul_purpose_skill && python3 /home/anombyte/.claude/skills/start/session-init.py hook-session-start`

Expected: JSON with `systemMessage` containing soul purpose and session state.

**Step 4: Commit**

```bash
git add /home/anombyte/.claude/skills/start/session-init.py
git commit -m "feat: add hook-session-start subcommand for SessionStart hook"
```

---

## Task 2: Add `hook-stop` subcommand to session-init.py

**Files:**
- Modify: `/home/anombyte/.claude/skills/start/session-init.py` (new function + argparse)

**Context:** This subcommand runs on every Stop event. It reads the transcript to check if the AI output `<soul-complete>PURPOSE</soul-complete>`, and if the soul purpose is active, it blocks the stop and re-injects the soul purpose as the reason. Mirrors Ralph Loop's pattern.

**Step 1: Write the `cmd_hook_stop` function**

Add after `cmd_hook_session_start`. This function:
1. Reads stdin for hook input JSON (contains `transcript_path`)
2. Checks if `.claude/session-lifecycle.local.md` state file exists (if not, allow stop)
3. Reads the last assistant message from transcript
4. Checks for `<soul-complete>PURPOSE</soul-complete>` tags
5. If found and matches soul purpose: allow stop (exit 0, no JSON)
6. If not found: block stop, re-inject soul purpose as reason

```python
def cmd_hook_stop(args):
    """Hook handler for Stop — checks soul purpose completion."""
    import sys
    import json as json_mod

    # Read hook input from stdin
    try:
        hook_input = json_mod.loads(sys.stdin.read())
    except (json_mod.JSONDecodeError, Exception):
        # Can't parse input, allow stop
        return

    # Check state file
    state_file = Path(".claude") / "session-lifecycle.local.md"
    if not state_file.exists():
        # No active lifecycle, allow stop
        return

    # Read state file
    state_content = state_file.read_text()
    lines = state_content.strip().split("\n")

    # Parse frontmatter
    soul_purpose = ""
    active = False
    in_frontmatter = False
    frontmatter_count = 0
    for line in lines:
        if line.strip() == "---":
            frontmatter_count += 1
            if frontmatter_count == 1:
                in_frontmatter = True
            elif frontmatter_count == 2:
                in_frontmatter = False
            continue
        if in_frontmatter:
            if line.startswith("soul_purpose:"):
                soul_purpose = line.split(":", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("active:"):
                active = line.split(":", 1)[1].strip().lower() == "true"

    if not active or not soul_purpose:
        return

    # Read transcript to check for completion signal
    transcript_path = hook_input.get("transcript_path", "")
    if transcript_path and Path(transcript_path).exists():
        import re
        transcript_content = Path(transcript_path).read_text()
        # Find last assistant message
        last_assistant = ""
        for tline in transcript_content.strip().split("\n"):
            try:
                entry = json_mod.loads(tline)
                if entry.get("role") == "assistant":
                    msg = entry.get("message", {})
                    content = msg.get("content", [])
                    texts = [c.get("text", "") for c in content if c.get("type") == "text"]
                    last_assistant = "\n".join(texts)
            except (json_mod.JSONDecodeError, Exception):
                continue

        # Check for <soul-complete>...</soul-complete> tags
        match = re.search(r"<soul-complete>(.*?)</soul-complete>", last_assistant, re.DOTALL)
        if match:
            promise_text = match.group(1).strip()
            # Normalize whitespace for comparison
            import re as re_mod
            normalized_promise = re_mod.sub(r'\s+', ' ', promise_text)
            normalized_purpose = re_mod.sub(r'\s+', ' ', soul_purpose)
            if normalized_promise == normalized_purpose:
                # Soul purpose complete! Clean up and allow stop
                state_file.unlink(missing_ok=True)
                return

    # Soul purpose not complete — block stop
    _out({
        "decision": "block",
        "reason": f"Soul purpose still active: {soul_purpose}",
        "systemMessage": f"🎯 Soul purpose active: {soul_purpose} | To complete: output <soul-complete>{soul_purpose}</soul-complete> when truly done"
    })
```

**Step 2: Register the subcommand**

```python
subparsers.add_parser("hook-stop", help="Stop hook handler")
```

```python
"hook-stop": cmd_hook_stop,
```

**Step 3: Test — create a mock state file and run**

```bash
mkdir -p .claude
cat > .claude/session-lifecycle.local.md << 'EOF'
---
active: true
soul_purpose: "Test purpose"
started_at: "2026-02-13T00:00:00Z"
---
EOF
echo '{"transcript_path": "/dev/null"}' | python3 /home/anombyte/.claude/skills/start/session-init.py hook-stop
```

Expected: JSON with `decision: "block"` and soul purpose in systemMessage.

**Step 4: Test completion signal**

Create a mock transcript with `<soul-complete>Test purpose</soul-complete>` and verify the hook allows stop (no JSON output).

**Step 5: Commit**

```bash
git add /home/anombyte/.claude/skills/start/session-init.py
git commit -m "feat: add hook-stop subcommand for Stop hook with soul purpose completion"
```

---

## Task 3: Add `hook-pre-compact` subcommand to session-init.py

**Files:**
- Modify: `/home/anombyte/.claude/skills/start/session-init.py` (new function + argparse)

**Context:** This subcommand runs before context compaction. It reads the soul purpose and active context summary, then returns a `systemMessage` that gets re-injected into the compressed context. This is how critical state survives compaction.

**Step 1: Write the `cmd_hook_pre_compact` function**

```python
def cmd_hook_pre_compact(args):
    """Hook handler for PreCompact — re-inject critical context before compaction."""
    parts = []

    # Read soul purpose
    soul_file = Path(SESSION_DIR) / "CLAUDE-soul-purpose.md"
    soul_purpose = ""
    if soul_file.exists():
        content = soul_file.read_text()
        for line in content.strip().split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("<!--"):
                continue
            if "[CLOSED]" in stripped:
                break
            soul_purpose = stripped
            break

    if soul_purpose and soul_purpose != "(No active soul purpose)":
        parts.append(f"SOUL PURPOSE: {soul_purpose}")

    # Read active context summary (brief)
    active_file = Path(SESSION_DIR) / "CLAUDE-activeContext.md"
    if active_file.exists():
        ac_content = active_file.read_text()
        open_tasks = []
        progress = []
        for line in ac_content.split("\n"):
            if "[ ]" in line:
                open_tasks.append(line.strip().lstrip("- "))
            elif "[x]" in line:
                progress.append(line.strip().lstrip("- "))

        if open_tasks:
            parts.append(f"OPEN TASKS ({len(open_tasks)}): " + "; ".join(open_tasks[:5]))
        if progress:
            parts.append(f"COMPLETED ({len(progress)}): " + "; ".join(progress[:3]))

    if parts:
        _out({
            "systemMessage": " | ".join(parts)
        })
    # If nothing to inject, output nothing (allow compaction without injection)
```

**Step 2: Register the subcommand**

```python
subparsers.add_parser("hook-pre-compact", help="PreCompact hook handler")
```

```python
"hook-pre-compact": cmd_hook_pre_compact,
```

**Step 3: Test**

Run: `cd /home/anombyte/Hermes/soul_purpose_skill && python3 /home/anombyte/.claude/skills/start/session-init.py hook-pre-compact`

Expected: JSON with `systemMessage` containing soul purpose and task counts.

**Step 4: Commit**

```bash
git add /home/anombyte/.claude/skills/start/session-init.py
git commit -m "feat: add hook-pre-compact subcommand for PreCompact context injection"
```

---

## Task 4: Create session-hooks.sh shell wrapper

**Files:**
- Create: `/home/anombyte/.claude/hooks/session-hooks.sh`

**Context:** Claude Code hooks call shell scripts. This thin wrapper receives the event type, pipes stdin to the Python script, and outputs the JSON result. Must handle errors gracefully (exit 0 on failure to avoid blocking the session).

**Step 1: Create the hooks directory if needed**

```bash
mkdir -p ~/.claude/hooks
```

**Step 2: Write the shell wrapper**

```bash
#!/usr/bin/env bash
# Session lifecycle hook wrapper
# Called by Claude Code for SessionStart, Stop, and PreCompact events.
# Delegates to session-init.py with the appropriate hook subcommand.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSION_SCRIPT="$HOME/.claude/skills/start/session-init.py"

# Determine which hook subcommand to run based on $1 (event type)
EVENT="${1:-}"

case "$EVENT" in
  session-start)
    SUBCOMMAND="hook-session-start"
    ;;
  stop)
    SUBCOMMAND="hook-stop"
    ;;
  pre-compact)
    SUBCOMMAND="hook-pre-compact"
    ;;
  *)
    # Unknown event, allow through
    exit 0
    ;;
esac

# Pipe stdin (hook input JSON) to the Python script
# If Python fails, exit 0 to avoid blocking the session
python3 "$SESSION_SCRIPT" "$SUBCOMMAND" 2>/dev/null || exit 0
```

**Step 3: Make executable**

```bash
chmod +x ~/.claude/hooks/session-hooks.sh
```

**Step 4: Test each event**

```bash
echo '{}' | ~/.claude/hooks/session-hooks.sh session-start
echo '{"transcript_path": "/dev/null"}' | ~/.claude/hooks/session-hooks.sh stop
echo '{}' | ~/.claude/hooks/session-hooks.sh pre-compact
echo '{}' | ~/.claude/hooks/session-hooks.sh unknown-event
```

**Step 5: Commit**

```bash
git add ~/.claude/hooks/session-hooks.sh
git commit -m "feat: add session-hooks.sh shell wrapper for Claude Code hooks"
```

---

## Task 5: Register hooks in settings.local.json

**Files:**
- Modify: `/home/anombyte/.claude/settings.local.json`

**Context:** Replace the old `auto-enroll-guardian.sh` SessionStart hook with the new session lifecycle hooks. Register SessionStart, Stop, and PreCompact events. Note: hooks in settings.local.json use the `"hooks"` wrapper key (unlike the settings.json user format which is top-level).

**Step 1: Read current settings.local.json**

Current content:
```json
{
  "permissions": { "allow": ["Bash(echo:*)"], "deny": [], "ask": [] },
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/auto-enroll-guardian.sh",
            "timeout": 5,
            "statusMessage": "Auto-enrolling session in guardian"
          }
        ]
      }
    ]
  }
}
```

**Step 2: Replace with new hook configuration**

```json
{
  "permissions": {
    "allow": ["Bash(echo:*)"],
    "deny": [],
    "ask": []
  },
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
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
        "matcher": "",
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

**Step 3: Archive old guardian hook**

```bash
mkdir -p ~/.claude/hooks/archived
mv ~/.claude/hooks/auto-enroll-guardian.sh ~/.claude/hooks/archived/ 2>/dev/null || true
```

**Step 4: Verify JSON is valid**

```bash
python3 -c "import json; json.load(open('$HOME/.claude/settings.local.json'))" && echo "Valid JSON"
```

**Step 5: Commit**

```bash
git add ~/.claude/settings.local.json
git commit -m "feat: register session lifecycle hooks (SessionStart, Stop, PreCompact)"
```

---

## Task 6: Add state file management (activate/deactivate lifecycle)

**Files:**
- Modify: `/home/anombyte/.claude/skills/start/session-init.py` (new `hook-activate` and `hook-deactivate` subcommands)

**Context:** The Stop hook only blocks if `.claude/session-lifecycle.local.md` exists. The /start skill needs a way to create this file (activate) after brainstorm, and the hook needs a way to remove it (deactivate) when soul purpose is complete. This mirrors Ralph's `.claude/ralph-loop.local.md` pattern.

**Step 1: Write `cmd_hook_activate` function**

```python
def cmd_hook_activate(args):
    """Create the lifecycle state file to activate Stop hook enforcement."""
    from datetime import datetime, timezone

    state_dir = Path(".claude")
    state_dir.mkdir(exist_ok=True)

    state_file = state_dir / "session-lifecycle.local.md"

    content = f"""---
active: true
soul_purpose: "{args.soul_purpose}"
started_at: "{datetime.now(timezone.utc).isoformat()}"
---
"""
    state_file.write_text(content)
    _out({
        "status": "ok",
        "state_file": str(state_file),
        "soul_purpose": args.soul_purpose
    })
```

**Step 2: Write `cmd_hook_deactivate` function**

```python
def cmd_hook_deactivate(args):
    """Remove the lifecycle state file to deactivate Stop hook enforcement."""
    state_file = Path(".claude") / "session-lifecycle.local.md"
    if state_file.exists():
        state_file.unlink()
        _out({"status": "ok", "message": "Lifecycle deactivated"})
    else:
        _out({"status": "ok", "message": "Already inactive"})
```

**Step 3: Register subcommands**

```python
activate_p = subparsers.add_parser("hook-activate", help="Activate lifecycle Stop hook")
activate_p.add_argument("--soul-purpose", required=True)

subparsers.add_parser("hook-deactivate", help="Deactivate lifecycle Stop hook")
```

```python
"hook-activate": cmd_hook_activate,
"hook-deactivate": cmd_hook_deactivate,
```

**Step 4: Test activation and deactivation**

```bash
cd /home/anombyte/Hermes/soul_purpose_skill
python3 /home/anombyte/.claude/skills/start/session-init.py hook-activate --soul-purpose "Test purpose"
cat .claude/session-lifecycle.local.md
python3 /home/anombyte/.claude/skills/start/session-init.py hook-deactivate
ls .claude/session-lifecycle.local.md  # Should not exist
```

**Step 5: Commit**

```bash
git add /home/anombyte/.claude/skills/start/session-init.py
git commit -m "feat: add hook-activate/deactivate for lifecycle state management"
```

---

## Task 7: Update SKILL.md to use hooks instead of manual script calls

**Files:**
- Modify: `/home/anombyte/.claude/skills/start/SKILL.md`

**Context:** The SKILL.md currently instructs the AI to manually call preflight, validate, cache-governance, restore-governance, read-context in sequence. With hooks, SessionStart handles all of this automatically. The SKILL.md should become thinner — only handling brainstorm, soul purpose questions, Ralph Loop setup, and activating the lifecycle state file.

**Step 1: Simplify Init Mode**

Remove manual script calls for preflight, validate, cache-governance, restore-governance. Replace with:
- SessionStart hook already ran (check systemMessage for session state)
- If systemMessage says "needs_init": run init subcommand, ensure-governance, then brainstorm
- After brainstorm: call `hook-activate --soul-purpose "DERIVED_PURPOSE"` to enable Stop enforcement

**Step 2: Simplify Reconcile Mode**

Remove manual script calls for validate, cache-governance, restore-governance, read-context. Replace with:
- SessionStart hook already ran (systemMessage contains soul purpose + state)
- AI only handles: directive check, self-assessment, user interaction, harvest/archive
- After any soul purpose change: call `hook-activate` with new purpose

**Step 3: Add lifecycle deactivation on Close**

When user chooses "Close" for soul purpose, call `hook-deactivate` to remove state file.

**Step 4: Document the hook architecture in SKILL.md header**

Add a brief section explaining that hooks handle the plumbing and the AI handles judgment calls only.

**Step 5: Commit**

```bash
git add /home/anombyte/.claude/skills/start/SKILL.md
git commit -m "refactor: slim SKILL.md — hooks handle plumbing, AI handles judgment"
```

---

## Task 8: End-to-end integration test

**Files:**
- No new files — testing existing implementation

**Context:** Verify the full flow works: SessionStart fires on new session, Stop blocks when soul purpose active, PreCompact preserves context, completion signal allows stop.

**Step 1: Clean state test**

```bash
cd /tmp/test-hooks-project
mkdir -p session-context
# Simulate SessionStart
echo '{}' | ~/.claude/hooks/session-hooks.sh session-start
```

Expected: JSON with systemMessage containing session state.

**Step 2: Stop hook enforcement test**

```bash
# Activate lifecycle
python3 ~/.claude/skills/start/session-init.py hook-activate --soul-purpose "Build the widget"

# Try to stop — should block
echo '{"transcript_path": "/dev/null"}' | ~/.claude/hooks/session-hooks.sh stop
```

Expected: JSON with `decision: "block"` and soul purpose in systemMessage.

**Step 3: Completion signal test**

Create a mock transcript with the completion signal and verify stop is allowed.

**Step 4: PreCompact test**

```bash
echo '{}' | ~/.claude/hooks/session-hooks.sh pre-compact
```

Expected: JSON with systemMessage containing soul purpose and tasks.

**Step 5: Deactivation test**

```bash
python3 ~/.claude/skills/start/session-init.py hook-deactivate
echo '{"transcript_path": "/dev/null"}' | ~/.claude/hooks/session-hooks.sh stop
```

Expected: No JSON output (stop allowed).

**Step 6: Commit any test fixes**

```bash
git add -A
git commit -m "test: end-to-end integration verification of session lifecycle hooks"
```

---

## Dependency Graph

```
Task 1 (hook-session-start) ──┐
Task 2 (hook-stop)          ──┼── Task 4 (shell wrapper) ── Task 5 (register hooks)
Task 3 (hook-pre-compact)   ──┘                                     │
                                                                     │
Task 6 (activate/deactivate) ───── Task 7 (update SKILL.md) ── Task 8 (integration test)
```

Tasks 1-3 can run in parallel. Task 4 depends on 1-3. Task 5 depends on 4. Task 6 can run in parallel with 4-5. Task 7 depends on 5+6. Task 8 depends on all.
