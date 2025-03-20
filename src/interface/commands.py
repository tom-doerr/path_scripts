"""
Command handling for the agent interface.
"""

import os
import sys
import datetime
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from rich.console import Console
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.markdown import Markdown

from src.agent.core import Agent
from src.utils.xml_tools import extract_xml_from_response
from .display import display_help, display_plan_tree, display_models, get_system_info
from src.interface.input import process_user_input, save_chat_history
from src.utils.input_schema import format_input_message
from src.agent.plan import generate_plan, update_plan
from src.utils.web_search import search_web
from src.utils.xml_tools import pretty_format_xml


def process_command(
    agent: Agent,
    command: List[str],
    chat_history: List[Dict[str, Any]],
    history_file: str,
    console: Console,
    multiline_input_mode: bool,
    multiline_input_buffer: List[str],
) -> None:
    """Process a command and handle the result."""
    """
    Process a command and handle the result.

    Args:
        agent: The agent instance
        command: List of command parts
        chat_history: The chat history
        history_file: Path to the history file
        console: Rich console instance
        multiline_input_mode: Whether multiline input mode is active
        multiline_input_buffer: Buffer for multiline input
    """
    if not command:
        return

    cmd = command[0].lower()
    args = command[1:]

    # Handle help command
    if cmd == "help":
        display_help(console)
        return

    # Handle exit command
    if cmd == "exit":
        console.print("[bold blue]Exiting...[/bold blue]")
        sys.exit(0)

    # Handle paste mode commands
    elif cmd == "paste":
        multiline_input_mode = True
        multiline_input_buffer.clear()
        console.print(
            "[bold yellow]Entering multiline paste mode. Type /end when finished.[/bold yellow]"
        )
        return

    elif cmd == "end":
        if multiline_input_mode:
            multiline_input_mode = False
            if multiline_input_buffer:
                _ = "\n".join(multiline_input_buffer)  # Store but don't use
                console.print(
                    f"[dim]Processing {len(multiline_input_buffer)} lines of input...[/dim]"
                )
                process_user_input(
                    agent, full_input, chat_history, history_file, console
                )
                multiline_input_buffer.clear()
            else:
                console.print("[yellow]No input to process[/yellow]")
        else:
            console.print("[yellow]Not in paste mode[/yellow]")
        return

    # Handle memory commands
    elif cmd == "memory":
        memory_content = _load_persistent_memory()
        try:
            # Format the XML for display
            memory_root = ET.fromstring(memory_content)

            formatted_memory = pretty_format_xml(
                ET.tostring(memory_root, encoding="unicode")
            )

            # Display as syntax-highlighted XML
            console.print("[bold blue]Agent Memory:[/bold blue]")
            console.print(Syntax(formatted_memory, "xml", theme="monokai"))
        except ET.ParseError as e:
            console.print(f"[bold red]Error parsing memory XML: {e}[/bold red]")
            console.print(memory_content)
        return

    elif cmd == "clear-memory":
        confirm = Prompt.ask(
            "Are you sure you want to clear the agent's memory?",
            choices=["y", "n"],
            default="n",
        )

        if confirm.lower() == "y":
            # Create default memory structure - simple and flexible
            default_memory = (
                "<memory>\n  <!-- Agent can structure this as needed -->\n</memory>"
            )
            with open("agent_memory.xml", "w") as f:
                f.write(default_memory)
            console.print("[bold green]Agent memory cleared[/bold green]")
        else:
            console.print("[bold yellow]Operation cancelled[/bold yellow]")
        return

    # Handle initialization
    elif cmd == "init":
        with console.status("[bold blue]Initializing agent...[/bold blue]"):
            agent.initialize()
        console.print("[bold green]Agent initialized successfully[/bold green]")
        return

    # Handle model commands
    elif cmd == "models":

        display_models(agent, console)
        return

    elif cmd == "model":
        if not args:
            console.print(f"[bold blue]Current model:[/bold blue] {agent.model_name}")
            console.print("[italic]Use /models to see available model aliases[/italic]")
            return

        model_name = args[0]

        # Check for model aliases
        model_aliases = {
            "flash": "openrouter/google/gemini-2.0-flash-001",
            "r1": "deepseek/deepseek-reasoner",
            "claude": "openrouter/anthropic/claude-3.7-sonnet",
            "gpt4": "openrouter/openai/gpt-4-turbo",
            "gpt3": "openrouter/openai/gpt-3.5-turbo",
            "mistral": "openrouter/mistralai/mistral-large",
            "llama3": "openrouter/meta-llama/llama-3-70b-instruct",
        }

        model_name = model_aliases.get(model_name, model_name)
            model_name = model_aliases[model_name]

        agent.model_name = model_name
        console.print(f"[bold green]Model changed to:[/bold green] {agent.model_name}")
        return

    # Handle plan commands
    elif cmd == "plan":
        # Use spec.md by default if no file specified
        spec_file = args[0] if args else "spec.md"
        console.print(f"[bold blue]Using specification file:[/bold blue] {spec_file}")
        try:
            with open(spec_file, "r") as f:
                spec = f.read()

            console.print(f"[bold blue]Using model:[/bold blue] {agent.model_name}")

            # Initialize if not already done
            if not agent.repository_info:
                with console.status("[bold blue]Initializing agent...[/bold blue]"):
                    agent.initialize()

            # Generate plan - don't use status context manager to allow streaming
            console.print("[bold blue]Generating plan...[/bold blue]", end=" ")
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

                # Import the input schema formatter

                # Get system information
                system_info = get_system_info()

                # Format the message with XML tags using the schema
                formatted_message = format_input_message(
                    message=f"Generate a plan based on the following specification:\n\n{spec}",
                    system_info=system_info,
                )


                result = generate_plan(agent, spec, formatted_message)

                # Save the plan to a file
                with open("agent_plan.xml", "w") as f:
                    f.write(result)

                # Extract plan XML for display
                plan_xml = extract_xml_from_response(result, "plan")
                if plan_xml:
                    console.print("\n\n[bold blue]Generated Plan:[/bold blue]")
                    display_plan_tree(console, result)
                else:
                    console.print(
                        "[bold red]Error:[/bold red] No plan found in response"
                    )

                console.print("[bold green]Plan saved to agent_plan.xml[/bold green]")

            except KeyboardInterrupt:
                console.print(
                    "\n[bold yellow]Operation cancelled by user[/bold yellow]"
                )

        except FileNotFoundError:
            console.print(
                f"[bold red]Error:[/bold red] Specification file '{spec_file}' not found"
            )
        return

    elif cmd == "display":
        # Load the plan from file if not already loaded
        try:
            with open("agent_plan.xml", "r") as f:
                xml_content = f.read()
                agent.plan_tree = extract_xml_from_response(xml_content, "plan")

            display_plan_tree(console, xml_content)
        except FileNotFoundError:
            console.print(
                "[bold red]Error:[/bold red] No plan file found. Generate a plan first."
            )
        return

    elif cmd == "update":
        if len(args) < 2:
            console.print("[bold red]Error:[/bold red] Missing task_id or status")
            return

        task_id = args[0]
        status = args[1]

        # Check for progress and notes flags
        progress = None
        notes = None

        for i, arg in enumerate(args[2:], 2):
            if arg.startswith("--progress="):
                progress = arg.split("=")[1]
            elif arg.startswith("--notes="):
                notes = arg.split("=")[1]
            elif i == 2 and not arg.startswith("--"):
                # For backward compatibility, treat the third argument as notes
                notes = arg

        # Load the plan from file if not already loaded
        if not agent.plan_tree:
            try:
                with open("agent_plan.xml", "r") as f:
                    xml_content = f.read()
                    agent.plan_tree = extract_xml_from_response(xml_content, "plan")
            except FileNotFoundError:
                console.print(
                    "[bold red]Error:[/bold red] No plan file found. Generate a plan first."
                )
                return

        with console.status(f"[bold blue]Updating task {task_id}...[/bold blue]"):

            result = update_plan(agent, task_id, status, notes, progress)

        # Save the updated plan
        with open("agent_plan.xml", "w") as f:
            f.write(result)

        console.print(f"[bold green]Task {task_id} updated to {status}[/bold green]")
        display_plan_tree(console, result)
        return

    # Handle history commands
    elif cmd == "history":
        # Display chat history
        count = 10  # Default to last 10 messages
        if args and args[0].isdigit():
            count = int(args[0])

        if not chat_history:
            console.print("[bold yellow]No chat history available[/bold yellow]")
            return

        # Get the specified number of messages from the end of history
        messages_to_show = (
            chat_history[-count:] if len(chat_history) > count else chat_history
        )

        console.print(
            f"[bold blue]Chat History (last {len(messages_to_show)} messages):[/bold blue]"
        )
        for i, msg in enumerate(messages_to_show):
            role = msg["role"]
            content = msg["content"]
            timestamp = msg.get("timestamp", "")

            # Format timestamp if available
            time_str = ""
            if timestamp:
                try:
                    dt = datetime.datetime.fromisoformat(timestamp)
                    time_str = f"[dim]{dt.strftime('%Y-%m-%d %H:%M:%S')}[/dim]"
                except Exception:
                    time_str = f"[dim]{timestamp}[/dim]"

            # Format based on role
            if role == "user":
                console.print(f"\n{time_str}")
                console.print(f"[bold green]User:[/bold green] {content}")
            else:
                console.print(f"\n{time_str}")

                # For assistant messages, try to extract and format the message part
                message_xml = extract_xml_from_response(content, "message")
                if message_xml:
                    try:
                        root = ET.fromstring(message_xml)
                        message_text = root.text if root.text else ""
                        console.print("[bold blue]Assistant:[/bold blue]")
                        console.print(Markdown(message_text))
                    except ET.ParseError:
                        console.print(
                            f"[bold blue]Assistant:[/bold blue] {content[:100]}..."
                        )
                else:
                    console.print(
                        f"[bold blue]Assistant:[/bold blue] {content[:100]}..."
                    )
        return

    elif cmd in ["clear-history", "reset"]:
        confirm = Prompt.ask(
            "Are you sure you want to clear the chat history?",
            choices=["y", "n"],
            default="n",
        )

        if confirm.lower() == "y":
            chat_history.clear()
            save_chat_history(chat_history, history_file)
            console.print("[bold green]Chat history cleared[/bold green]")
        else:
            console.print("[bold yellow]Operation cancelled[/bold yellow]")
        return

    # If we get here, it's an unknown command
    console.print(f"[bold red]Unknown command:[/bold red] {cmd}")
    console.print("Type [bold]help[/bold] for available commands")


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


    """
    Process a command and handle the result.

    Args:
        agent: The agent instance
        command: List of command parts
        chat_history: The chat history
        history_file: Path to the history file
        console: Rich console instance
        multiline_input_mode: Whether multiline input mode is active
        multiline_input_buffer: Buffer for multiline input
    """
    if not command:
        return

    cmd = command[0].lower()
    args = command[1:]

    # Handle paste mode commands
    if cmd == "paste":
        multiline_input_mode = True
        multiline_input_buffer.clear()
        console.print(
            "[bold yellow]Entering multiline paste mode. Type /end when finished.[/bold yellow]"
        )
        return

    if cmd == "end":
        if multiline_input_mode:
            multiline_input_mode = False
            if multiline_input_buffer:
                full_input = "\n".join(multiline_input_buffer)
                console.print(
                    f"[dim]Processing {len(multiline_input_buffer)} lines of input...[/dim]"
                )
                # This would need to call back to the interface to process the input
                # For now, just acknowledge
                console.print("[yellow]Input processing would happen here[/yellow]")
                multiline_input_buffer.clear()
            else:
                console.print("[yellow]No input to process[/yellow]")
        else:
            console.print("[yellow]Not in paste mode[/yellow]")
        return

    if cmd == "help":
        display_help(console)

    elif cmd == "exit":
        console.print("[bold blue]Exiting...[/bold blue]")
        sys.exit(0)

    elif cmd == "init":
        with console.status("[bold blue]Initializing agent...[/bold blue]"):
            agent.initialize()
        console.print("[bold green]Agent initialized successfully[/bold green]")

    elif cmd == "plan":
        # Use spec.md by default if no file specified
        spec_file = args[0] if args else "spec.md"
        console.print(f"[bold blue]Using specification file:[/bold blue] {spec_file}")
        try:
            with open(spec_file, "r") as f:
                spec = f.read()

            console.print(f"[bold blue]Using model:[/bold blue] {agent.model_name}")

            # Initialize if not already done
            if not agent.repository_info:
                with console.status("[bold blue]Initializing agent...[/bold blue]"):
                    agent.initialize()

            # Generate plan - don't use status context manager to allow streaming
            console.print("[bold blue]Generating plan...[/bold blue]")
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
                result = agent.generate_plan(spec)

                # Save the plan to a file
                with open("agent_plan.xml", "w") as f:
                    f.write(result)

                # Extract plan XML for display
                plan_xml = agent.extract_xml_from_response(result, "plan")
                if plan_xml:
                    console.print("\n\n[bold blue]Generated Plan:[/bold blue]")
                    display_plan_tree(console, result)
                else:
                    console.print(
                        "[bold red]Error:[/bold red] No plan found in response"
                    )

                console.print("[bold green]Plan saved to agent_plan.xml[/bold green]")

            except KeyboardInterrupt:
                console.print(
                    "\n[bold yellow]Operation cancelled by user[/bold yellow]"
                )

        except FileNotFoundError:
            console.print(
                f"[bold red]Error:[/bold red] Specification file '{spec_file}' not found"
            )

    elif cmd == "model":
        if not args:
            console.print(f"[bold blue]Current model:[/bold blue] {agent.model_name}")
            return

        model_name = args[0]

        # Check for model aliases
        model_aliases = {
            "flash": "openrouter/google/gemini-2.0-flash-001",
            "r1": "deepseek/deepseek-reasoner",
            "claude": "openrouter/anthropic/claude-3.7-sonnet",
            "gpt4": "openrouter/openai/gpt-4-turbo",
            "gpt3": "openrouter/openai/gpt-3.5-turbo",
            "mistral": "openrouter/mistralai/mistral-large",
            "llama3": "openrouter/meta-llama/llama-3-70b-instruct",
        }

        model_name = model_aliases.get(model_name, model_name)
            model_name = model_aliases[model_name]

        agent.model_name = model_name
        console.print(f"[bold green]Model changed to:[/bold green] {agent.model_name}")

    elif cmd == "models":
        console.print("[bold blue]Available models:[/bold blue]")
        console.print("- [bold]flash[/bold]: openrouter/google/gemini-2.0-flash-001")
        console.print("- [bold]r1[/bold]: deepseek/deepseek-reasoner")
        console.print("- [bold]claude[/bold]: openrouter/anthropic/claude-3.7-sonnet")
        console.print("\n[bold blue]Current model:[/bold blue] " + agent.model_name)

    elif cmd == "search":
        if not args:
            console.print("[bold red]Error:[/bold red] Please provide a search query")
            return
        
        query = " ".join(args)
        results = search_web(query)
        
        if not results:
            console.print("[bold yellow]No results found[/bold yellow]")
            return
            
        console.print(f"[bold blue]Search results for '{query}':[/bold blue]")
        for i, result in enumerate(results, 1):
            console.print(f"{i}. [bold]{result['title']}[/bold]")
            console.print(f"   {result['snippet']}")
            console.print(f"   [dim]{result['link']}[/dim]")
            console.print()

    else:
        console.print(f"[bold red]Unknown command:[/bold red] {cmd}")
        console.print("Type [bold]/help[/bold] for available commands")


