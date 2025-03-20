"""Tests for interface components."""
from rich.console import Console
from src.interface.display import get_system_info, display_welcome

def test_get_system_info():
    """Test system info returns expected fields."""
    info = get_system_info()
    assert isinstance(info, dict)
    for key in ["platform", "python", "shell"]:
        assert key in info
        assert isinstance(info[key], str)

def test_display_welcome():
    """Test welcome message displays without errors."""
    console = Console()
    display_welcome(console)
    # Basic smoke test - just verify function runs without exceptions
