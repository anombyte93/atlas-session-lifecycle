# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Project**: Atlas Session Lifecycle
**Goal**: MCP server for AI session lifecycle management — persistent memory, soul purpose tracking, and contract verification for Claude Code
**Stack**: Python 3.10+, FastMCP, FastAPI, HTMX, TailwindCSS, Playwright, pytest

---

## Architecture

### Modular Monolith Design

The MCP server (`src/atlas_session/server.py`) is a single FastMCP application with three tool domains:

1. **Session tools** (`session/`): Session lifecycle management (init, validate, read_context, harvest, archive, check_clutter, cache/restore_governance)
2. **Contract tools** (`contract/`): Bounty creation and verification with executable test criteria
3. **Stripe tools** (`stripe/`): License and payment processing (optional)

**Key pattern**: Stateless tools with file-based state management. All state lives in `session-context/` directories.

### MCP Tool Registration

FastMCP tools are registered via decorator functions in each domain's `tools.py`. The server entry point aggregates all domains:

```python
session_tools.register(mcp)
contract_tools.register(mcp)
stripe_tools.register(mcp)
```

### Deterministic Operations

Session operations use JSON-outputting subcommands in `session/operations.py`. Each operation returns structured JSON that the skill layer (SKILL.md) interprets.

### Contract/Bounty System

- Contracts define executable test criteria at creation time
- Verification just runs tests — no subjective judgment required
- Criteria types: `shell`, `context_check`, `file_exists`, `git_check`
- Local `session-context/contract.json` + optional AtlasCoin remote bounty

---

## Development Commands

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest tests/ --cov=atlas_session --cov-report=html

# Run single test file
pytest tests/unit/test_session_operations.py -v
```

### MCP Server

```bash
# Run MCP server (stdio - for Claude Code)
python -m atlas_session.server

# Run HTTP transport (for remote access)
python -m atlas_session.server --transport http

# Install for development
pip install -e ".[dev]"
```

### Linting/Formatting

```bash
# Lint
ruff check src/

# Format
ruff format src/

# Lint and format
ruff check --fix src/ && ruff format src/
```

### Web Dashboard

```bash
cd web
./run.sh
# Runs at http://127.0.0.1:8080
```

---

## Project Structure

```
src/atlas_session/     # MCP server package
├── server.py          # FastMCP server entry point
├── session/           # Session lifecycle tools
│   ├── tools.py       # MCP tool decorators
│   └── operations.py  # Deterministic JSON operations
├── contract/          # Bounty/contract tools
│   ├── tools.py       # MCP tool decorators
│   ├── model.py       # Contract/Criterion dataclasses
│   ├── verifier.py    # Test execution logic
│   └── atlascoin.py   # AtlasCoin API client
├── stripe/            # License/payment tools
└── common/            # Shared utilities

web/                   # FastAPI + HTMX dashboard
├── app.py             # FastAPI app
├── templates/         # Jinja2 templates
└── static/            # CSS/JS assets

skills/                # Claude Code skills (/.claude/skills/)
├── start/SKILL.md     # Main /start skill orchestrator
├── stop/SKILL.md      # /stop skill
├── stepback/SKILL.md  # /stepback skill
└── sync/SKILL.md      # /sync skill

templates/             # Immutable session file templates
├── CLAUDE-activeContext.md
├── CLAUDE-decisions.md
├── CLAUDE-patterns.md
├── CLAUDE-soul-purpose.md
└── CLAUDE-troubleshooting.md

tests/                 # Test suite
├── unit/              # Unit tests for operations/models
├── integration/       # MCP protocol & lifecycle flows
└── e2e/               # Playwright dashboard tests

scripts/               # Installation & utility scripts
```

---

## Session Context Files

The five-file memory bank lives in `session-context/`:

| File | Purpose |
|------|---------|
| `CLAUDE-activeContext.md` | Current session state, goals, progress |
| `CLAUDE-decisions.md` | Architecture decisions and rationale |
| `CLAUDE-patterns.md` | Established code patterns and conventions |
| `CLAUDE-troubleshooting.md` | Common issues and proven solutions |
| `CLAUDE-soul-purpose.md` | Soul purpose definition and completion criteria |

**Entry Format**:
```markdown
## HH:MM DD/MM/YY
### REASON
Who:
What:
When:
Where:
Why:
How:
References:
Git Commit:
Potential Issues to face:
```

---

## Structure Maintenance Rules

- **CLAUDE.md** stays at root (Claude Code requirement)
- **Session context** files live in `session-context/` — NEVER at root
- **Scripts** go in `scripts/<category>/`
- **Documentation** goes in `docs/<category>/`
- **Config** files go in `config/` unless framework-required at root
- **Logs** go in `logs/`

---

## Installation

```bash
# Skill mode (default)
curl -fsSL https://raw.githubusercontent.com/anombyte93/atlas-session-lifecycle/main/install.sh | bash

# Plugin mode
curl -fsSL ... | bash -s -- --plugin

# Update
bash install.sh --update
```

---

## Security Considerations

- **Command allowlist**: Contract shell commands restricted to allowlist (git, python3, npm, etc.)
- **Path validation**: All `project_dir` parameters resolved via `Path.resolve()` to prevent traversal attacks
- **HMAC-signed tokens**: License tokens use SHA-256 HMAC to prevent bypass
- **Commit pinning**: Installer uses specific commit hashes for reproducible installs

See `session-context/CLAUDE-decisions.md` for full security architecture decisions.

---

## MCP Configuration

Claude Code uses `~/.claude.json` (NOT `~/.claude/mcp_config.json`) for MCP server registration.

```bash
# Add MCP server (global scope)
claude mcp add -s user atlas-session python -m atlas_session.server

# Add MCP server (project scope)
claude mcp add -s local atlas-session python -m atlas_session.server

# List MCP servers
claude mcp list
```

---

## CI/CD

- **ci.yml**: Tests on Python 3.10/3.11/3.12
- **publish.yml**: Package publishing to PyPI
- **claude-review.yml**: Claude Code review automation
- **release-please.yml**: Automated releases
- **review-gate.yml**: PR review gating

---

## Soul Purpose Lifecycle

```
Define --> Work --> Reconcile --> Assess --> Close or Continue
```

**Key invariant**: The AI never closes a soul purpose. It assesses and suggests; the user decides.

See `/start` skill (`skills/start/SKILL.md`) for full lifecycle orchestration.

---

## IMMUTABLE TEMPLATE RULES

> **DO NOT** edit the template files in `templates/`.
> Templates are immutable source-of-truth. Only edit the copies in your project.
