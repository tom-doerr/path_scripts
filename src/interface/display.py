#!/usr/bin/env python3
"""Display formatting for the agent interface."""

import os
import platform
import xml.etree.ElementTree as ET
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table
from rich.syntax import Syntax

from src.agent.core import Agent
from src.utils.xml_tools import extract_xml_from_response


def get_system_info() -> Dict[str, str]:
    """Get basic system information."""
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "shell": platform.system(),
    }


def display_welcome(console: Console, system_info: Dict[str, str] = None):
    """Display welcome message."""
    if system_info is None:
        system_info = get_system_info()
        
    console.print(
        Panel.fit(
            "[bold blue]Agent Interface[/bold blue]\n"
            f"Running on: {system_info['platform']} | Python {system_info['python']}",
            title="Welcome",
            border_style="blue",
        )
    )


def display_help(console: Console):
    """Display available commands."""
    console.print("[bold]Available Commands:[/bold]")
    console.print("- /help: Show this help")
    console.print("- /exit: Exit the interface")


def display_models(agent, console: Console):
    """Display available models."""
    console.print(f"[bold blue]Current model:[/bold blue] {agent.model_name}")


def display_plan_tree(console: Console, xml_content: str):
    """Display plan tree from XML."""
    if not xml_content:
        console.print("[bold red]Error: No plan content[/bold red]")
        return
    
    console.print("[bold blue]Plan Tree:[/bold blue]")
    console.print(xml_content[:100])  # Print first 100 chars for simplicity


def display_from_top(console: Console, content: str, preserve_history: bool = True):
    """
    Display content without clearing terminal history.

    Args:
        console: Rich console instance
        content: Content to display
        preserve_history: Not used, kept for backward compatibility
    """
    # Simply print the content without any clearing or cursor manipulation
    console.print(content)
