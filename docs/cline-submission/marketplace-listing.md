# Marketplace Listing: Atlas Session Lifecycle

**Submission for:** Cline AI Extension Marketplace

---

## Extension Metadata

| Field | Value |
|-------|-------|
| **Name** | Atlas Session Lifecycle |
| **Display Name** | Atlas Session Lifecycle |
| **Description** | Persistent project memory and session lifecycle management |
| **Short Description** | 5-file memory bank, auto file organization, soul purpose tracking |
| **Version** | 3.0.0 |
| **Author** | Atlas AI (https://atlas-ai.au) |
| **Repository** | https://github.com/anombyte93/atlas-session-lifecycle |
| **License** | MIT |
| **Category** | Developer Tools / Productivity |

---

## Keywords (comma-separated)

session, lifecycle, init, persistent-memory, context-management, project-management, claude-code, cline, ai-assistant, soul-purpose, file-organization, session-management

---

## Detailed Description

### The Problem

AI coding assistants have no persistent memory between sessions. Every new conversation starts from zero. This creates three compounding problems:

1. **No persistent memory** -- Context, decisions, and progress are lost between sessions. You re-explain the same things every time.
2. **Project sprawl** -- Files accumulate at the project root with no organization. Scripts, docs, configs, and logs pile up across sessions.
3. **No lifecycle management** -- Projects have goals, but no mechanism to track progress, verify completion, or transition to new objectives.

### The Solution

`/start` solves all three with a structured five-file memory bank, automatic file organization, and a soul purpose lifecycle that tracks your project from inception through completion.

### How It Works

```
/start
  |
  +-- session-context/ exists? --> Reconcile Mode
  |                                  +-- Validate & repair session files
  |                                  +-- Refresh project context
  |                                  +-- Self-assess soul purpose status
  |                                  +-- Offer: Continue / Close / Redefine
  |
  +-- No session-context/ -------> Init Mode
                                     +-- Capture soul purpose
                                     +-- Bootstrap 5-file memory bank
                                     +-- Organize root files
                                     +-- Generate project CLAUDE.md
```

### Session Memory Bank

Five files in `session-context/` give your AI persistent memory across sessions:

| File | Purpose |
|------|---------|
| `CLAUDE-activeContext.md` | Current session state, goals, and progress |
| `CLAUDE-decisions.md` | Architecture decisions and rationale |
| `CLAUDE-patterns.md` | Established code patterns and conventions |
| `CLAUDE-troubleshooting.md` | Common issues and proven solutions |
| `CLAUDE-soul-purpose.md` | Soul purpose definition and completion criteria |

### Included Commands

- `/start` -- Main session lifecycle orchestrator
- `/stop` -- Session closure with context harvesting
- `/sync` -- Update session files with current progress
- `/stepback` -- Strategic reassessment for stuck debugging

---

## Screenshots / Demos

### Screenshot 1: Init Mode
```
[Description] First run in a new project. The skill captures the soul purpose,
organizes scattered files, and bootstraps the session memory bank.

[Suggested screenshot content]
- Terminal showing `/start` command
- Question: "What is this project's soul purpose?"
- File organization proposal
- Session-context directory being created
```

### Screenshot 2: Reconcile Mode
```
[Description] Returning to an existing project. The skill validates state,
refreshes context, and offers lifecycle options.

[Suggested screenshot content]
- Terminal showing reconnect message
- Soul purpose display
- Progress assessment
- Options: Continue / Close / Redefine
```

### Screenshot 3: Memory Bank Contents
```
[Description] The five session memory files with structured entries.

[Suggested screenshot content]
- session-context/ directory listing
- Sample CLAUDE-decisions.md with architecture decisions
- Sample CLAUDE-patterns.md with code conventions
```

---

## Installation Instructions (for Marketplace)

### Option 1: One-line Install
```bash
curl -fsSL https://raw.githubusercontent.com/anombyte93/atlas-session-lifecycle/main/install.sh | bash
```

### Option 2: Manual Install
```bash
# Clone the repository
git clone https://github.com/anombyte93/atlas-session-lifecycle.git
cd atlas-session-lifecycle

# Run the installer
./install.sh
```

### After Installation
Run `/start` in any project to begin.

---

## Compatibility

| Platform | Status |
|----------|--------|
| Claude Code | ✅ Fully supported |
| Cline | ✅ Compatible |
| Other AI assistants | ⚠️ May require adaptation |

---

## Changelog Highlights

### v3.0.0 (Current)
- Agent Teams-based session coordination
- AtlasCoin bounty verification integration
- Enhanced settlement flow with code review gates

### v2.0.0
- Extracted deterministic operations to Python script
- Reduced SKILL.md to slim orchestrator
- Added Ralph Loop integration

### v1.0.0
- Initial release with monolithic SKILL.md

---

## Support

- **Issues**: https://github.com/anombyte93/atlas-session-lifecycle/issues
- **Discussions**: https://github.com/anombyte93/atlas-session-lifecycle/discussions
- **Documentation**: https://github.com/anombyte93/atlas-session-lifecycle/blob/main/README.md

---

## Marketing Copy (Short)

### Tagline
"Give your AI assistant a memory. Keep your projects organized."

### 140-character description
"Persistent 5-file memory bank, auto file organization, and soul purpose lifecycle for AI coding sessions. Never re-explain your project again."

### Featured badge
"Featured in: [I just delivered on a $30,000 contract thanks to Claude Code](https://www.reddit.com/r/ClaudeAI/comments/1r0n1qz/i_just_delivered_on_a_30000_contract_thanks_to/)"

---

## Additional Assets

| Asset | Location |
|-------|----------|
| Icon | `docs/cline-submission/icon.png` (128x128px) |
| Banner | `docs/cline-submission/banner.png` (1280x640px) |
| Screenshots | `docs/cline-submission/screenshots/` |

---

## Submission Checklist

- [x] llms-install.md created
- [x] Marketplace listing prepared
- [x] Installation instructions verified
- [ ] Icon created (128x128px)
- [ ] Banner created (1280x640px)
- [ ] Screenshots captured
- [ ] Demo video recorded (optional)
- [ ] Categories selected
- [ ] Keywords finalized
- [ ] License confirmed

---

## Notes for Reviewers

1. **Security**: All code is MIT-licensed and open source
2. **Privacy**: No data leaves the user's machine; all state is stored locally
3. **Dependencies**: Minimal (Python 3.8+, Git optional)
4. **Idempotent**: Safe to run multiple times; won't corrupt existing state
5. **User control**: AI never closes projects without user confirmation
