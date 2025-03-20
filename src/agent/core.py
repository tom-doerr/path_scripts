"""Core agent functionality."""

import os
import sys
import json
import threading
import datetime
from typing import Dict, List, Optional, Any, Tuple, Callable
import litellm
from rich.console import Console
from src.agent.plan import (
    generate_plan,
    update_plan,
    check_dependencies,
    apply_plan_updates,
)
from src.agent.task import execute_task
from src.utils.xml_operations import format_xml_response, extract_xml_from_response


class Agent:
    """Main agent class for handling model interactions and reasoning."""

    def __init__(self, model_name: str = "openrouter/deepseek/deepseek-r1"):
        self.console = Console()
        self.model_name = model_name
        self.plan_tree = None
        self.plan_lock = threading.Lock()  # Thread safety for plan_tree access
        self.repository_info: Dict[str, Any] = {}
        self.config = {
            "stream_reasoning": True,
            "verbose": True,
            "rate_limit": 5,  # Requests per minute
        }
        self.stream_callback: Optional[Callable[[str, bool], None]] = None

    def initialize(self, repo_path: str = ".") -> None:
        """Initialize the agent with repository information"""
        from src.utils.file_ops import read_file

        self.repository_info = {"path": repo_path}
        print(f"Agent initialized for repository: {repo_path}")

    def _get_terminal_height(self) -> int:
        """Get terminal height using shutil"""
        try:
            return shutil.get_terminal_size().lines
        except Exception:
            return 40  # Fallback default

    def stream_reasoning(self, prompt: str) -> str:
        """Stream the reasoning process from the model and return the final response"""
        messages = [{"role": "user", "content": prompt}]

        # Get terminal height and add that many newlines to preserve history
        terminal_height = self._get_terminal_height()
        print("\n" * terminal_height)

        if not self.config["stream_reasoning"]:
            # Non-streaming mode
            try:
                response = litellm.completion(
                    model=self.model_name,
                    messages=messages,
                    timeout=60,  # Add timeout to prevent hanging
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
                model=self.model_name, messages=messages, stream=True, timeout=60
            )

            for chunk in response:
                # Handle regular content
                if hasattr(chunk.choices[0], "delta") and hasattr(
                    chunk.choices[0].delta, "content"
                ):
                    content = chunk.choices[0].delta.content
                    if content:
                        # We've transitioned to regular content
                        reasoning_phase = False

                        # Clean content of control characters
                        clean_content = content.replace("\r", "").replace("\b", "")

                        if self.stream_callback:
                            if callable(self.stream_callback):
                                self.stream_callback(clean_content, is_reasoning=False)
                        else:
                            # Print without any special formatting
                            print(clean_content, end="", flush=True)
                        full_response += clean_content

                # Handle reasoning content separately (for deepseek models)
                if hasattr(chunk.choices[0], "delta") and hasattr(
                    chunk.choices[0].delta, "reasoning_content"
                ):
                    reasoning = chunk.choices[0].delta.reasoning_content
                    if reasoning:
                        # Clean up control chars and handle newlines
                        clean_reasoning = reasoning.replace("\r", "").replace("\b", "")

                        # Use callback if available, otherwise use console
                        if self.stream_callback:
                            if callable(self.stream_callback):
                                self.stream_callback(clean_reasoning, is_reasoning=True)
                        else:
                            # Use yellow color for reasoning
                            self.console.print(
                                f"[yellow]{clean_reasoning}[/yellow]",
                                end="",
                                highlight=False,
                            )
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

    # Plan management methods
    def generate_plan(self, spec: str) -> str:
        """Generate a plan tree based on the specification"""
        return generate_plan(self, spec)

    def update_plan(
        self,
        task_id: str,
        new_status: str,
        notes: Optional[str] = None,
        progress: Optional[str] = None,
    ) -> str:
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
