# Changelog

All notable changes to this project will be documented in this file.

## [3.1.0](https://github.com/anombyte93/atlas-session-lifecycle/compare/v3.0.0...v3.1.0) (2026-02-17)


### Features

* add /stop skill for graceful session close ([1c6f1f1](https://github.com/anombyte93/atlas-session-lifecycle/commit/1c6f1f15ff8b7211bdbf20cbe555bb60f332175c))
* add check-clutter command and reconcile cleanup step ([a9e8348](https://github.com/anombyte93/atlas-session-lifecycle/commit/a9e8348be7ce678a2e9421aebe6eee10882c2d67))
* bundle /stepback strategic reassessment skill ([1e307aa](https://github.com/anombyte93/atlas-session-lifecycle/commit/1e307aacbc2b11a92b5b3098511132874a4ace7b))
* enforce Agent Teams for work execution (not just session lifecycle) ([44af5aa](https://github.com/anombyte93/atlas-session-lifecycle/commit/44af5aa9d6b99911bb6e1748c6560e3939997ec9))
* interactive extra skills prompt in skill-mode installer ([9f3e170](https://github.com/anombyte93/atlas-session-lifecycle/commit/9f3e1709fd0083208b51fcacd65a55a6540b7349))
* v2.0 — session lifecycle management with reconcile mode and plugin structure ([7772bd9](https://github.com/anombyte93/atlas-session-lifecycle/commit/7772bd91008fe5412352b69bbce0e2aa3def2280))
* v3.0 — Agent Teams orchestration with AtlasCoin bounty verification ([c011aea](https://github.com/anombyte93/atlas-session-lifecycle/commit/c011aea1ffa43bc555df22eee573d8e563ac4e46))


### Bug Fixes

* address doubt findings in /stop skill ([3bbba54](https://github.com/anombyte93/atlas-session-lifecycle/commit/3bbba543a1bd43df2eb4334b2cc776eed508ec76))
* move permissions to workflow level for release-please caller ([dc3113f](https://github.com/anombyte93/atlas-session-lifecycle/commit/dc3113f3324d4943685bbca3c6c239a780c3ff40))
* move review-gate permissions to workflow level, trigger release-please with v1 tag ([c30e909](https://github.com/anombyte93/atlas-session-lifecycle/commit/c30e9091bb03fdad49f54cf733ab449ed9054608))
* use simple release-type for non-node project ([d5b4724](https://github.com/anombyte93/atlas-session-lifecycle/commit/d5b4724af536b830b0d9d59545f8801ef5964371))

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
