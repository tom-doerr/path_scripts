"""
Input handling for the agent interface.
"""

import os
import datetime
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Callable
from rich.console import Console

from src.interface.display import get_system_info
from src.interface.chat import process_chat_response


def process_user_input(
    agent,
    user_input: str,
    chat_history: List[Dict[str, Any]],
    history_file: str,
    console: Console,
):
    """Process user input and send to the model."""

    # Add user message to history
    timestamp = datetime.datetime.now().isoformat()
    chat_history.append({"role": "user", "content": user_input, "timestamp": timestamp})
    save_chat_history(chat_history, history_file)

    # Format history for the prompt
    formatted_history = _format_history_for_prompt(chat_history)

    # Get persistent memory
    memory_content = _load_persistent_memory()

    # Get system information
    system_info = get_system_info()

    # Import the input schema formatter
    from src.utils.input_schema import format_input_message

    # Format the message with XML tags using the schema
    formatted_input = format_input_message(
        message=user_input,
        system_info=system_info,
        memory=memory_content,
        history=formatted_history,
    )

    # Construct a prompt that instructs the model to respond in XML format
    from src.interface.chat import process_chat_message

    prompt = process_chat_message(
        formatted_input,
        formatted_history,
        memory_content,
        system_info,
        getattr(agent, "config", {}),
    )

    try:
        # Set a callback to handle streaming in the interface
        def stream_callback(content, is_reasoning=False):
            if is_reasoning:
                # Use yellow color for reasoning tokens
                console.print(f"[yellow]{content}[/yellow]", end="")
            else:
                # Use rich for normal content
                console.print(content, end="", highlight=False)

        # Pass the callback to the agent
        agent.stream_callback = stream_callback
        response = agent.stream_reasoning(prompt)

        # Process the response
        process_chat_response(
            agent,
            console,
            response,
            chat_history,
            _update_persistent_memory,
            _get_terminal_height,
            _load_persistent_memory,
            _format_history_for_prompt,
            lambda: save_chat_history(chat_history, history_file),
        )
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operation cancelled by user[/bold yellow]")


def save_chat_history(chat_history: List[Dict[str, Any]], history_file: str):
    """Save chat history to file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(history_file), exist_ok=True)

        with open(history_file, "w") as f:
            json.dump(chat_history, f, indent=2)
    except Exception as e:
        print(f"Could not save chat history: {e}")


def _format_history_for_prompt(chat_history: List[Dict[str, Any]]) -> str:
    """Format chat history for inclusion in the prompt."""
    # Limit history to last 10 messages to avoid context overflow
    recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history

    formatted_history = []
    for msg in recent_history:
        role = msg["role"]
        content = msg["content"]
        timestamp = msg.get("timestamp", "")

        # Format as XML
        entry = f'<entry role="{role}" timestamp="{timestamp}">'

        # For assistant messages, try to extract just the message part to keep history cleaner
        if role == "assistant":
            from src.utils.xml_tools import extract_xml_from_response

            message_xml = extract_xml_from_response(content, "message")
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


def _load_persistent_memory() -> str:
    """Load memory from file."""
    memory_file = "agent_memory.xml"
    try:
        if os.path.exists(memory_file):
            with open(memory_file, "r") as f:
                return f.read()
        else:
            # Create default memory structure - simple and flexible
            default_memory = (
                "<memory>\n  <!-- Agent can structure this as needed -->\n</memory>"
            )
            with open(memory_file, "w") as f:
                f.write(default_memory)
            return default_memory
    except Exception as e:
        print(f"Could not load memory: {e}")
        return "<memory></memory>"


def _update_persistent_memory(memory_updates_xml):
    """Update memory based on model's instructions."""
    if not memory_updates_xml:
        return

    try:
        memory_file = "agent_memory.xml"
        current_memory = _load_persistent_memory()

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
                memory_str = ET.tostring(memory_root, encoding="unicode")

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
        from src.utils.xml_tools import pretty_format_xml

        updated_memory = pretty_format_xml(ET.tostring(memory_root, encoding="unicode"))
        with open(memory_file, "w") as f:
            f.write(updated_memory)

        print("Memory updated")

    except Exception as e:
        print(f"Error updating memory: {e}")


def _get_terminal_height() -> int:
    """Get the terminal height for proper screen clearing."""
    try:
        import shutil

        terminal_size = shutil.get_terminal_size()
        return terminal_size.lines
    except Exception:
        # Fallback to a reasonable default if we can't get the terminal size
        return 40


def _format_history_for_prompt(chat_history: List[Dict[str, Any]]) -> str:
    """
    Format chat history for inclusion in the prompt.

    Args:
        chat_history: List of chat history entries

    Returns:
        Formatted history string
    """
    formatted_history = []

    # Get the last few messages (up to 10)
    recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history

    for entry in recent_history:
        role = entry.get("role", "unknown")
        content = entry.get("content", "")
        formatted_history.append(f'<message role="{role}">{content}</message>')

    return "\n".join(formatted_history)


def save_chat_history(chat_history: List[Dict[str, Any]], history_file: str):
    """
    Save chat history to file.

    Args:
        chat_history: List of chat history entries
        history_file: Path to the history file
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(history_file), exist_ok=True)

        with open(history_file, "w") as f:
            import json

            json.dump(chat_history, f, indent=2)
    except Exception as e:
        print(f"Could not save chat history: {e}")


def _load_persistent_memory() -> str:
    """
    Load memory from file.

    Returns:
        Memory content as string
    """
    memory_file = "agent_memory.xml"
    try:
        if os.path.exists(memory_file):
            with open(memory_file, "r") as f:
                return f.read()
        else:
            # Create default memory structure - simple and flexible
            default_memory = (
                "<memory>\n  <!-- Agent can structure this as needed -->\n</memory>"
            )
            with open(memory_file, "w") as f:
                f.write(default_memory)
            return default_memory
    except Exception as e:
        print(f"Could not load memory: {e}")
        return "<memory></memory>"


def _update_persistent_memory(memory_updates_xml):
    """
    Update the persistent memory with the provided updates.

    Args:
        memory_updates_xml: XML string containing memory updates
    """
    try:
        # Parse the memory updates
        updates_root = ET.fromstring(memory_updates_xml)

        # Load the current memory
        memory_content = _load_persistent_memory()
        memory_root = ET.fromstring(memory_content)

        # Process edits
        for edit in updates_root.findall("./edit"):
            search = edit.find("./search")
            replace = edit.find("./replace")

            if search is not None and replace is not None:
                search_text = search.text if search.text else ""
                replace_text = replace.text if replace.text else ""

                # Convert memory to string for search/replace
                memory_str = ET.tostring(memory_root, encoding="unicode")
                memory_str = memory_str.replace(search_text, replace_text)

                # Parse back to XML
                memory_root = ET.fromstring(memory_str)

        # Process appends
        for append in updates_root.findall("./append"):
            append_text = append.text if append.text else ""

            # Create a temporary root to parse the append text
            try:
                # Try to parse as XML first
                append_elem = ET.fromstring(f"<root>{append_text}</root>")
                for child in append_elem:
                    memory_root.append(child)
            except ET.ParseError:
                # If not valid XML, add as text node to a new element
                new_elem = ET.SubElement(memory_root, "entry")
                new_elem.text = append_text
                new_elem.set("timestamp", datetime.datetime.now().isoformat())

        # Save the updated memory
        with open("agent_memory.xml", "w") as f:
            f.write(ET.tostring(memory_root, encoding="unicode"))

    except ET.ParseError as e:
        print(f"Could not parse memory updates XML: {e}")
    except Exception as e:
        print(f"Error updating memory: {e}")


def _get_terminal_height() -> int:
    """
    Get the terminal height.

    Returns:
        Terminal height in lines
    """
    try:
        import os

        return os.get_terminal_size().lines
    except:
        return 24  # Fallback value
