"""Unit tests for atlas_session.common.state — file-based state helpers.

Covers:
  TestSessionDir: session_dir() returns correct path
  TestClaudeMd: claude_md() returns correct path
  TestParseMdSections: parse_md_sections() markdown parsing
  TestFindSection: find_section() partial case-insensitive lookup
  TestReadWriteJson: read_json() / write_json() round-trip and edge cases
"""

import json
from pathlib import Path

import pytest

from atlas_session.common.state import (
    claude_md,
    find_section,
    parse_md_sections,
    read_json,
    session_dir,
    write_json,
)


class TestSessionDir:
    """Tests for the session_dir() function."""

    def test_returns_path_ending_in_session_context(self, tmp_path):
        """Returns a Path whose final component is 'session-context'."""
        result = session_dir(str(tmp_path))
        assert isinstance(result, Path)
        assert result.name == "session-context"

    def test_parent_is_project_dir(self, tmp_path):
        """Parent of the returned path is the project directory."""
        result = session_dir(str(tmp_path))
        assert result.parent == tmp_path


class TestClaudeMd:
    """Tests for the claude_md() function."""

    def test_returns_path_ending_in_claude_md(self, tmp_path):
        """Returns a Path whose final component is 'CLAUDE.md'."""
        result = claude_md(str(tmp_path))
        assert isinstance(result, Path)
        assert result.name == "CLAUDE.md"

    def test_parent_is_project_dir(self, tmp_path):
        """Parent of the returned path is the project directory."""
        result = claude_md(str(tmp_path))
        assert result.parent == tmp_path


class TestParseMdSections:
    """Tests for the parse_md_sections() function."""

    def test_parses_basic_sections(self):
        """Parses ## headings into a dict keyed by heading text."""
        content = (
            "# Title\n"
            "\n"
            "Preamble text.\n"
            "\n"
            "## Section One\n"
            "\n"
            "Content of section one.\n"
            "\n"
            "## Section Two\n"
            "\n"
            "Content of section two.\n"
        )
        sections = parse_md_sections(content)
        assert "## Section One" in sections
        assert "## Section Two" in sections
        assert "Content of section one." in sections["## Section One"]
        assert "Content of section two." in sections["## Section Two"]

    def test_code_blocks_not_treated_as_headings(self):
        """## inside code fences is not treated as a heading."""
        content = (
            "## Real Section\n"
            "\n"
            "Some text.\n"
            "\n"
            "```markdown\n"
            "## This Is Inside Code\n"
            "Not a real heading.\n"
            "```\n"
            "\n"
            "Still in Real Section.\n"
        )
        sections = parse_md_sections(content)
        assert len(sections) == 1
        assert "## Real Section" in sections
        assert "## This Is Inside Code" not in sections
        # The fenced content should be part of the real section body
        assert "Not a real heading." in sections["## Real Section"]

    def test_empty_input_returns_empty_dict(self):
        """Empty string returns an empty dict."""
        assert parse_md_sections("") == {}

    def test_no_sections_returns_empty_dict(self):
        """Content with no ## headings returns an empty dict."""
        content = "# Title\n\nJust a paragraph.\n"
        assert parse_md_sections(content) == {}

    def test_h3_headings_not_split(self):
        """### headings do not create new sections."""
        content = (
            "## Parent\n"
            "\n"
            "### Child\n"
            "\n"
            "Child content.\n"
        )
        sections = parse_md_sections(content)
        assert len(sections) == 1
        assert "### Child" not in sections
        assert "Child content." in sections["## Parent"]


class TestFindSection:
    """Tests for the find_section() function."""

    def test_finds_exact_match(self):
        """Exact heading text finds the section."""
        sections = {
            "## Structure Maintenance Rules": "content A",
            "## Ralph Loop": "content B",
        }
        heading, body = find_section(sections, "## Ralph Loop")
        assert heading == "## Ralph Loop"
        assert body == "content B"

    def test_finds_partial_case_insensitive_match(self):
        """Partial, case-insensitive key finds the section."""
        sections = {
            "## Structure Maintenance Rules": "content A",
            "## Ralph Loop": "content B",
        }
        heading, body = find_section(sections, "ralph loop")
        assert heading == "## Ralph Loop"
        assert body == "content B"

    def test_returns_none_when_not_found(self):
        """Returns (None, None) when no heading matches."""
        sections = {
            "## Structure Maintenance Rules": "content A",
        }
        heading, body = find_section(sections, "nonexistent")
        assert heading is None
        assert body is None

    def test_returns_none_on_empty_sections(self):
        """Returns (None, None) when sections dict is empty."""
        heading, body = find_section({}, "anything")
        assert heading is None
        assert body is None

    def test_first_match_wins(self):
        """Returns the first matching section when multiple match."""
        sections = {
            "## Ralph Loop Config": "first",
            "## Ralph Loop Variables": "second",
        }
        heading, body = find_section(sections, "ralph loop")
        assert heading == "## Ralph Loop Config"
        assert body == "first"


class TestReadWriteJson:
    """Tests for read_json() and write_json() round-trip."""

    def test_round_trip(self, tmp_path):
        """write_json then read_json returns the same data."""
        path = tmp_path / "data.json"
        data = {"key": "value", "nested": {"a": 1, "b": [2, 3]}}
        write_json(path, data)
        result = read_json(path)
        assert result == data

    def test_missing_file_returns_empty_dict(self, tmp_path):
        """read_json on a non-existent path returns {}."""
        path = tmp_path / "does_not_exist.json"
        assert read_json(path) == {}

    def test_invalid_json_returns_empty_dict(self, tmp_path):
        """read_json on a file with invalid JSON returns {}."""
        path = tmp_path / "bad.json"
        path.write_text("not valid json {{{")
        assert read_json(path) == {}

    def test_write_creates_pretty_json(self, tmp_path):
        """write_json produces indented JSON output."""
        path = tmp_path / "pretty.json"
        write_json(path, {"a": 1})
        raw = path.read_text()
        # Pretty JSON has newlines and indentation
        assert "\n" in raw
        assert "  " in raw

    def test_empty_dict_round_trip(self, tmp_path):
        """Empty dict round-trips correctly."""
        path = tmp_path / "empty.json"
        write_json(path, {})
        assert read_json(path) == {}
