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
