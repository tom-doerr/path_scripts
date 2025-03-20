#!/usr/bin/env python3
"""Core Agent functionality for model interaction and reasoning."""

import os
import sys
import threading
import json
from typing import Dict, List, Optional, Any, Tuple, Callable
import xml.etree.ElementTree as ET
import litellm
from rich.console import Console

from .repository import analyze_repository

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
"""Core agent functionality."""

import os
import sys
import json
import datetime
from typing import Dict, List, Optional, Any, Tuple
import litellm
from rich.console import Console

class Agent:
    """Main agent class for handling model interactions and reasoning."""
    
    def __init__(self, model_name: str = "openrouter/deepseek/deepseek-r1"):
        self.console = Console()
        self.model_name = model_name
        self.plan_tree = None
        self.plan_lock = threading.Lock()  # Thread safety for plan_tree access
        self.repository_info = {}
        self.config = {
            "stream_reasoning": True,
            "verbose": True
        }
        self.stream_callback = None
        
    def initialize(self, repo_path: str = ".") -> None:
        """Initialize the agent with repository information"""
        from utils.file_ops import read_file
        self.repository_info = {"path": repo_path}
        print(f"Agent initialized for repository: {repo_path}")
    
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
    
    def _get_terminal_height(self) -> int:
        """Get the terminal height for proper screen clearing"""
        try:
            import shutil
            terminal_size = shutil.get_terminal_size()
            return terminal_size.lines
        except Exception:
            # Fallback to a reasonable default if we can't get the terminal size
            return 40
            
    def pretty_format_xml(self, xml_string: str) -> str:
        """Format XML string in a cleaner way than minidom."""
        try:
            import xml.etree.ElementTree as ET
            from xml.dom import minidom
            
            # Parse the XML
            root = ET.fromstring(xml_string)
            
            # Define a recursive function to format elements
            def format_elem(elem, level=0):
                indent = "  " * level
                result = f"{indent}<{elem.tag}"
                
                # Add attributes
                for name, value in elem.attrib.items():
                    result += f' {name}="{value}"'
                
                # Check if element has children or text
                if len(elem) == 0 and (elem.text is None or elem.text.strip() == ""):
                    result += "/>\n"
                else:
                    result += ">"
                    
                    # Add text if present and not just whitespace
                    if elem.text and elem.text.strip():
                        if "\n" in elem.text:
                            # For multiline text, add a newline after the opening tag
                            result += "\n"
                            # Indent each line of the text
                            text_lines = elem.text.split("\n")
                            for line in text_lines:
                                if line.strip():  # Skip empty lines
                                    result += f"{indent}  {line.strip()}\n"
                        else:
                            result += elem.text
                    
                    # Add children
                    if len(elem) > 0:
                        result += "\n"
                        for child in elem:
                            result += format_elem(child, level + 1)
                        result += f"{indent}"
                    
                    result += f"</{elem.tag}>\n"
                
                return result
            
            # Start formatting from the root
            formatted_xml = format_elem(root)
            return formatted_xml
            
        except Exception as e:
            print(f"Error formatting XML: {e}")
            return xml_string  # Return original if formatting fails
