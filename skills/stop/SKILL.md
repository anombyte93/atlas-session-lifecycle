---
name: stop
description: "Gracefully close a session: harvest promotable content, archive soul purpose, settle AtlasCoin bounty, clean up. Use when user says /stop, wrap up, done for the day, finishing up, close session, or end session."
user-invocable: true
---

# Session Stop Skill

> Graceful session close. Harvest → Settle → Archive → Cleanup.

**Plugin root** (resolved at load time):

!`if [ -n "$CLAUDE_PLUGIN_ROOT" ]; then echo "$CLAUDE_PLUGIN_ROOT"; elif p=$(find ~/.claude/plugins -path '*/atlas-session-lifecycle/scripts/session-init.py' -type f 2>/dev/null | head -1) && [ -n "$p" ]; then dirname "$(dirname "$p")"; elif [ -f ~/.claude/skills/start/session-init.py ]; then echo "$HOME/.claude/skills/start"; else echo 'NOT_FOUND'; fi`

Use the resolved path above as `PLUGIN_ROOT`. If `NOT_FOUND`, tell user "Session lifecycle plugin not installed." and **EXIT**.

**Script path** (resolved at load time):

!`if [ -n "$CLAUDE_PLUGIN_ROOT" ] && [ -f "$CLAUDE_PLUGIN_ROOT/scripts/session-init.py" ]; then echo "$CLAUDE_PLUGIN_ROOT/scripts/session-init.py"; elif p=$(find ~/.claude/plugins -path '*/atlas-session-lifecycle/scripts/session-init.py' -type f 2>/dev/null | head -1) && [ -n "$p" ]; then echo "$p"; elif [ -f ~/.claude/skills/start/session-init.py ]; then echo "$HOME/.claude/skills/start/session-init.py"; else echo 'NOT_FOUND'; fi`

Use the resolved path above as `SESSION_SCRIPT`.

**AtlasCoin URL**:

!`if [ -n "$ATLASCOIN_URL" ]; then echo "$ATLASCOIN_URL"; else echo "http://localhost:3000"; fi`

Use the resolved URL above as `ATLASCOIN_URL`.

---

## Hard Invariants

1. **User authority is absolute** — AI NEVER closes without confirmation.
2. **Human-visible memory only** — All state lives in files.
3. **Trust separation** — bounty-agent submits, finality-agent verifies. Never the same agent.
4. **AtlasCoin is optional** — if down, skip bounty steps and continue closing.
5. **Idempotent** — Running /stop on an already-closed session exits cleanly.
6. **Archive after verification** — Soul purpose is archived AFTER bounty settlement, not before.

---

## UX Contract

- User sees ONE confirmation question, then settlement results. Nothing else.
- Agent Teams are invisible — no team creation, task assignment, or teammate messages shown.
- No step announcements, no narration.

---

## Phase 0: State Detection (no team yet)

Cheap checks before paying team-spawn cost:

1. `test -d session-context/` → if missing: tell user "No active session to close." **EXIT**.
2. Read `session-context/CLAUDE-soul-purpose.md` → extract current soul purpose text (first non-header, non-blank line after `# Soul Purpose`). If the extracted text is empty, starts with `[CLOSED]`, `---`, `##`, or `(No active soul purpose)`: tell user "No active soul purpose to close." **EXIT**.
3. `test -f session-context/BOUNTY_ID.txt` → store `HAS_BOUNTY` (true/false). If true, read the bounty ID.

---

## Phase 1: User Confirmation

Ask ONE question via AskUserQuestion:

**Question**: "Soul purpose: '[soul purpose text]'. Close this session?"
- **"Close"** — Archive and shut down.
- **"Close and set new purpose"** — Archive current, set a new soul purpose for next session.
- **"Cancel"** — Do nothing. **EXIT**.

If "Close and set new purpose": ask a follow-up question for the new purpose text. Store as `NEW_PURPOSE`.

---

## Phase 2: Team Setup

Always create a fresh team — do not attempt to reuse an existing one.

1. `TeamCreate("session-lifecycle")`
2. Spawn session-ops (always needed)
3. If `HAS_BOUNTY`: spawn bounty-agent

### Spawn session-ops

Read `PLUGIN_ROOT/prompts/session-ops.md`. Replace `{SESSION_SCRIPT}` with the resolved `SESSION_SCRIPT`, `{PROJECT_DIR}` with current working directory. Spawn:

```
Task(name="session-ops", team_name="session-lifecycle", subagent_type="general-purpose", prompt=<resolved prompt>)
```

### Spawn bounty-agent (only if HAS_BOUNTY)

Read `PLUGIN_ROOT/prompts/bounty-agent.md`. Replace `{ATLASCOIN_URL}`, `{PROJECT_DIR}`. Spawn:

```
Task(name="bounty-agent", team_name="session-lifecycle", subagent_type="general-purpose", prompt=<resolved prompt>)
```

---

## Phase 3: Settlement

**Read `PLUGIN_ROOT/custom.md`** if it exists, and follow any instructions under "During Settlement".

**Error handling**: If any session-ops command fails, report the error to the user and ask: "Continue closing (skip failed step) or abort?" If abort, clean up team and **EXIT**.

### Step 1: Validate + Harvest (via session-ops)

1. Message session-ops: run `validate` (ensures session files are intact before operating on them).
2. Message session-ops: run `harvest`.
3. Receive harvest JSON. If promotable content exists:
   - **Main agent judges** what to promote (decisions need rationale, patterns must be reusable, troubleshooting must have verified solutions).
   - Present promotable items to user for approval.
   - After approval, append promoted content to target session-context files via Edit tool.

### Step 2: Bounty Settlement (only if HAS_BOUNTY)

1. Message bounty-agent: check AtlasCoin health first (`GET /api/health`). If unhealthy: tell user "AtlasCoin is not available. Skipping bounty settlement." and proceed to Step 3.
2. Message bounty-agent: check bounty status via `GET /api/bounties/:id`.
3. If bounty is active, message bounty-agent: submit solution via `POST /api/bounties/:id/submit`.
4. Spawn finality-agent: Read `PLUGIN_ROOT/prompts/finality-agent.md`, replace `{SESSION_SCRIPT}`, `{PROJECT_DIR}`, `{ATLASCOIN_URL}`, `{BOUNTY_ID}`. Spawn as teammate.
5. Finality-agent collects evidence and calls `POST /api/bounties/:id/verify`.
6. **If PASSED**: Message bounty-agent to call `POST /api/bounties/:id/settle`. Tell user: "Soul purpose verified and settled. [X] AtlasCoin tokens earned."
7. **If FAILED**: Ask user:
   - "Close anyway (forfeit bounty)" → continue to Step 3
   - "Continue working" → clean up team, **EXIT** (user returns to active work with purpose intact)

### Step 3: Archive (via session-ops)

This runs AFTER bounty settlement so "continue working" can exit without corrupting state.

Message session-ops: run `archive --old-purpose "CURRENT_SOUL_PURPOSE"` (add `--new-purpose "NEW_PURPOSE"` if user chose "Close and set new purpose").

### Step 4: Cleanup

1. Remove Ralph Loop indicator if present: `rm -f ~/.claude/ralph-loop.local.md`
2. `SendMessage(type="shutdown_request")` to all active teammates (session-ops, bounty-agent, finality-agent).
3. Wait for shutdown confirmations (timeout: 30 seconds per agent, then force-proceed).
4. `TeamDelete("session-lifecycle")`.
5. Tell user: "Session closed. Soul purpose '[text]' archived." (Include token info if bounty was settled.)
