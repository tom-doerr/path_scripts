"""
Vim-like input interface for the agent CLI using Textual.
"""

from enum import Enum
from typing import List, Dict, Any, Callable, Optional

from rich.console import Console
from textual.app import App
from textual.widgets import Input
from textual.events import Key

# Import necessary modules for input processing
from src.interface.display import get_system_info


class Mode(Enum):
    NORMAL = "normal"
    INSERT = "insert"


class VimInput(App):
    """A Vim-like input widget using Textual."""

    def __init__(
        self,
        console: Console,
        history: List[str] = None,
        on_submit: Callable[[str], None] = None,
    ):
        super().__init__()
        self.console = console
        self.history = history or []
        self.history_index = len(self.history)
        self.on_submit = on_submit
        self.mode = Mode.INSERT
        self.result: Optional[str] = None

    def compose(self):
        """Create child widgets."""
        self.input = Input(placeholder="Enter command (Esc for normal mode)")
        yield self.input

    def on_mount(self):
        """Called when app is mounted."""
        self.input.focus()

    def on_key(self, event: Key):
        """Handle key events."""
        # Handle mode switching
        if event.key == "escape":
            self.mode = Mode.NORMAL
            self.input.placeholder = "[Normal Mode] j/k: history, i: insert, :/search"
            return

        if self.mode == Mode.NORMAL:
            self._handle_normal_mode(event)
        # In insert mode, let default handlers work

    def _handle_normal_mode(self, event: Key):
        """Handle keys in normal mode."""
        key = event.key

        if key == "i":
            # Switch to insert mode
            self.mode = Mode.INSERT
            self.input.placeholder = "Enter command (Esc for normal mode)"

        elif key == "a":
            # Append (move cursor to end and switch to insert)
            self.mode = Mode.INSERT
            self.input.placeholder = "Enter command (Esc for normal mode)"
            # Move cursor to end
            self.input.cursor_position = len(self.input.value)

        elif key == "0":
            # Move to beginning of line
            self.input.cursor_position = 0

        elif key == "$":
            # Move to end of line
            self.input.cursor_position = len(self.input.value)

        elif key == "j":
            # Navigate down in history
            if self.history and self.history_index < len(self.history) - 1:
                self.history_index += 1
                self.input.value = self.history[self.history_index]

        elif key == "k":
            # Navigate up in history
            if self.history and self.history_index > 0:
                self.history_index -= 1
                self.input.value = self.history[self.history_index]

        elif key == "d":
            # dd to clear line
            if getattr(self, "_last_key", None) == "d":
                self.input.value = ""
            self._last_key = "d"
            return

        elif key == "x":
            # Delete character under cursor
            if self.input.value and self.input.cursor_position < len(self.input.value):
                pos = self.input.cursor_position
                self.input.value = self.input.value[:pos] + self.input.value[pos + 1 :]

        elif key == "enter":
            # Submit in normal mode too
            self.result = self.input.value
            self.exit()

        # Store last key for combinations like dd
        self._last_key = key

    def on_input_submitted(self):
        """Handle input submission."""
        self.result = self.input.value
        self.exit()


def get_vim_input(
    console: Console, history: List[str] = None, on_submit: Callable[[str], None] = None
) -> str:
    """
    Display a Vim-like input prompt and return the entered text.

    Args:
        console: Rich console instance
        history: Command history list
        on_submit: Callback for when input is submitted

    Returns:
        The entered text
    """
    app = VimInput(console, history, on_submit)
    app.run()
    return app.result or ""
