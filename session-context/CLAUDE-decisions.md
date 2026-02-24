# Architecture Decisions

## 07:08 19/02/26
Security-first architecture decisions:

1. **HMAC-signed license tokens**: Moved from mtime-based cache to HMAC-signed tokens to prevent trivial bypass via `touch()`. Uses customer_id + expiry as message payload with SHA-256 HMAC.

2. **Command allowlist**: Contract shell commands now restricted to allowlist (git, python3, npm, etc.) to prevent arbitrary command execution via MCP tool parameters.

3. **Path resolution validation**: All project_dir parameters resolved through Path.resolve() to prevent `../` traversal attacks.

4. **Installer commit pinning**: Git clones now use specific commit hashes instead of `main` HEAD for reproducible, verifiable installations.

5. **Semver validation**: GitHub API responses validated with regex before use in python3 -c to prevent shell injection.

6. **Secure tempfile**: Replaced predictable /tmp filename with tempfile.NamedTemporaryFile for random, unlink-on-close behavior.

7. **Stripe webhook docs**: Added SECURITY documentation emphasizing raw byte-exact requirement for HMAC verification.

## 10:55 19/02/26

8. **Capability inventory as cached MCP tool**: Implemented as `session_capability_inventory` MCP tool with git HEAD-based cache invalidation. Cache stored in `session-context/.capability-cache.json`. Non-git projects always regenerate. Design keeps the MCP tool responsible for cache logic while the skill layer (SKILL.md) decides when to invoke.

9. **MCP server registration via CLI not JSON**: Discovered Claude Code uses `~/.claude.json` (via `claude mcp add`), NOT `~/.claude/mcp_config.json`. The latter is ignored. Always use `claude mcp add -s user` for global scope, `-s local` for project scope.

10. **Perplexity MCP server as dedicated private repo**: Moved from `/opt/perplexity/` to `/home/anombyte/Hermes/Projects/perplexity-mcp-server` with proper git tracking, main/develop branching, and one-shot install script.

## 15:44 19/02/26

11. **Atlas-Copilot positioning vs SaaS competitors**: Differentiated on self-hosted, free (BYO API key), no vendor lock-in. CodeRabbit ($12-24/user/mo) and Graphite ($20-40/user/mo) are SaaS with code sent to external infrastructure. Atlas-Copilot runs in user's GitHub with their own Anthropic API key — code never leaves their infrastructure.

12. **CI/CD scaffold detection "just works"**: Integrated into /start Init Step 3 with smart skip logic — only prompts when: code files exist, package manifest present, no existing CI. Skips simple scripts, toy projects, and projects with CI. Follows "zero friction" UX principle.

13. **Phase tracking via hooks for statusline display**: Created `phase-tracker.sh` hook that tracks /start and atlas-session operation phases. Statusline shows `[phase]` in color-coded brackets (lavender for /start, sapphire for session). Auto-clears after 5 seconds to prevent stale display.

## 21:09 19/02/26

14. **Ralph Loop vs quick-clarify separation**: Ralph Loop is for iterative development (self-referential, fed same prompt repeatedly). quick-clarify is a pre-work brainstorming skill (3 questions: deliverable, done criteria, size). Converted ralph-go → quick-clarify to avoid confusion — Ralph is now purely invoked via `/ralph-loop` command, not through skill questions.

15. **Web dashboard tech stack: FastAPI + HTMX + TailwindCSS**: Chose for Atlas Session Dashboard because FastAPI is already the MCP server framework, HTMX enables server-driven UI without complex JavaScript, and TailwindCSS provides rapid styling. All Python, no build step, perfect for internal admin tooling.

## 21:29 19/02/26

16. **Hook precedence is deterministic (alphabetical plugin load order)**: Claude Code executes hooks in plugin registration order. First hook to exit 0 allows the action — subsequent hooks never run. This means if hookify registers a Stop hook that exits 0, Ralph Loop's Stop hook never gets to block termination.

17. **Lifecycle hooks must be exclusive or explicitly ordered**: When multiple plugins register the same lifecycle hook, execution order matters. A permissive early hook shadows restrictive later hooks. Solution: either single Stop broker plugin or explicit priority config.

## 11:30 21/02/26

18. **MCP CLI is archived and redundant**: The mcp-cli tool referenced in test-spec-gen skill is no longer maintained. MCP tool discovery should use ToolSearch (built-in to Claude Code) or direct file reads (~/.claude/mcp_config.json or ~/.claude.json). All mcp-cli references must be removed.

19. **Subagent types are validated at runtime**: "doubt-agent" is not a valid subagent_type for Task tool. Valid types are: Explore, general-purpose, Plan, etc. For custom agent behavior, use subagent_type="general-purpose" with a prompt that specifies the role.

## 12:06 21/02/26

20. **Soul-purpose skill as backpressure enforcement system**: The skill itself is the backpressure layer — it ensures deterministic constraints (types, linting, tests, CI/CD) are in place before AI begins generating output. /start bootstraps the enforcement system, /stop verifies through deterministic gates before agentic review.

21. **Deterministic first, agentic second for soul loop**: Following Huntley's backpressure pyramid, soul loop should enforce deterministic gates (max iterations, state validation, feature proofs, test suite) before agentic gates (completion promise, soul purpose fulfillment). 90% of problems caught by deterministic checks, 10% by judgment.

## 20:24 21/02/26
22. **Meta self-test validation via adapted domains**: When applying test-spec-gen to itself (a skill, not a web app), the standard discovery domains (Routes, Auth, Database, Framework, UX) are not applicable. Adapted domains are: Skill Discovery & Configuration, Agent Orchestration & Parallel Execution, Research Integration & Domain Determination, Test Specification Generation & Assembly, Verification & Integration.
23. **Circular testing paradox acknowledged**: Meta self-testing of a test generation skill creates circular validation (testing doubt agents with doubt agents). This is inherent to dogfooding and must be acknowledged as a limitation, not "solved."
24. **Semantic vs absolute references for maintainability**: Doubt agent identified line number references as high-maintenance (65% invalidation rate). Migration to semantic references (Phase X section vs line Y) reduces fragility when SKILL.md is edited.

## 11:53 21/02/26
25. **Soul Loop plugin as separate backpressure enforcement system**: Created soul-loop as a separate plugin (not part of soul-purpose skill) to enable independent lifecycle and reusability. Uses state file at session-context/soul-loop-state.md with YAML frontmatter for iteration tracking.
26. **Hierarchical gate design for backpressure**: Critical (hard block: max iterations, corruption, 10+ failures), Quality (soft warning: test failures, feature proof failures), Progressive (friction: 5+ failures warn, 10+ hard stop), Agentic (allow exit: completion promise matched). This follows Huntley's "Engineering Backpressure" — deterministic first (90%), agentic second (10%).
27. **Promise tag for graceful loop termination**: User outputs `<promise>EXACT_TEXT</promise>` to exit soul loop early. Hook scans transcript JSON for matching promise tag. Enables human-controlled completion condition within enforced iteration constraints.

## 12:38 21/02/26
28. **Blocking MCP check in /start prevents silent failures**: Added `claude mcp list | grep "atlas-session"` check in both Init and Reconcile modes. If MCP is not connected, /start STOPS immediately with clear error message instead of attempting "AI slop" fallback behavior.
29. **Extended soul loop gates for hierarchical enforcement**: Added --gates flag to soul-loop setup script. New gates: research (test-spec-gen), e2e (playwright tests), acceptance (trello-test). Gates configured from project structure (tests/e2e/, config/trello-testing.json).
30. **Auto-invocation of soul-loop from /start**: When soul purpose involves code keywords (implement, build, fix, add, create, refactor, update, write), /start automatically invokes /soul-loop with intensity from task size and gates from project structure.

## 13:57 21/02/26
No new decisions this session.


## 15:02:21 21/02/26
No new decisions this session.
