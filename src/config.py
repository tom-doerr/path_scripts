"""
Configuration management for the agent.
"""

import os
import json
from typing import Dict, Any, Optional

DEFAULT_CONFIG = {
    "vim_mode": True,
    "stream_reasoning": True,
    "verbose": True,
    "default_model": "openrouter/deepseek/deepseek-r1",
    "history_size": 100,
    "model_aliases": {
        "flash": "openrouter/google/gemini-2.0-flash-001",
        "r1": "deepseek/deepseek-reasoner",
        "claude": "openrouter/anthropic/claude-3.7-sonnet",
    },
}

CONFIG_PATH = os.path.expanduser("~/.config/agent/config.json")


def load_config() -> Dict[str, Any]:
    """
    Load configuration from file or return default.

    Returns:
        Configuration dictionary
    """
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
                # Merge with defaults for any missing keys
                return {**DEFAULT_CONFIG, **config}
        except Exception:
            return DEFAULT_CONFIG
    else:
        return DEFAULT_CONFIG


def save_config(config: Dict[str, Any]) -> bool:
    """
    Save configuration to file.

    Args:
        config: Configuration dictionary

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False


def update_config(key: str, value: Any) -> bool:
    """
    Update a specific configuration value.

    Args:
        key: Configuration key
        value: New value

    Returns:
        True if successful, False otherwise
    """
    config = load_config()
    config[key] = value
    return save_config(config)


def get_config_value(key: str, default: Optional[Any] = None) -> Any:
    """
    Get a specific configuration value.

    Args:
        key: Configuration key
        default: Default value if key not found

    Returns:
        Configuration value or default
    """
    config = load_config()
    return config.get(key, default)
