"""Tests for display functionality."""

from rich.console import Console
from src.interface.display import (
    get_system_info,
    display_welcome,
    display_help,
    display_models,
    display_plan_tree,
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
