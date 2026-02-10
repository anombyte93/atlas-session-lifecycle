#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="${HOME}/.claude/skills"
TEMPLATE_DIR="${HOME}/claude-session-init-templates"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing claude-session-init..."

# 1. Create directories
# Claude Code discovers skills by scanning <name>/SKILL.md directories
# The old flat file (skills/start.md) was invisible to skill discovery
mkdir -p "$SKILL_DIR/start"
mkdir -p "$TEMPLATE_DIR"

# 2. Copy skill file into the correct directory structure
# Claude Code requires: skills/<name>/SKILL.md (NOT skills/<name>.md)
cp "$SCRIPT_DIR/start.md" "$SKILL_DIR/start/SKILL.md"
echo "  Skill installed to $SKILL_DIR/start/SKILL.md"

# 3. Copy templates
cp "$SCRIPT_DIR/templates/"* "$TEMPLATE_DIR/"
echo "  Templates installed to $TEMPLATE_DIR/"

# 4. Clean up old flat file if it exists (from previous installs)
if [ -f "$SKILL_DIR/start.md" ]; then
    rm "$SKILL_DIR/start.md"
    echo "  Removed old flat file $SKILL_DIR/start.md (replaced by directory structure)"
fi

echo ""
echo "Done. Use /start in any Claude Code session to bootstrap a project."
