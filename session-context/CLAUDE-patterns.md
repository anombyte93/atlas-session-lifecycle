# Code Patterns

## 07:08 19/02/26
Security patterns established:

1. **HMAC signature pattern**:
   ```python
   def _sign_token(customer_id: str, expiry: float) -> str:
       message = f"{customer_id}:{expiry}".encode()
       return hmac.new(_HMAC_SECRET, message, hashlib.sha256).hexdigest()
   ```

2. **Command validation pattern**:
   ```python
   def _validate_command(command: str) -> tuple[bool, str | None]:
       if _SHELL_METACHARACTERS.search(command):
           return False, f"Command contains shell metacharacters: {command}"
       parts = shlex.split(command)
       cmd_name = Path(parts[0]).name
       if cmd_name not in _ALLOWED_COMMANDS:
           return False, f"Command '{cmd_name}' not in allowlist"
       return True, None
   ```

3. **Path resolution pattern**:
   ```python
   def _resolve_project_dir(project_dir: str) -> Path:
       path = Path(project_dir).resolve()
       if not path.is_dir():
           raise ValueError(f"Not a directory: {project_dir}")
       return path
   ```

## 10:55 19/02/26

4. **Git-based cache invalidation pattern**:
   ```python
   def capability_inventory(project_dir, force_refresh=False):
       git_head = _get_git_head(project_dir)
       cache = _load_capability_cache(project_dir) if git_head else None
       cache_hit = cache and cache.get("git_head") == git_head and not force_refresh
       if not cache_hit:
           _save_capability_cache(project_dir, {"git_head": git_head, ...})
       return {"cache_hit": cache_hit, "needs_generation": not cache_hit}
   ```

5. **Claude Code MCP registration pattern**:
   ```bash
   # Global (all projects): -s user
   claude mcp add -s user --transport stdio <name> --env KEY=val -- node /path/to/index.js
   # Project-scoped: -s local
   claude mcp add -s local --transport stdio <name> -- node /path/to/index.js
   ```

## 15:44 19/02/26

6. **Reusable workflow calling pattern** (Atlas-Copilot):
   ```yaml
   jobs:
     ci:
       uses: anombyte93/atlas-copilot/.github/workflows/reusable-ci.yml@v1
       with:
         node-version: '22'
         test-command: 'pytest tests/ -x'
   ```

7. **Phase tracking hook pattern** (statusline integration):
   ```bash
   # ~/.claude/hooks/phase-tracker.sh
   # Reads hook JSON from stdin, writes to ~/.claude/state/phase-{PANE_ID}.json
   # Statusline reads state file, shows [phase] if timestamp < 5s old
   PANE_ID=$(tmux display-message -p '#{pane_id}' 2>/dev/null | tr -d '%' || echo "0")
   PHASE_FILE="$HOME/.claude/state/phase-${PANE_ID}.json"
   ```

## 21:09 19/02/26

8. **Ralph Loop stop hook pattern**: The `ralph-loop-stop.sh` hook intercepts exit attempts, checks `.claude/ralph-loop.local.md` state file, parses iteration/completion promise from YAML frontmatter, and either (a) removes state file and allows exit if completion promise matched, or (b) increments iteration and blocks exit with JSON response containing original prompt to continue. This enables self-referential loop where Claude sees previous work in files/git.

9. **Jinja2 environment with FileSystemLoader**: For FastAPI templating, use `Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=select_autoescape(['html', 'xml'])` to enable template inheritance (`{% extends "base.html" %}`) and avoid loader errors when rendering templates.

## 21:29 19/02/26

10. **Hook conflict diagnosis pattern**:
```bash
# Check all registered Stop hooks
find ~/.claude -name hooks.json -exec grep -l '"Stop"' {} \;
# Verify plugin execution order
claude plugin list | sort
# Add physical proof logging for debugging
echo "RALPH STOP FIRED $(date)" >> ~/.claude/hook-debug.log
```

11. **Hook short-circuit visibility problem**: Hooks fail silently. If hookify exits 0, Ralph never runs. No error message — just silent bypass. Always add artifact logging (`echo >> log`) when debugging lifecycle hooks.

## 11:30 21/02/26

12. **MCP tool discovery via ToolSearch**: Instead of relying on external tools like mcp-cli (archived), use Claude Code's built-in ToolSearch tool to discover available MCP tools before using them.

13. **Custom agent behavior via general-purpose**: To create "doubt-agent" or other custom agent behaviors, use `Task(subagent_type="general-purpose", prompt="You are a doubt-agent. [full instructions]")` instead of non-existent subagent_type values.

14. **Backpressure gate hierarchy**: Deterministic gates (types → lint → unit tests → contract tests → integration → E2E) run first and are script-verifiable. Agentic gates (judgment-based review) run only after deterministic gates pass. This ensures AI output quality before human review.

15. **Stop hook continuation pattern**: Hook reads transcript, checks state file, and either (a) allows exit or (b) outputs JSON `{"decision": "block", "reason": "prompt text", "systemMessage": "iteration info"}` to continue loop. This enables self-referential iteration where each loop sees previous work in files/git.

## 20:24 21/02/26
16. **Multi-agent orchestration for test specification**: 5 parallel Explore agents (routes, auth, data, framework, UX) → Research agent (perplexity/context7) → 5 parallel Specialist agents (one per domain) → Doubt agent → Finality agent. Total 13+ agents, 3 sequential phases with parallel execution within phases.
17. **TC-XXX test case format**: Standardized test case format with Area, Priority, Preconditions, Test Steps, Expected Outcome, Pass Criteria, Notes. Used across all specialist outputs for consistency.
18. **Template-based document assembly**: Load test-spec.md template → Replace simple placeholders ({PROJECT_NAME}, {DATE}) → Insert complex outputs ({SPECIALIST_OUTPUTS}) → Generate traceability matrix → Save to output path.
19. **Fallback domain pattern**: When research doesn't yield 5 test domains, use fallback: UI Component Testing, User Flow Testing, Error Handling & Edge Cases, Data Integrity & CRUD, Access Control & Security.

## 11:53 21/02/26
20. **Soul loop stop hook pattern**: Hook reads state file → checks critical gates (max iterations, corruption) → runs quality gates (tests, feature proofs) → checks progressive gate (5 warn, 10 stop) → checks agentic gate (promise tag) → either allows exit or blocks with continuation prompt. Updates iteration counter at end of each turn.
21. **Progressive friction implementation**: Use simple line-count failure counter (one line per failure). Check with `wc -l`. At 5 failures, warn user. At 10 failures, hard stop. This creates increasing friction without blocking legitimate debugging.
22. **Promise tag detection in transcripts**: Greedy search through transcript JSON for `<promise>PROMISE_TEXT</promise>` tag. Try multiple grep patterns since JSON formats vary (compact vs pretty-printed). Allow exit only on exact match with configured completion_promise.

## 12:38 21/02/26
23. **MCP availability check pattern**: `claude mcp list | grep "server-name"` to verify connection status before attempting to use MCP tools. Look for "✓ Connected" vs "✗ Failed" or missing entry.
24. **Gate configuration from project structure**: Dynamically enable soul-loop gates based on directory existence (tests/e2e/ for e2e gate) or config files (config/trello-testing.json for acceptance gate). Base gates always enabled: research,deterministic.
25. **Auto-invocation pattern**: /start detects code keywords in soul purpose (implement, build, fix, add, create, refactor, update, write) → determines intensity from task size → invokes /soul-loop with --gates flag.

## 13:57 21/02/26
No new patterns this session.


## 15:02:21 21/02/26
No new patterns this session.
