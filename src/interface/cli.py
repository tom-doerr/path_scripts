#!/usr/bin/env python3

import sys

def main():
    """Entry point for the CLI interface"""
    from src.interface.interface import main as interface_main
    interface_main()

if __name__ == "__main__":
    main()
"""
Command-line interface for the agent.
"""
import os
import sys
import datetime
from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from src.agent.core import Agent
from src.interface.display import display_welcome, get_system_info
from src.interface.commands import process_command
from src.interface.input import process_user_input, save_chat_history
from src.interface.input_handler import get_user_input
from src.config import load_config

def main():
    """Main entry point for the agent CLI."""
    # Initialize console
    console = Console()
    
    # Display welcome message
    system_info = get_system_info()
    display_welcome(console, system_info)
    
    # Initialize agent
    agent = Agent()
    
    # Load configuration
    config = load_config()
    
    # Set up history
    history_dir = os.path.expanduser("~/.config/agent/history")
    os.makedirs(history_dir, exist_ok=True)
    history_file = os.path.join(history_dir, "chat_history.json")
    
    # Initialize chat history
    chat_history = []
    try:
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                import json
                chat_history = json.load(f)
    except Exception as e:
        console.print(f"[yellow]Could not load chat history: {e}[/yellow]")
    
    # Command history for up/down navigation
    command_history = []
    
    # Multiline input mode flag and buffer
    multiline_input_mode = False
    multiline_input_buffer = []
    
    # Main input loop
    while True:
        try:
            # Handle multiline input mode
            if multiline_input_mode:
                line = get_user_input(console, "... ", command_history, config=config)
                if line.strip() == "/end":
                    multiline_input_mode = False
                    if multiline_input_buffer:
                        full_input = "\n".join(multiline_input_buffer)
                        console.print(f"[dim]Processing {len(multiline_input_buffer)} lines of input...[/dim]")
                        process_user_input(agent, full_input, chat_history, history_file, console)
                        multiline_input_buffer.clear()
                    else:
                        console.print("[yellow]No input to process[/yellow]")
                else:
                    multiline_input_buffer.append(line)
                continue
            
            # Get user input
            user_input = get_user_input(console, "> ", command_history, config=config)
            
            # Add to command history if not empty
            if user_input.strip() and (not command_history or user_input != command_history[-1]):
                command_history.append(user_input)
                # Trim history if needed
                if len(command_history) > config.get("history_size", 100):
                    command_history.pop(0)
            
            # Check for empty input
            if not user_input.strip():
                continue
            
            # Check for slash commands
            if user_input.startswith("/"):
                # Split the command and arguments
                parts = user_input[1:].split()
                process_command(
                    agent, 
                    parts, 
                    chat_history, 
                    history_file, 
                    console,
                    multiline_input_mode,
                    multiline_input_buffer
                )
            else:
                # Process as regular input to the model
                process_user_input(agent, user_input, chat_history, history_file, console)
                
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Operation cancelled by user[/bold yellow]")
            continue
        except EOFError:
            console.print("\n[bold blue]Exiting...[/bold blue]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            import traceback
            console.print(traceback.format_exc())
