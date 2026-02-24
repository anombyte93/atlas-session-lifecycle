"""Test the test-spec-gen skill."""

import pytest
from pathlib import Path


def test_skill_directory_exists():
    """Skill directory should exist."""
    skill_path = Path(".claude/skills/test-spec-gen")
    assert skill_path.exists()
    assert (skill_path / "SKILL.md").exists()


def test_templates_exist():
    """Templates should exist."""
    template_path = Path(".claude/skills/test-spec-gen/templates")
    assert (template_path / "test-spec.md").exists()
    assert (template_path / "traceability.md").exists()


def test_skill_yaml_frontmatter():
    """SKILL.md should have valid YAML frontmatter."""
    skill_md = Path(".claude/skills/test-spec-gen/SKILL.md").read_text()
    assert skill_md.startswith("---")
    assert "name: test-spec-gen" in skill_md
    assert "user-invocable: true" in skill_md


def test_plan_mode_mentioned():
    """SKILL.md should mention plan mode."""
    skill_md = Path(".claude/skills/test-spec-gen/SKILL.md").read_text()
    assert "EnterPlanMode" in skill_md or "plan mode" in skill_md.lower()


def test_five_explore_agents_documented():
    """5 explore agents should be documented."""
    skill_md = Path(".claude/skills/test-spec-gen/SKILL.md").read_text()
    assert "Agent 1:" in skill_md
    assert "Agent 2:" in skill_md
    assert "Agent 3:" in skill_md
    assert "Agent 4:" in skill_md
    assert "Agent 5:" in skill_md


def test_verification_phase_documented():
    """Doubt and finality agents should be documented."""
    skill_md = Path(".claude/skills/test-spec-gen/SKILL.md").read_text()
    assert "doubt" in skill_md.lower() or "verification" in skill_md.lower()


def test_error_handling_documented():
    """Error handling should be documented."""
    skill_md = Path(".claude/skills/test-spec-gen/SKILL.md").read_text()
    assert "Error Handling" in skill_md or "error" in skill_md.lower()


def test_trello_conversion_documented():
    """Trello conversion should be documented."""
    skill_md = Path(".claude/skills/test-spec-gen/SKILL.md").read_text()
    assert "Trello" in skill_md or "trello" in skill_md.lower()


def test_quick_clarify_mentioned():
    """Quick-clarify iteration should be documented."""
    skill_md = Path(".claude/skills/test-spec-gen/SKILL.md").read_text()
    assert "quick-clarify" in skill_md.lower() or "Quick-Clarify" in skill_md


def test_test_domains_documented():
    """Test domains should be documented."""
    skill_md = Path(".claude/skills/test-spec-gen/SKILL.md").read_text()
    assert "UI Component Testing" in skill_md or "domain" in skill_md.lower()


def test_traceability_matrix_documented():
    """Traceability matrix should be documented."""
    skill_md = Path(".claude/skills/test-spec-gen/SKILL.md").read_text()
    assert "traceability" in skill_md.lower() or "Traceability" in skill_md


def test_research_phase_documented():
    """Research phase should be documented."""
    skill_md = Path(".claude/skills/test-spec-gen/SKILL.md").read_text()
    assert "Phase 2" in skill_md or "Research" in skill_md


def test_progress_reporting_documented():
    """Progress reporting should be documented."""
    skill_md = Path(".claude/skills/test-spec-gen/SKILL.md").read_text()
    assert "progress" in skill_md.lower() or "Progress" in skill_md


def test_tc_xxx_format_mentioned():
    """TC-XXX format should be mentioned."""
    skill_md = Path(".claude/skills/test-spec-gen/SKILL.md").read_text()
    assert "TC-XXX" in skill_md or "TC-" in skill_md


def test_specialist_agents_documented():
    """Specialist agents should be documented."""
    skill_md = Path(".claude/skills/test-spec-gen/SKILL.md").read_text()
    assert "specialist" in skill_md.lower() or "Specialist" in skill_md
