"""Display formatting for the agent interface."""

import platform
from typing import Dict
from rich.console import Console
from rich.panel import Panel


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
    console.print("- /models: Show available models")
    console.print("- /plan: Generate or display plan")
    console.print("- /execute: Execute a task")


def display_models(agent, console: Console):
    """Display available models."""
    model_name = agent.model_name if agent else "No model selected"
    console.print(f"[bold blue]Current model:[/bold blue] {model_name}")


def display_plan_tree(console: Console, xml_content: str):
    """Display plan tree from XML."""
    if not xml_content:
        console.print("[bold red]Error: No plan content[/bold red]")
        return

    console.print("[bold blue]Plan Tree:[/bold blue]")
    console.print(xml_content)


def display_from_top(console: Console, content: str, _preserve_history: bool = True):
    """
    Display content without clearing terminal history.

    Args:
        console: Rich console instance
        content: Content to display
        preserve_history: Not used, kept for backward compatibility
    """
    console.print(content)
