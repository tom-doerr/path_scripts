"""Common helper functions reused across the codebase."""

import os
import json
from typing import List, Dict, Any

def load_persistent_memory() -> str:
    """
    Load memory from file.
    
    Returns:
        Memory content as string
    """
    memory_file = "agent_memory.xml"
    try:
        if os.path.exists(memory_file):
            with open(memory_file, "r") as f:
                return f.read()
        # Create default memory structure
        default_memory = "<memory>\n  <!-- Agent memory -->\n</memory>"
        with open(memory_file, "w") as f:
            f.write(default_memory)
        return default_memory
    except Exception as e:
        print(f"Could not load memory: {e}")
        return "<memory></memory>"

def save_chat_history(chat_history: List[Dict[str, Any]], history_file: str) -> None:
    """
    Save chat history to file.
    
    Args:
        chat_history: List of chat history entries
        history_file: Path to the history file
    """
    try:
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        with open(history_file, "w") as f:
            json.dump(chat_history, f, indent=2)
    except Exception as e:
        print(f"Could not save chat history: {e}")

def get_terminal_height() -> int:
    """
    Get terminal height in lines.
    
    Returns:
        Terminal height or 40 as default
    """
    try:
        import shutil
        return shutil.get_terminal_size().lines
    except Exception:
        return 40
