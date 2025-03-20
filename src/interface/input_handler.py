"""
Input handler for the agent CLI with Vim-like functionality.
"""
from typing import List, Dict, Any, Optional
from rich.console import Console

# Try to import the Vim input module, fall back to regular input if not available
try:
    from src.interface.vim_input import get_vim_input
    VIM_INPUT_AVAILABLE = True
except ImportError:
    VIM_INPUT_AVAILABLE = False

def get_user_input(
    console: Console,
    prompt: str = "> ",
    history: List[str] = None,
    vim_mode: bool = True
) -> str:
    """
    Get input from the user with optional Vim-like interface.
    
    Args:
        console: Rich console instance
        prompt: Input prompt to display
        history: Command history
        vim_mode: Whether to use Vim-like input mode
        
    Returns:
        User input string
    """
    if vim_mode and VIM_INPUT_AVAILABLE:
        console.print(prompt, end="")
        return get_vim_input(console, history)
    else:
        # Fall back to regular input
        return console.input(prompt)

def process_input_with_history(
    input_text: str,
    history: List[str],
    max_history: int = 100
) -> None:
    """
    Process input and update history.
    
    Args:
        input_text: The input text to process
        history: The history list to update
        max_history: Maximum history items to keep
    """
    if input_text and (not history or input_text != history[-1]):
        history.append(input_text)
        
        # Trim history if needed
        if len(history) > max_history:
            history.pop(0)
