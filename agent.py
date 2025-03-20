#!/usr/bin/env python3
"""Core Agent functionality for model interaction and reasoning."""

import os
import sys
import json
from typing import Dict, List, Optional, Any, Tuple, Callable
import xml.etree.ElementTree as ET
import litellm
from rich.console import Console

class Agent:
    """Main agent class for handling model interactions and reasoning."""
    
    def __init__(self, model_name: str = "openrouter/deepseek/deepseek-r1"):
        """
        Initialize the agent with a specific model.
        
        Args:
            model_name: The name of the LLM to use
        """
        self.console = Console()
        self.model_name = model_name
        self.plan_tree = None
        self.repository_info: Dict[str, Any] = {}
        self.config = {
            "stream_reasoning": True,
            "verbose": True
        }
        self.stream_callback: Optional[Callable[[str, bool], None]] = None
    
    def initialize(self, repo_path: str = ".") -> None:
        """
        Initialize the agent with repository information.
        
        Args:
            repo_path: Path to the repository to analyze
        """
        self.repository_info = analyze_repository(repo_path)
        print(f"Agent initialized for repository: {repo_path}")
    
    def stream_reasoning(self, prompt: str) -> str:
        """
        Stream the reasoning process from the model and return the final response.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            The model's response as a string
        """
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
                    timeout=120  # Increase timeout to prevent hanging
                )
                return response.choices[0].message.content
            except Exception as e:
                error_msg = str(e)
                print(f"Error in non-streaming mode: {error_msg}")
                
                # Provide more specific error messages
                if "rate limit" in error_msg.lower():
                    return "Error: Rate limit exceeded. Please try again later."
                elif "timeout" in error_msg.lower():
                    return "Error: Request timed out. The model may be overloaded."
                elif "connection" in error_msg.lower():
                    return "Error: Connection failed. Please check your internet connection."
                else:
                    return f"Error: {error_msg}"
        
        # Streaming mode
        full_response = ""
        reasoning_output = ""
        
        try:
            # Add timeout to prevent hanging
            response = litellm.completion(
                model=self.model_name,
                messages=messages,
                stream=True,
                timeout=120  # Increase timeout
            )
            
            # Track if we's in the reasoning phase
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
            error_msg = str(e)
            print(f"\nError during streaming: {error_msg}")
            
            # Provide more specific error messages
            if "rate limit" in error_msg.lower():
                error_response = "Error: Rate limit exceeded. Please try again later."
            elif "timeout" in error_msg.lower():
                error_response = "Error: Request timed out. The model may be overloaded."
            elif "connection" in error_msg.lower():
                error_response = "Error: Connection failed. Please check your internet connection."
            else:
                error_response = f"Error: {error_msg}"
                
            return full_response or error_response
    
    def _get_terminal_height(self) -> int:
        """
        Get the terminal height for proper screen clearing.
        
        Returns:
            The height of the terminal in lines
        """
        try:
            import shutil
            terminal_size = shutil.get_terminal_size()
            return terminal_size.lines
        except Exception:
            # Fallback to a reasonable default if we can't get the terminal size
            return 40


if __name__ == "__main__":
    # Simple test when run directly
    agent = Agent()
    print(f"Initialized agent with model: {agent.model_name}")
    
    # Test prompt if an argument is provided
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        print(f"Testing with prompt: {prompt}")
        response = agent.stream_reasoning(prompt)
        print("\nFinal response:")
        print(response)
