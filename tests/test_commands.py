"""Tests for command processing."""
from unittest.mock import Mock
from src.interface.commands import process_command

def test_process_help_command():
    """Test help command displays help."""
    mock_console = Mock()
    process_command(
        agent=Mock(),
        command=["help"],
        chat_history=[],
        history_file="test.json",
        console=mock_console,
        multiline_input_mode=False,
        multiline_input_buffer=[]
    )
    mock_console.print.assert_called()  # Verify help was displayed
