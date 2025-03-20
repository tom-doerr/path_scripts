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

from ..agent import Agent
from ..utils.xml_tools import extract_xml_from_response

def get_system_info() -> Dict[str, str]:
    """
    Get system information.
    
    Returns:
        Dictionary of system information
    """
    info = {}
    try:
        info["platform"] = platform.platform()
    except Exception:
        info["极platform"] = "unknown"
        
    try:
        info["python"] = platform.python_version()
    except Exception:
        info["python"] = "unknown"
        
    try:
        info["processor"] = platform.processor()
    except Exception:
        info["processor"] = "unknown"
        
    try:
        info["hostname"] = platform.node()
    except Exception:
        info["hostname"] = "unknown"
        
    try:
        info["shell"] = os.environ.get("SHELL", "unknown")
    except Exception:
        info["shell"] = "unknown"
        
    return info

def display_welcome(console: Console):
    """
    Display welcome message and instructions.
    
    Args:
        console: Rich console instance
    """
    system_info = get_system_info()
    system_info_text = f"Running on: {system_info['platform']} | Python {system_info['python']} | {system_info['shell']}"
    
    console.print(Panel.fit(
        "[bold blue]Agent Interface[/bold blue]\n"
        "A simple interface for the agent planning system\n"
        "Type [bold]/help[/bold] for available commands\n"
        "Any text not starting with / will be sent directly to the model\n\n"
        f"[dim]{system_info_text}[/dim]",
        title="Welcome",
        border_style="blue"
    ))

def display_help(console: Console):
    """
    Display available commands.
    
    Args:
        console: Rich console instance
    """
    console.print("[bold]Available Commands:[/bold]")
    console.print("")
    console.print("[bold green]/init[/bold green]", "- Initialize the agent")
    console.print("[bold green]/plan [spec_file][/bold green]", "- Generate a plan from specification (default: spec.md)")
    console.print("[bold green]/display[/bold green]", "- Display the current plan")
    console.print("[bold green]/update <task_id> <status> [--notes=text] [--progress=0-100][/bold green]", "- Update task status")
    console.print("[bold green]/execute <task_id>[/bold green]", "- Execute a specific task (with confirmation)")
    console.print("[bold green]/execute-ready[/bound green]", "- Execute all ready tasks in dependency order")
    console.print("[bold green]/modify-plan[/bold green]", "- Let the agent suggest modifications to the plan")
    console.print("[bold green]/model [model_name][/bold green]", "- Change the model (aliases: flash, r1, claude)")
    console.print("[bold green]/models[/bold green]", "- List available models and aliases")
    console.print("[bold green]/history [count][/bold green]", "- Display chat history (default: last 10 messages)")
    console.print("[bold green]/clear-history[/bold green]", "- Clear the chat history")
    console.print("[bold green]/memory[/bold green]", "- Display the agent's memory")
    console.print("[bold green]/clear-memory[/bold green]", "- Clear the agent's memory")
    console.print("[bold green]/paste[/bold green]", "- Enter multiline paste mode (end with /end)")
    console.print("[bold green]/end[/bold green]", "- End multiline paste mode")
    console.print("[bold green]/help[/bold green]", "- Show this help")
    console.print("[bold green]/exit[/bold green]", "- Exit the interface")
    console.print("")
    console.print("[italic]Any text not starting with / will be sent directly to the model as a chat message[/italic]")
    console.print("[italic]For multiline input, use /paste to start and /end to finish[/italic]")
    console.print("")
    console.print("[bold]XML Input Format:[/bold]")
    console.print("You can also send messages in XML format for more structured input:")
    console.print("")
    console.print("[bold cyan]<user_message>Your message here</user_message>[/bold cyan]")
    console.print("[bold cyan]<file_request path=\"path/to/file.py\">Request to see a file</file_request>[/bold cyan]")

def display_models(agent: Agent, console: Console):
    """
    Display available models and aliases.
    
    Args:
        agent: The agent instance
        console: Rich console instance
    """
    console.print("[bold blue]Current model:[/bold blue] " + agent.model_name)
    console.print("\n[bold blue]Available model aliases:[/bold blue]")
    
    # Create a table of model aliases
    model_aliases = {
        "flash": "openrouter/google/gemini-2.0-flash-001",
        "r1": "deepseek/deepseek-reasoner",
        "claude": "openrouter/anthropic/claude-3.7-sonnet",
        "gpt4": "openrouter/openai/gpt-4-turbo",
        "gpt3": "openrouter/openai/gpt-3.5-turbo",
        "mistral": "openrouter/mistralai/mistral-large",
        "llama3": "openrouter/meta-llama/llama-3-70b-instruct"
    }
    
    table = Table(show_header=True)
    table.add_column("Alias", style="green")
    table.add_column("Full Model Name", style="blue")
    
    for alias, model in model_aliases.items():
        table.add_row(alias, model)
        
    console.print(table)
    
    console.print("\n[italic]Use /model <alias> or /model <full-model-name> to change models[/italic]")

def display_plan_tree(console: Console, xml_content: str):
    """
    Display the plan as a rich tree.
    
    Args:
        console: Rich console instance
        xml_content: XML content containing the plan
    """
    try:
        # Parse the XML
        root = ET.fromstring(xml_content)
        plan_element = root.find(".//plan")
        
        if plan_element is None:
            console.print("[bold red]Error:[/bold red] No plan found in XML")
            return
        
        # Create a rich tree
        tree = Tree("[bold blue]Plan[/bold blue]")
        
        # Process tasks recursively
        def add_tasks(parent_element, parent_tree):
            for task in parent_element.findall("./task"):
                task_id = task.get("id", "unknown")
                description = task.get("description", "No description")
                status = task.get("status", "pending")
                complexity = task.get("complexity", "unknown")
                
                # Choose color based on status
                status_color = {
                    "pending": "yellow",
                    "in-progress": "blue",
                    "completed": "green",
                    "failed": "red"
                }.get(status, "white")
                
                # Get dependencies and progress
                depends_on = task.get("depends_on", "")
                progress = task.get("progress", "0")
                
                # Create task node
                task_text = f"[bold]{task_id}[/bold]: {description} "
                task_text += f"[{status_color}]({status})[/{status_color}]"
                
                # Add progress bar if available
                if progress and progress.isdigit():
                    progress_int = int(progress)
                    progress_bar = "█" * (progress_int // 10) + "░" * (10 - (progress_int // 10))
                    task_text += f" [{status_color}]{progress_bar} {progress}%[/{status_color}]"
                
                task_text += f" [dim]complexity: {complexity}[/dim]"
                
                # Add dependencies if present
                if depends_on:
                    task_text += f" [dim italic]depends on: {depends_on}[/dim italic]"
                
                task_node = parent_tree.add(task_text)
                
                # Add notes if present
                notes = task.get("notes")
                if notes:
                    task_node.add(f"[italic dim]Notes: {notes}[/italic dim]")
                
                # Process subtasks
                add_tasks(task, task_node)
        
        # Start with the root task
        root_task = plan_element.find("./task")
        if root_task is not None:
            add_tasks(plan_element, tree)
        
        # Display the tree
        console.print(tree)
        
    except ET.ParseError as e:
        console.print(f"[bold red]Error parsing XML:[/bound red] {e}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
import platform
import os
import xml.etree.ElementTree as ET
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax

def get_system_info() -> Dict[str, str]:
    """Get system information"""
    info = {}
    try:
        info["platform"] = platform.platform()
    except Exception:
        info["platform"] = "unknown"
        
    try:
        info["python"] = platform.python_version()
    except Exception:
        info["python"] = "unknown"
        
    try:
        info["processor"] = platform.processor()
    except Exception:
        info["processor"] = "unknown"
        
    try:
        info["hostname"] = platform.node()
    except Exception:
        info["hostname"] = "unknown"
        
    try:
        info["shell"] = os.environ.get("SHELL", "unknown")
    except Exception:
        info["shell"] = "unknown"
        
    return info

def display_welcome(console: Console, system_info: Dict[str, str] = None):
    """Display welcome message and instructions"""
    if system_info is None:
        system_info = get_system_info()
        
    system_info_text = f"Running on: {system_info['platform']} | Python {system_info['python']} | {system_info['shell']}"
    
    console.print(Panel.fit(
        "[bold blue]Agent Interface[/bold blue]\n"
        "A simple interface for the agent planning system\n"
        "Type [bold]/help[/bold] for available commands\n"
        "Any text not starting with / will be sent directly to the model\n\n"
        f"[dim]{system_info_text}[/dim]",
        title="Welcome",
        border_style="blue"
    ))

def display_help(console: Console):
    """Display available commands"""
    console.print("[bold]Available Commands:[/bold]")
    console.print("")
    console.print("[bold green]/init[/bold green]", "- Initialize the agent")
    console.print("[bold green]/plan [spec_file][/bold green]", "- Generate a plan from specification (default: spec.md)")
    console.print("[bold green]/display[/bold green]", "- Display the current plan")
    console.print("[bold green]/update <task_id> <status> [--notes=text] [--progress=0-100][/bold green]", "- Update task status")
    console.print("[bold green]/execute <task_id>[/bold green]", "- Execute a specific task (with confirmation)")
    console.print("[bold green]/execute-ready[/bold green]", "- Execute all ready tasks in dependency order")
    console.print("[bold green]/modify-plan[/bold green]", "- Let the agent suggest modifications to the plan")
    console.print("[bold green]/model [model_name][/bold green]", "- Change the model (aliases: flash, r1, claude)")
    console.print("[bold green]/models[/bold green]", "- List available models and aliases")
    console.print("[bold green]/history [count][/bold green]", "- Display chat history (default: last 10 messages)")
    console.print("[bold green]/clear-history[/bold green] or [bold green]/reset-chat[/bold green]", "- Clear the chat history")
    console.print("[bold green]/memory[/bold green]", "- Display the agent's memory")
    console.print("[bold green]/clear-memory[/bold green]", "- Clear the agent's memory")
    console.print("[bold green]/paste[/bold green]", "- Enter multiline paste mode (end with /end)")
    console.print("[bold green]/end[/bold green]", "- End multiline paste mode")
    console.print("[bold green]/help[/bold green]", "- Show this help")
    console.print("[bold green]/exit[/bold green]", "- Exit the interface")
    console.print("")
    console.print("[italic]Any text not starting with / will be sent directly to the model as a chat message[/italic]")
    console.print("[italic]For multiline input, use /paste to start and /end to finish[/italic]")
    console.print("")
    console.print("[bold]XML Input Format:[/bold]")
    console.print("You can also send messages in XML format for more structured input:")
    console.print("")
    console.print("[bold cyan]<user_message>Your message here</user_message>[/bold cyan]")
    console.print("[bold cyan]<file_request path=\"path/to/file.py\">Request to see a file</file_request>[/bold cyan]")

def display_models(agent, console: Console):
    """Display available models and current model"""
    console.print("[bold blue]Available models:[/bold blue]")
    console.print("- [bold]flash[/bold]: openrouter/google/gemini-2.0-flash-001")
    console.print("- [bold]r1[/bold]: deepseek/deepseek-reasoner")
    console.print("- [bold]claude[/bold]: openrouter/anthropic/claude-3.7-sonnet")
    console.print("\n[bold blue]Current model:[/bold blue] " + agent.model_name)

def display_plan_tree(console: Console, xml_content: str):
    """
    Display the plan as a rich tree.
    
    Args:
        console: Rich console instance
        xml_content: XML content containing the plan
    """
    try:
        # Parse the XML
        root = ET.fromstring(xml_content)
        plan_element = root.find(".//plan")
        
        if plan_element is None:
            console.print("[bold red]Error:[/bold red] No plan found in XML")
            return
        
        # Create a rich tree
        tree = Tree("[bold blue]Plan[/bold blue]")
        
        # Process tasks recursively
        def add_tasks(parent_element, parent_tree):
            for task in parent_element.findall("./task"):
                task_id = task.get("id", "unknown")
                description = task.get("description", "No description")
                status = task.get("status", "pending")
                complexity = task.get("complexity", "unknown")
                
                # Choose color based on status
                status_color = {
                    "pending": "yellow",
                    "in-progress": "blue",
                    "completed": "green",
                    "failed": "red"
                }.get(status, "white")
                
                # Get dependencies and progress
                depends_on = task.get("depends_on", "")
                progress = task.get("progress", "0")
                
                # Create task node
                task_text = f"[bold]{task_id}[/bold]: {description} "
                task_text += f"[{status_color}]({status})[/{status_color}]"
                
                # Add progress bar if available
                if progress and progress.isdigit():
                    progress_int = int(progress)
                    progress_bar = "█" * (progress_int // 10) + "░" * (10 - (progress_int // 10))
                    task_text += f" [{status_color}]{progress_bar} {progress}%[/{status_color}]"
                
                task_text += f" [dim]complexity: {complexity}[/dim]"
                
                # Add dependencies if present
                if depends_on:
                    task_text += f" [dim italic]depends on: {depends_on}[/dim italic]"
                
                task_node = parent_tree.add(task_text)
                
                # Add notes if present
                notes = task.get("notes")
                if notes:
                    task_node.add(f"[italic dim]Notes: {notes}[/italic dim]")
                
                # Process subtasks
                add_tasks(task, task_node)
        
        # Start with the root task
        root_task = plan_element.find("./task")
        if root_task is not None:
            add_tasks(plan_element, tree)
        
        # Display the tree
        console.print(tree)
        
    except ET.ParseError as e:
        console.print(f"[bold red]Error parsing XML:[/bold red] {e}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
