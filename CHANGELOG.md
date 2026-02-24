# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0](https://github.com/anombyte93/atlas-session-lifecycle/compare/v3.0.0...v3.1.0) (2026-02-24)


### Features

* /start and /stop now run /sync first ([8c4cbc5](https://github.com/anombyte93/atlas-session-lifecycle/commit/8c4cbc5ff1dedb682a56cabac5f1966bc6a3db24))
* add /stop skill for graceful session close ([1c6f1f1](https://github.com/anombyte93/atlas-session-lifecycle/commit/1c6f1f15ff8b7211bdbf20cbe555bb60f332175c))
* add /sync skill — fast zero-question save-point ([a8cc365](https://github.com/anombyte93/atlas-session-lifecycle/commit/a8cc365ec8148a887467d5ee5402a5f62625443c))
* add capability inventory for /start reconcile mode ([7d2c690](https://github.com/anombyte93/atlas-session-lifecycle/commit/7d2c6909578552d50949d773aa276ce3e7250a0e))
* add check-clutter command and reconcile cleanup step ([a9e8348](https://github.com/anombyte93/atlas-session-lifecycle/commit/a9e8348be7ce678a2e9421aebe6eee10882c2d67))
* add composite MCP tools (session_start, session_activate, session_close) ([08d4eb6](https://github.com/anombyte93/atlas-session-lifecycle/commit/08d4eb626cf9907fb931a9fcbd8e3575569bd80f))
* add landing page for GitHub Pages ([76fd6a1](https://github.com/anombyte93/atlas-session-lifecycle/commit/76fd6a161e349177241433dda80c9e3c38b87846))
* add license management module — activate, revoke, validate ([f54cdcd](https://github.com/anombyte93/atlas-session-lifecycle/commit/f54cdcd6cf89ce24936f54bee33cb73fe7466c77))
* add stripe as optional dependency ([a3eb5c1](https://github.com/anombyte93/atlas-session-lifecycle/commit/a3eb5c12c7b32d58cfe5217b04d7e7432549de74))
* add Stripe setup documentation and complete Stripe integration ([18ef2ed](https://github.com/anombyte93/atlas-session-lifecycle/commit/18ef2ed8091e8579baa5e9ba6ce702ff2d323d1a))
* bring MCP server source into repo + add 5 new session tools ([26573cb](https://github.com/anombyte93/atlas-session-lifecycle/commit/26573cb6e0458eee0db14ca73b4bcc95171efaf4))
* bundle /stepback strategic reassessment skill ([1e307aa](https://github.com/anombyte93/atlas-session-lifecycle/commit/1e307aacbc2b11a92b5b3098511132874a4ace7b))
* complete productization — landing page, Stripe, Cline marketplace, PyPI workflow ([7122580](https://github.com/anombyte93/atlas-session-lifecycle/commit/712258012d9aec56b84bf680c436330344302c9c))
* complete productization — landing page, Stripe, Cline marketplace, PyPI workflow ([7840ec9](https://github.com/anombyte93/atlas-session-lifecycle/commit/7840ec97c84d6638dd58af88526a205eeb878de3))
* complete Trello card requirements ([7d9e2fb](https://github.com/anombyte93/atlas-session-lifecycle/commit/7d9e2fb1fc6e84db1671789655b3b94b8822b738))
* create test-spec-gen skill directory structure ([d5996cf](https://github.com/anombyte93/atlas-session-lifecycle/commit/d5996cf54135aa054e050d8ecc5bf8107d4a03d9))
* enforce Agent Teams for work execution (not just session lifecycle) ([44af5aa](https://github.com/anombyte93/atlas-session-lifecycle/commit/44af5aa9d6b99911bb6e1748c6560e3939997ec9))
* interactive extra skills prompt in skill-mode installer ([9f3e170](https://github.com/anombyte93/atlas-session-lifecycle/commit/9f3e1709fd0083208b51fcacd65a55a6540b7349))
* MCP server source control + 5 new session tools ([9099f06](https://github.com/anombyte93/atlas-session-lifecycle/commit/9099f06dc0358b6893e7c1aa24244e09ee69e057))
* Python CI + production pyproject.toml ([7c27d89](https://github.com/anombyte93/atlas-session-lifecycle/commit/7c27d89ef499c93bbf79c1455fe01ac651d9f499))
* rewrite /start SKILL.md — MCP-first, 266 lines ([a8e6bdf](https://github.com/anombyte93/atlas-session-lifecycle/commit/a8e6bdf045bad2eacdd081c79f1336043462c651))
* rewrite /start SKILL.md — MCP-first, 464→266 lines ([237e20e](https://github.com/anombyte93/atlas-session-lifecycle/commit/237e20eacef7c03ddd63863124a8c414d8a00f1d))
* rewrite /stop SKILL.md — MCP-first, 3-intent, 156 lines ([d3ad590](https://github.com/anombyte93/atlas-session-lifecycle/commit/d3ad590e62eeebeb8e4fd0433b19850061bbaf1f))
* track session-context knowledge files in git ([c4c48a1](https://github.com/anombyte93/atlas-session-lifecycle/commit/c4c48a14509c053ca8888c244e79d98e2e40ccc8))
* v2.0 — session lifecycle management with reconcile mode and plugin structure ([7772bd9](https://github.com/anombyte93/atlas-session-lifecycle/commit/7772bd91008fe5412352b69bbce0e2aa3def2280))
* v3.0 — Agent Teams orchestration with AtlasCoin bounty verification ([c011aea](https://github.com/anombyte93/atlas-session-lifecycle/commit/c011aea1ffa43bc555df22eee573d8e563ac4e46))
* wire up atlas-license CLI entry point ([6af0586](https://github.com/anombyte93/atlas-session-lifecycle/commit/6af0586cdc8b45a0ebf068338eb225f50d1a8a13))


### Bug Fixes

* add test compatibility + extend command allowlist ([6a276ef](https://github.com/anombyte93/atlas-session-lifecycle/commit/6a276ef5f2e251a835e95a028dc0a8714d4068f7))
* address doubt findings in /stop skill ([3bbba54](https://github.com/anombyte93/atlas-session-lifecycle/commit/3bbba543a1bd43df2eb4334b2cc776eed508ec76))
* install stripe extras in CI for test coverage ([dd21771](https://github.com/anombyte93/atlas-session-lifecycle/commit/dd217713bb64b9c29405407645f34bad4abc659e))
* landing page rewrite - show WHY users need this ([3de92fc](https://github.com/anombyte93/atlas-session-lifecycle/commit/3de92fc4710e29e9de661fa8ee08bf1eab3c40da))
* make Stripe truly optional dependency ([1a6f208](https://github.com/anombyte93/atlas-session-lifecycle/commit/1a6f208522787d6877a399042b2bf212669cb4ae))
* move permissions to workflow level for release-please caller ([dc3113f](https://github.com/anombyte93/atlas-session-lifecycle/commit/dc3113f3324d4943685bbca3c6c239a780c3ff40))
* move review-gate permissions to workflow level, trigger release-please with v1 tag ([c30e909](https://github.com/anombyte93/atlas-session-lifecycle/commit/c30e9091bb03fdad49f54cf733ab449ed9054608))
* production readiness — security, versions, CI signals, docs ([a7822c3](https://github.com/anombyte93/atlas-session-lifecycle/commit/a7822c3ce08a33ee8ca6b7fa71fa70cb55a338b6))
* read_context parser checked full file for "(No active soul purpose)" ([29979b7](https://github.com/anombyte93/atlas-session-lifecycle/commit/29979b75dbd981c8ebbcd5108cc87197d07da48b))
* remove mcp-cli dependencies, fix subagent_type bug ([84b63f7](https://github.com/anombyte93/atlas-session-lifecycle/commit/84b63f707b3d8a744c376d7af7c8c2448cdfe074))
* remove unused variable in stripe_client.py ([b98a829](https://github.com/anombyte93/atlas-session-lifecycle/commit/b98a829103ae2b9bc6e4b6d58e73a434013813aa))
* resolve 4 remaining known bugs — binary crash, None crash, archive destruction, non-dict JSON ([d5f3f32](https://github.com/anombyte93/atlas-session-lifecycle/commit/d5f3f328d72a57a55bf07651d6b1e6c049b6448b))
* restore workflow file to match main branch ([dde3fc5](https://github.com/anombyte93/atlas-session-lifecycle/commit/dde3fc5e3106aba02b15e4b808b75a93857a42e5))
* **security:** remove shell injection — shlex.split replaces shell=True ([6817280](https://github.com/anombyte93/atlas-session-lifecycle/commit/68172808835b2caa5ce10340d77372044ed600c1))
* test compatibility for security changes ([c03f590](https://github.com/anombyte93/atlas-session-lifecycle/commit/c03f590a4c40e8a6c0d3a4ecfe56a178e069ce4c))
* use simple release-type for non-node project ([d5b4724](https://github.com/anombyte93/atlas-session-lifecycle/commit/d5b4724af536b830b0d9d59545f8801ef5964371))

## [Unreleased]

### Security
- HMAC secret reads from `ATLAS_HMAC_SECRET` env var (no more hardcoded default in production)
- Path traversal protection in `_resolve_project_dir()` — rejects paths outside `$HOME` and `/tmp`

### Added
- CI provider detection (`has_ci`, `ci_provider`) in project signals
- Pre-commit hooks configuration (ruff, trailing-whitespace, check-yaml/json)
- Capability inventory for `/start` reconcile mode

### Changed
- Version numbers unified to 4.1.0 across all files
- `stripe_client.py` imports `_HMAC_SECRET` from `license.py` (single source of truth)
- Business strategy docs untracked from git (kept on disk)

### Fixed
- `install.sh` pinned commit trimmed from malformed `8c4cbc5feat-productization` to `8c4cbc5`
- Test compatibility for security changes

## [4.1.0] - 2026-02-18

### Added
- Stripe integration — checkout, webhooks, license refresh, customer validation (5 tools)
- Landing page for GitHub Pages
- Stripe setup documentation
- Capability inventory tool (`session_capability_inventory`)

### Changed
- Stripe is a truly optional dependency
- `pyproject.toml` formatted — optional dependencies moved to end

### Fixed
- Landing page rewrite — shows WHY users need this
- Unused variable removed in `stripe_client.py`
- Workflow file restored to match main branch
- Stripe extras installed in CI for test coverage

### Security
- 7 issues fixed from Claude Code Review
- Test compatibility extended for security changes
- Command allowlist extended

## [4.0.0] - 2026-02-17

### Added
- `/start` and `/stop` now run `/sync` first
- CI triggers on feature branches + `workflow_dispatch`
- `atlas-license` CLI entry point wired up
- License management module — activate, revoke, validate
- Python CI + production `pyproject.toml`

### Changed
- Reusable CI, review, and release-please workflows from `anombyte93/copilot@v1`
- `/ralph-go` replaces Ralph questions in `/start` skill

### Fixed
- 4 remaining known bugs — binary crash, None crash, archive destruction, non-dict JSON

### Security
- Shell injection removed — `shlex.split` replaces `shell=True`

## [3.0.0] - 2026-02-16

### Added
- MCP server source brought into repo + 5 new session tools
- `/start` SKILL.md rewrite — MCP-first, 464 to 266 lines
- `/stop` SKILL.md rewrite — MCP-first, 3-intent, 156 lines
- `/sync` skill — fast zero-question save-point
- Comprehensive test suite — 196 tests covering all 23 MCP tools
- 13 edge case tests for verifier, read_context, clutter
- Agent Teams orchestration with AtlasCoin bounty verification
- `/stop` skill for graceful session close
- `check-clutter` command and reconcile cleanup step
- Interactive extra skills prompt in installer
- Bundled `/stepback` strategic reassessment skill
- `custom.md` documentation with concrete examples

### Changed
- Hostile testing rewrite — deleted 28 tautological tests, added 31 hostile tests
- Agent Teams enforced for work execution (not just session lifecycle)

### Fixed
- `read_context` parser checked full file for "(No active soul purpose)"
- Doubt findings addressed in `/stop` skill
- Simple release-type for non-node project
- Review-gate permissions moved to workflow level

## [2.0.0] - 2026-02-14

### Added
- **Reconcile Mode**: Returning session detection with soul purpose completion assessment
- **Soul Purpose Lifecycle**: init -> work -> reconcile -> harvest -> close/continue
- **Active Context Harvesting**: Promote decisions, patterns, troubleshooting on closure
- **Governance Caching**: Cache CLAUDE.md sections before Claude /init, restore after
- **Plugin Format**: `.claude-plugin/` structure for plugin installation
- **custom.md**: Extensibility hook for init/reconcile customization
- **Auto-Update Check**: Non-blocking notification when new version available
- **Deterministic Backend**: Python script handles all file I/O, outputs JSON
- **Dual-Mode Installer**: Supports both skill and plugin installation
- **Stepback Skill**: Bundled `/stepback` strategic reassessment protocol for debugging loops

### Changed
- SKILL.md refactored into thin orchestrator (320 lines) + Python backend (664 lines)
- Templates resolve from plugin-relative path with home directory fallback
- Install script supports both `~/.claude/skills/` and `~/.claude/plugins/` targets
- Repository renamed from `claude-session-init` to `atlas-session-lifecycle`
- File structure reorganized: `skills/start/SKILL.md`, `scripts/session-init.py`

### Migration from v1
- v1 SKILL.md preserved in `v1/` directory
- `install.sh --version v1` still available
- `install.sh --revert` to downgrade

## [1.0.0] - 2025-06-15

### Added
- Initial `/start` skill with session bootstrapping
- Template-based session context files (5-file memory bank)
- File organization for cluttered project roots
- CLAUDE.md generation with governance sections
- Soul purpose capture and tracking
- Ralph Loop onboarding
