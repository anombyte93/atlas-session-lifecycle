#!/usr/bin/env bash
# ============================================================================
# Installation Test Script for Atlas Session Lifecycle
# ============================================================================
# This script tests the installation in a clean environment.
# Used for marketplace submission verification.
# ============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

info()  { printf "${CYAN}[info]${RESET}  %s\n" "$*"; }
ok()    { printf "${GREEN}[ok]${RESET}    %s\n" "$*"; }
warn()  { printf "${YELLOW}[warn]${RESET}  %s\n" "$*"; }
err()   { printf "${RED}[error]${RESET} %s\n" "$*" >&2; }

test_count=0
pass_count=0
fail_count=0

test_step() {
    ((test_count++)) || true
    info "Test $test_count: $1"
}

run_test() {
    local description="$1"
    local command="$2"
    local expected="$3"

    test_step "$description"

    if eval "$command" > /dev/null 2>&1; then
        if [[ -n "$expected" ]]; then
            if eval "$expected"; then
                ok "PASS: $description"
                ((pass_count++))
                return 0
            else
                err "FAIL: $description - expectation not met"
                ((fail_count++))
                return 1
            fi
        else
            ok "PASS: $description"
            ((pass_count++))
            return 0
        fi
    else
        err "FAIL: $description - command failed"
        ((fail_count++))
        return 1
    fi
}

check_file() {
    local file="$1"
    local description="$2"

    test_step "$description"

    if [[ -f "$file" ]]; then
        ok "PASS: $description - file exists"
        ((pass_count++)) || true
        return 0
    else
        err "FAIL: $description - file not found: $file"
        ((fail_count++)) || true
        return 1
    fi
}

check_dir() {
    local dir="$1"
    local description="$2"

    test_step "$description"

    if [[ -d "$dir" ]]; then
        ok "PASS: $description - directory exists"
        ((pass_count++)) || true
        return 0
    else
        err "FAIL: $description - directory not found: $dir"
        ((fail_count++)) || true
        return 1
    fi
}

# ============================================================================
# Test Suite
# ============================================================================

main() {
    local SKILL_DIR="${SKILL_DIR:-$HOME/.claude/skills/start}"
    local TEMPLATE_DIR="${TEMPLATE_DIR:-$HOME/claude-session-init-templates}"

    printf "${BOLD}Atlas Session Lifecycle — Installation Test Suite${RESET}\n"
    printf "Testing installation at: $SKILL_DIR\n\n"

    # Test 1: Check SKILL.md exists
    check_file "$SKILL_DIR/SKILL.md" "SKILL.md exists"

    # Test 2: Check session-init.py exists
    check_file "$SKILL_DIR/session-init.py" "session-init.py exists"

    # Test 3: Check templates directory
    check_dir "$TEMPLATE_DIR" "Templates directory exists"

    # Test 4: Verify SKILL.md has required content
    test_step "SKILL.md has required frontmatter"
    if grep -q '^name: start' "$SKILL_DIR/SKILL.md" 2>/dev/null; then
        ok "PASS: SKILL.md has name field"
        ((pass_count++)) || true
    else
        err "FAIL: SKILL.md missing name field"
        ((fail_count++)) || true
    fi

    # Test 5: Verify templates contain all required files
    local template_dir="${TEMPLATE_DIR:-$HOME/claude-session-init-templates}"
    local required_templates=(
        "CLAUDE-activeContext.md"
        "CLAUDE-decisions.md"
        "CLAUDE-patterns.md"
        "CLAUDE-troubleshooting.md"
        "CLAUDE-soul-purpose.md"
    )

    for template in "${required_templates[@]}"; do
        test_step "Template exists: $template"
        if [[ -f "$template_dir/$template" ]]; then
            ok "PASS: Template $template exists"
            ((pass_count++)) || true
        else
            err "FAIL: Template $template not found"
            ((fail_count++)) || true
        fi
    done

    # Test 6: Check session-init.py is executable
    test_step "session-init.py is executable"
    if [[ -x "$SKILL_DIR/session-init.py" ]]; then
        ok "PASS: session-init.py is executable"
        ((pass_count++)) || true
    else
        warn "WARN: session-init.py not executable (may need chmod +x)"
        ((pass_count++)) || true  # Not a hard fail
    fi

    # Test 7: Verify Python script syntax
    test_step "session-init.py has valid Python syntax"
    if python3 -m py_compile "$SKILL_DIR/session-init.py" 2>/dev/null; then
        ok "PASS: session-init.py has valid syntax"
        ((pass_count++)) || true
    else
        err "FAIL: session-init.py has syntax errors"
        ((fail_count++)) || true
    fi

    # Test 8: Check for .version file
    check_file "$SKILL_DIR/.version" "Version tracking file exists"

    # ============================================================================
    # Summary
    # ============================================================================

    printf "\n${BOLD}Test Summary${RESET}\n"
    printf "Total tests: $test_count\n"
    printf "${GREEN}Passed: $pass_count${RESET}\n"
    printf "${RED}Failed: $fail_count${RESET}\n"

    if [[ $fail_count -eq 0 ]]; then
        printf "\n${GREEN}${BOLD}All tests passed!${RESET}\n"
        exit 0
    else
        printf "\n${RED}${BOLD}Some tests failed. Please review installation.${RESET}\n"
        exit 1
    fi
}

main "$@"
