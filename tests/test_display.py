"""Tests for display functionality."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from rich.console import Console
from src.interface.display import (
    get_system_info,
    display_welcome,
    display_help,
    display_models,
    display_plan_tree,
    display_from_top,
)


def test_get_system_info_returns_dict():
    """Test get_system_info returns a dictionary with expected keys."""
    info = get_system_info()
    assert isinstance(info, dict)
    assert "platform" in info
    assert "python" in info
    assert "shell" in info


def test_display_welcome_prints(capsys):
    """Test display_welcome prints output."""
    console = Console()
    display_welcome(console)
    captured = capsys.readouterr()
    assert "Welcome" in captured.out
    assert "Agent Interface" in captured.out


def test_display_help_prints_commands(capsys):
    """Test display_help prints available commands."""
    console = Console()
    display_help(console)
    captured = capsys.readouterr()
    assert "/help" in captured.out
    assert "/exit" in captured.out


def test_display_models_shows_current_model(capsys):
    """Test display_models shows current model."""
    console = Console()
    display_models(None, console)  # Pass None as agent since we just test output
    captured = capsys.readouterr()
    assert "Current model" in captured.out


def test_display_plan_tree_handles_empty_xml(capsys):
    """Test display_plan_tree handles empty XML gracefully."""
    console = Console()
    display_plan_tree(console, "")
    captured = capsys.readouterr()
    assert "No plan" in captured.out or "Error" in captured.out


def test_display_from_top_prints_content(capsys):
    """Test display_from_top prints content without clearing."""
    console = Console()
    test_content = "Test output"
    display_from_top(console, test_content)
    captured = capsys.readouterr()
    assert test_content in captured.out


def test_display_plan_tree_shows_xml_content(capsys):
    """Test display_plan_tree shows XML content."""
    console = Console()
    test_xml = "<plan><task>Test</task></plan>"
    display_plan_tree(console, test_xml)
    captured = capsys.readouterr()
    assert "Test" in captured.out


def test_display_welcome_includes_system_info(capsys):
    """Test display_welcome includes system information."""
    console = Console()
    display_welcome(console)
    captured = capsys.readouterr()
    info = get_system_info()
    assert info["platform"] in captured.out
    assert info["python"] in captured.out


def test_display_help_includes_all_commands(capsys):
    """Test display_help includes all expected commands."""
    console = Console()
    display_help(console)
    captured = capsys.readouterr()
    expected_commands = ["/help", "/exit", "/models", "/plan", "/execute"]
    for cmd in expected_commands:
        assert cmd in captured.out


def test_display_models_handles_missing_agent(capsys):
    """Test display_models handles missing agent gracefully."""
    console = Console()
    display_models(None, console)
    captured = capsys.readouterr()
    assert "Current model" in captured.out
