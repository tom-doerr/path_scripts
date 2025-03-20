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
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.chat_history, f, indent=2)
        except Exception as e:
            self.console.print(f"[dim]Could not save chat history: {e}[/dim]")
    
    def _format_history_for_prompt(self):
        """Format chat history for inclusion in the prompt"""
        # Limit history to last 10 messages to avoid context overflow
        recent_history = self.chat_history[-10:] if len(self.chat_history) > 10 else self.chat_history
        
        formatted_history = []
        for msg in recent_history[:-1]:  # Exclude the current message which is added separately
            role = msg["role"]
            content = msg["content"]
            timestamp = msg.get("timestamp", "")
            
            # Format as XML
            entry = f"<entry role=\"{role}\" timestamp=\"{timestamp}\">"
            
            # For assistant messages, try to extract just the message part to keep history cleaner
            if role == "assistant":
                message_xml = self.agent.extract_xml_from_response(content, "message")
                if message_xml:
                    try:
                        root = ET.fromstring(message_xml)
                        message_text = root.text if root.text else ""
                        entry += f"<content>{message_text}</content>"
                    except ET.ParseError:
                        entry += f"<content>{content}</content>"
                else:
                    entry += f"<content>{content}</content>"
            else:
                entry += f"<content>{content}</content>"
                
            entry += "</entry>"
            formatted_history.append(entry)
        
        return "\n".join(formatted_history)
    
    def _load_persistent_memory(self):
        """Load memory from file"""
        memory_file = "agent_memory.xml"
        try:
            if os.path.exists(memory_file):
                with open(memory_file, 'r') as f:
                    return f.read()
            else:
                # Create default memory structure - simple and flexible
                default_memory = "<memory>\n  <!-- Agent can structure this as needed -->\n</memory>"
                with open(memory_file, 'w') as f:
                    f.write(default_memory)
                return default_memory
        except Exception as e:
            self.console.print(f"[dim]Could not load memory: {e}[/dim]")
            return "<memory></memory>"
    
    def _update_persistent_memory(self, memory_updates_xml):
        """Update memory based on model's instructions"""
        if not memory_updates_xml:
            return
            
        try:
            memory_file = "agent_memory.xml"
            current_memory = self._load_persistent_memory()
            
            # Parse the updates
            updates_root = ET.fromstring(memory_updates_xml)
            
            # Parse current memory
            try:
                memory_root = ET.fromstring(current_memory)
            except ET.ParseError:
                # If parsing fails, create a new memory structure
                memory_root = ET.Element("memory")
            
            # Process edits - simple search/replace approach
            for edit in updates_root.findall("./edit"):
                search_elem = edit.find("search")
                replace_elem = edit.find("replace")
                
                if search_elem is not None and replace_elem is not None:
                    search_text = search_elem.text if search_elem.text else ""
                    replace_text = replace_elem.text if replace_elem.text else ""
                    
                    # Convert memory to string for search/replace
                    memory_str = ET.tostring(memory_root, encoding='unicode')
                    
                    if search_text in memory_str:
                        # Replace the text
                        memory_str = memory_str.replace(search_text, replace_text)
                        
                        # Parse the updated memory
                        memory_root = ET.fromstring(memory_str)
            
            # Process additions - just add text directly to memory
            for append in updates_root.findall("./append"):
                append_text = append.text if append.text else ""
                if append_text:
                    # Append to existing memory text
                    if memory_root.text is None:
                        memory_root.text = append_text
                    else:
                        memory_root.text += "\n" + append_text
            
            # Save the updated memory
            updated_memory = self.agent.pretty_format_xml(ET.tostring(memory_root, encoding='unicode'))
            with open(memory_file, 'w') as f:
                f.write(updated_memory)
                
            self.console.print("[dim]Memory updated[/dim]")
            
        except Exception as e:
            self.console.print(f"[bold red]Error updating memory: {e}[/bold red]")
    
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
        from src.interface.chat import process_chat_message, process_chat_response
        
        # Move existing text up and clear remaining space
        terminal_height = self._get_terminal_height()
        # Move cursor up by terminal height and clear from cursor down
        print(f"\x1b[{terminal_height}F\x1b[J", end="")
        
        # Initialize agent if not already done
        if not self.agent.repository_info:
            with self.console.status("[bold blue]Initializing agent...[/bold blue]"):
                self.agent.initialize()
        
        # Format user message as XML if it's not already
        if not message.strip().startswith("<"):
            formatted_message = f"<user_message>{message}</user_message>"
        else:
            formatted_message = message
        
        # Add user message to history
        timestamp = datetime.datetime.now().isoformat()
        self.chat_history.append({
            "role": "user",
            "content": formatted_message,
            "timestamp": timestamp
        })
        self.save_chat_history()
        
        # Get the full prompt
        prompt = process_chat_message(
            formatted_message, 
            self._format_history_for_prompt(), 
            self._load_persistent_memory(),
            self.system_info
        )
        
        try:
            # Set a callback to handle streaming in the interface
            def stream_callback(content, is_reasoning=False):
                if is_reasoning:
                    # Use yellow color for reasoning tokens
                    self.console.print(f"[yellow]{content}[/yellow]", end="")
                else:
                    # Use rich for normal content
                    self.console.print(content, end="", highlight=False)
                    
            # Pass the callback to the agent
            self.agent.stream_callback = stream_callback
            response = self.agent.stream_reasoning(prompt)
            
            # Process the response
            process_chat_response(
                self.agent,
                self.console,
                response, 
                self.chat_history,
                self._update_persistent_memory,
                self._get_terminal_height,
                self._load_persistent_memory,
                self._format_history_for_prompt,
                self.save_chat_history
            )
                
        except KeyboardInterrupt:
            self.console.print("\n[bold yellow]Operation cancelled by user[/bold yellow]")
    
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
