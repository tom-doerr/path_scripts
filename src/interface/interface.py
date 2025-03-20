#!/usr/bin/env python3
# Make sure this file is executable with: chmod +x interface.py

import os
import sys
import json
import datetime
from typing import List, Dict, Any, Tuple, Optional
import xml.etree.ElementTree as ET
from rich.console import Console
from rich.prompt import Prompt

# Import other interface modules
from src.interface.commands import process_command
from src.interface.display import display_welcome, get_system_info
from src.interface.actions import execute_action, execute_file_edit, execute_shell_command
from src.interface.input import process_user_input, save_chat_history
from src.agent.core import Agent

class AgentInterface:
    def __init__(self):
        self.console = Console()
        self.agent = Agent()
        self.current_plan = None
        self.model_aliases = {
            "flash": "openrouter/google/gemini-2.0-flash-001",
            "r1": "deepseek/deepseek-reasoner",
            "claude": "openrouter/anthropic/claude-3.7-sonnet"
        }
        self.chat_history = []
        self.history_file = "chat_history.json"
        self.system_info = get_system_info()
        self.multiline_input_buffer = []
        self.multiline_input_mode = False
        self.load_chat_history()
    
    def load_chat_history(self):
        """Load chat history from file if it exists"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.chat_history = json.load(f)
                    self.console.print(f"[dim]Loaded {len(self.chat_history)} previous messages[/dim]")
        except Exception as e:
            self.console.print(f"[dim]Could not load chat history: {e}[/dim]")
            self.chat_history = []
    
    def save_chat_history(self):
        """Save chat history to file"""
        from src.interface.input import save_chat_history
        save_chat_history(self.chat_history, self.history_file)
    
    # These methods have been moved to the input module
    
    def _get_terminal_height(self) -> int:
        """Get the terminal height for proper screen clearing"""
        try:
            import shutil
            terminal_size = shutil.get_terminal_size()
            return terminal_size.lines
        except Exception:
            # Fallback to a reasonable default if we can't get the terminal size
            return 40
    
    def run_command(self, command: List[str], is_slash_command: bool = True):
        """Run a command and handle the result"""
        process_command(
            self.agent, 
            command, 
            self.chat_history, 
            self.history_file,
            self.console,
            self.multiline_input_mode,
            self.multiline_input_buffer
        )
    
    def chat_with_model(self, message: str):
        """Send a message directly to the model and handle the response"""
        self.console.print("\n")
        
        # Initialize agent if not already done
        if not self.agent.repository_info:
            with self.console.status("[bold blue]Initializing agent...[/bold blue]"):
                self.agent.initialize()
        
        # Use the process_user_input function from input module
        process_user_input(
            self.agent,
            message,
            self.chat_history,
            self.history_file,
            self.console
        )
    
    def run_interactive(self):
        """Run the interface in interactive mode"""
        display_welcome(self.console, self.system_info)
        
        while True:
            try:
                # Handle multiline input mode
                if self.multiline_input_mode:
                    user_input = Prompt.ask("\n[bold yellow]paste>[/bold yellow]")
                    
                    # Check for end of multiline input
                    if user_input.lower() in ["/end", "/done", "/finish"]:
                        self.multiline_input_mode = False
                        
                        # Process the collected input
                        if self.multiline_input_buffer:
                            full_input = "\n".join(self.multiline_input_buffer)
                            self.console.print(f"[dim]Processing {len(self.multiline_input_buffer)} lines of input...[/dim]")
                            self.chat_with_model(full_input)
                            self.multiline_input_buffer = []
                        else:
                            self.console.print("[yellow]No input to process[/yellow]")
                    else:
                        # Add to buffer
                        self.multiline_input_buffer.append(user_input)
                        self.console.print(f"[dim]Line {len(self.multiline_input_buffer)} added[/dim]")
                else:
                    # Normal single-line input mode
                    user_input = Prompt.ask("\n[bold blue]>[/bold blue]")
                    
                    if user_input.lower() in ["exit", "quit", "q", "/exit", "/quit", "/q"]:
                        self.console.print("[bold blue]Exiting...[/bold blue]")
                        sys.exit(0)
                    
                    # Check if this is a paste command
                    if user_input.lower() == "/paste":
                        self.multiline_input_mode = True
                        self.multiline_input_buffer = []
                        self.console.print("[bold yellow]Entering multiline paste mode. Type /end when finished.[/bold yellow]")
                        continue
                    
                    # Check if this is a slash command
                    if user_input.startswith('/'):
                        # Remove the slash and split into command parts
                        command = user_input[1:].strip().split()
                        self.run_command(command)
                    else:
                        # Check if this might be a multiline paste
                        if "\n" in user_input:
                            lines = user_input.split("\n")
                            self.console.print(f"[dim]Detected multiline paste with {len(lines)} lines[/dim]")
                            self.chat_with_model(user_input)
                        else:
                            # Treat as direct chat with the model
                            self.chat_with_model(user_input)
                    
            except KeyboardInterrupt:
                if self.multiline_input_mode:
                    self.console.print("\n[bold yellow]Cancelling multiline input[/bold yellow]")
                    self.multiline_input_mode = False
                    self.multiline_input_buffer = []
                else:
                    self.console.print("\n[bold yellow]Exiting...[/bold yellow]")
                    sys.exit(0)
            except EOFError:  # Handle Ctrl+D
                self.console.print("\n[bold yellow]Exiting...[/bold yellow]")
                sys.exit(0)
            except Exception as e:
                self.console.print(f"[bold red]Error:[/bold red] {e}")

def main():
    """Main function to run the agent interface"""
    interface = AgentInterface()
    interface.run_interactive()

if __name__ == "__main__":
    main()
