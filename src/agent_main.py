#!/usr/bin/env python3

import os
import sys
import json
from typing import Dict, List, Optional, Any, Tuple
import litellm
from rich.console import Console

# Import refactored modules
from src.agent.repository import analyze_repository
from src.agent.plan import generate_plan, update_plan, check_dependencies, apply_plan_updates
from src.agent.task import execute_task
from src.utils.xml_operations import extract_xml_from_response, format_xml_response, pretty_format_xml
from src.utils.xml_tools import extract_xml_from_response as extract_xml_alt
from src.utils.feedback import DopamineReward

class Agent:
    def __init__(self, model_name: str = "openrouter/deepseek/deepseek-r1"):
        self.console = Console()
        self.model_name = model_name
        self.plan_tree = None
        self.repository_info = {}
        self.config = {
            "stream_reasoning": True,
            "verbose": True
        }
        self.stream_callback = None
        
    def initialize(self, repo_path: str = ".") -> None:
        """Initialize the agent with repository information"""
        self.repository_info = analyze_repository(repo_path)
        print(f"Agent initialized for repository: {repo_path}")
    
    def generate_plan(self, spec: str) -> str:
        """Generate a plan tree based on the specification"""
        return generate_plan(self, spec)
    
    def extract_xml_from_response(self, response: str, tag_name: str) -> Optional[str]:
        """Extract XML content for a specific tag from the response"""
        try:
            # Look for XML content in the response
            start_tag = f"<{tag_name}"
            end_tag = f"</{tag_name}>"
            
            start_index = response.find(start_tag)
            end_index = response.find(end_tag, start_index) + len(end_tag)
            
            if start_index != -1 and end_index != -1:
                return response[start_index:end_index]
            return None
        except Exception as e:
            print(f"Error extracting XML: {e}")
            return None
    
    def stream_reasoning(self, prompt: str) -> str:
        """Stream the reasoning process from the model and return the final response"""
        messages = [{"role": "user", "content": prompt}]
        
        # Print the full message being sent to the model
        print("\n=== Message Sent to Model ===\n")
        print(f"Model: {self.model_name}")
        print(prompt)
        print("\n=== End Message ===\n")
        
        # Get terminal height and add that many newlines to preserve history
        terminal_height = self._get_terminal_height()
        print("\n" * terminal_height)
        
        if not self.config["stream_reasoning"]:
            # Non-streaming mode
            try:
                response = litellm.completion(
                    model=self.model_name,
                    messages=messages,
                    timeout=60  # Add timeout to prevent hanging
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"Error in non-streaming mode: {e}")
                return f"Error: {str(e)}"
        
        # Streaming mode
        full_response = ""
        reasoning_output = ""
        
        try:
            # Add timeout to prevent hanging
            response = litellm.completion(
                model=self.model_name,
                messages=messages,
                stream=True,
                timeout=60
            )
            
            # Track if we're in the reasoning phase
            reasoning_phase = True
            
            for chunk in response:
                # Handle regular content
                if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content
                    if content:
                        # We've transitioned to regular content
                        reasoning_phase = False
                        
                        # Clean content of control characters
                        clean_content = content.replace('\r', '').replace('\b', '')
                        
                        if self.stream_callback:
                            self.stream_callback(clean_content, is_reasoning=False)
                        else:
                            # Print without any special formatting
                            print(clean_content, end='', flush=True)
                        full_response += clean_content
                
                # Handle reasoning content separately (for deepseek models)
                if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'reasoning_content'):
                    reasoning = chunk.choices[0].delta.reasoning_content
                    if reasoning:
                        # Clean up control chars and handle newlines
                        clean_reasoning = reasoning.replace('\r', '').replace('\b', '')
                        
                        # Use callback if available, otherwise use console
                        if self.stream_callback:
                            self.stream_callback(clean_reasoning, is_reasoning=True)
                        else:
                            # Use yellow color for reasoning
                            self.console.print(f"[yellow]{clean_reasoning}[/yellow]", end='', highlight=False)
                        reasoning_output += clean_reasoning
            
            print("\n")
            
            # Save reasoning to a file for reference
            if reasoning_output:
                try:
                    with open("last_reasoning.txt", "w") as f:
                        f.write(reasoning_output)
                except Exception as e:
                    print(f"Warning: Could not save reasoning to file: {e}")
                
            return full_response
            
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user")
            return full_response
        except Exception as e:
            print(f"\nError during streaming: {e}")
            return full_response or f"Error: {str(e)}"
    
    # These methods are now imported from utils.xml_operations
                
    def _get_terminal_height(self) -> int:
        """Get the terminal height for proper screen clearing"""
        try:
            import shutil
            terminal_size = shutil.get_terminal_size()
            return terminal_size.lines
        except Exception:
            # Fallback to a reasonable default if we can't get the terminal size
            return 40
    
    def update_plan(self, task_id: str, new_status: str, notes: Optional[str] = None, progress: Optional[str] = None) -> str:
        """Update the status of a task in the plan"""
        return update_plan(self, task_id, new_status, notes, progress)
    
    def display_plan_tree(self) -> str:
        """Display the current plan tree"""
        if not self.plan_tree:
            return format_xml_response({"error": "No plan exists"})
        
        return format_xml_response({"plan": self.plan_tree})
    
    def apply_plan_updates(self, plan_update_xml: str) -> None:
        """Apply updates to the plan tree based on the plan_update XML"""
        apply_plan_updates(self, plan_update_xml)
    
    def check_dependencies(self, task_id: str) -> Tuple[bool, List[str]]:
        """Check if all dependencies for a task are completed"""
        return check_dependencies(self, task_id)
    
    def execute_task(self, task_id: str) -> str:
        """Execute a specific task from the plan"""
        return execute_task(self, task_id)

def main():
    """Main function to handle command line arguments and run the agent"""
    # Check for model argument
    model_name = "openrouter/deepseek/deepseek-r1"  # Default model
    
    # Look for --model or -m flag
    for i, arg in enumerate(sys.argv):
        if arg in ["--model", "-m"] and i + 1 < len(sys.argv):
            model_name = sys.argv[i + 1]
            # Remove these arguments
            sys.argv.pop(i)
            sys.argv.pop(i)
            break
    
    agent = Agent(model_name)
    
    if len(sys.argv) < 2:
        print("Usage: ./agent [--model MODEL_NAME] <command> [arguments]")
        print("Commands:")
        print("  init                  - Initialize the agent")
        print("  plan [spec_file]      - Generate a plan from specification (default: spec.md)")
        print("  display               - Display the current plan")
        print("  update <task_id> <status> [--notes=text] [--progress=0-100] - Update task status")
        print("  execute <task_id>     - Execute a specific task")
        print("\nOptions:")
        print("  --model, -m MODEL_NAME - Specify the model to use (default: openrouter/deepseek/deepseek-r1)")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        agent.initialize()
        print("Agent initialized successfully")
    
    elif command == "plan":
        # Use spec.md by default if no file specified
        spec_file = sys.argv[2] if len(sys.argv) > 2 else "spec.md"
        print(f"Using specification file: {spec_file}")
        try:
            with open(spec_file, 'r') as f:
                spec = f.read()
            
            print(f"Using model: {agent.model_name}")
            agent.initialize()
            
            try:
                result = agent.generate_plan(spec)
                print(result)
                
                # Save the plan to a file
                with open("agent_plan.xml", 'w') as f:
                    f.write(result)
                print("Plan saved to agent_plan.xml")
            except KeyboardInterrupt:
                print("\nOperation cancelled by user")
                sys.exit(1)
            
        except FileNotFoundError:
            print(f"Error: Specification file '{spec_file}' not found")
            sys.exit(1)
    
    elif command == "display":
        # Load the plan from file
        try:
            with open("agent_plan.xml", 'r') as f:
                xml_content = f.read()
                agent.plan_tree = agent.extract_xml_from_response(xml_content, "plan")
            
            result = agent.display_plan_tree()
            print(result)
            
        except FileNotFoundError:
            print("Error: No plan file found. Generate a plan first.")
            sys.exit(1)
    
    elif command == "update":
        if len(sys.argv) < 4:
            print("Error: Missing task_id or status")
            sys.exit(1)
        
        task_id = sys.argv[2]
        status = sys.argv[3]
        
        # Check for progress and notes flags
        progress = None
        notes = None
        
        for i, arg in enumerate(sys.argv[4:], 4):
            if arg.startswith("--progress="):
                progress = arg.split("=")[1]
            elif arg.startswith("--notes="):
                notes = arg.split("=")[1]
            elif i == 4 and not arg.startswith("--"):
                # For backward compatibility, treat the fourth argument as notes
                notes = arg
        
        # Load the plan from file
        try:
            with open("agent_plan.xml", 'r') as f:
                xml_content = f.read()
                agent.plan_tree = agent.extract_xml_from_response(xml_content, "plan")
            
            result = agent.update_plan(task_id, status, notes, progress)
            print(result)
            
            # Save the updated plan
            with open("agent_plan.xml", 'w') as f:
                f.write(result)
            
        except FileNotFoundError:
            print("Error: No plan file found. Generate a plan first.")
            sys.exit(1)
    
    elif command == "execute":
        if len(sys.argv) < 3:
            print("Error: Missing task_id")
            sys.exit(1)
        
        task_id = sys.argv[2]
        
        # Load the plan from file
        try:
            with open("agent_plan.xml", 'r') as f:
                xml_content = f.read()
                agent.plan_tree = agent.extract_xml_from_response(xml_content, "plan")
            
            try:
                result = agent.execute_task(task_id)
                print(result)
                
                # Save the actions to a file
                with open(f"agent_actions_{task_id}.xml", 'w') as f:
                    f.write(result)
                print(f"Actions saved to agent_actions_{task_id}.xml")
                
                # Save the updated plan
                with open("agent_plan.xml", 'w') as f:
                    f.write(agent.format_xml_response({"plan": agent.plan_tree}))
            except KeyboardInterrupt:
                print("\nOperation cancelled by user")
                sys.exit(1)
            
        except FileNotFoundError:
            print("Error: No plan file found. Generate a plan first.")
            sys.exit(1)
    
    elif command == "interactive":
        print(f"Starting interactive mode with model: {agent.model_name}")
        agent.initialize()
        
        while True:
            try:
                user_input = input("\n> ")
                if user_input.lower() in ["exit", "quit", "q"]:
                    break
                
                # Simple command processing
                if user_input.startswith("/"):
                    parts = user_input[1:].split()
                    cmd = parts[0] if parts else ""
                    
                    if cmd == "plan" and len(parts) > 1:
                        spec_file = parts[1]
                        try:
                            with open(spec_file, 'r') as f:
                                spec = f.read()
                            result = agent.generate_plan(spec)
                            print(result)
                        except FileNotFoundError:
                            print(f"Error: File '{spec_file}' not found")
                    
                    elif cmd == "display":
                        result = agent.display_plan_tree()
                        print(result)
                    
                    elif cmd == "execute" and len(parts) > 1:
                        task_id = parts[1]
                        result = agent.execute_task(task_id)
                        print(result)
                    
                    elif cmd == "help":
                        print("Available commands:")
                        print("  /plan <spec_file> - Generate a plan from specification")
                        print("  /display - Display the current plan")
                        print("  /execute <task_id> - Execute a specific task")
                        print("  /help - Show this help")
                        print("  exit, quit, q - Exit interactive mode")
                    
                    else:
                        print("Unknown command. Type /help for available commands.")
                
                # Treat as a prompt to the model
                else:
                    response = agent.stream_reasoning(user_input)
                    # No need to print response as it's already streamed
            
            except KeyboardInterrupt:
                print("\nUse 'exit' or 'q' to quit")
            except Exception as e:
                print(f"Error: {e}")
    
    else:
        print(f"Error: Unknown command '{command}'")
        sys.exit(1)

if __name__ == "__main__":
    main()
