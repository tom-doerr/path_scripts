import datetime
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Callable, Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.prompt import Prompt

from src.interface.actions import execute_action, execute_file_edit, execute_shell_command
from src.utils.xml_schema import get_schema

def process_chat_message(
    formatted_message: str, 
    formatted_history: str, 
    memory_content: str,
    system_info: Dict[str, str]
) -> str:
    """Prepare the chat message to send to the model"""
    # Get current date, time and timezone
    now = datetime.datetime.now()
    timezone = datetime.datetime.now().astimezone().tzinfo
    
    # Get the XML schema
    xml_schema = get_schema()
    
    # Import the input schema formatter
    from src.utils.input_schema import format_input_message
    
    # Format the message with XML tags using the schema if it's not already formatted
    if not formatted_message.strip().startswith("<input>"):
        formatted_message = format_input_message(
            message=formatted_message,
            system_info=system_info,
            memory=memory_content,
            history=formatted_history
        )
    
    # Get the response schema
    response_schema = get_schema()
    
    # Construct a prompt that instructs the model to respond in XML format
    prompt = f"""<xml>
  <system>
    <instructions>
      You are an AI assistant that can respond to user queries and also perform actions.
      You must respond using the response schema provided below.
      For shell commands, set safe_to_autorun="true" only for commands that are completely safe and have no destructive potential.
      When you need to update your persistent memory, use the memory_updates tag to edit or add information.
      Use the execution_status tag to indicate if you've completed the task or need more input from the user.
    </instructions>
    <context>
      <system_info>
        <date>{now.strftime('%Y-%m-%d')}</date>
        <time>{now.strftime('%H:%M:%S')}</time>
        <timezone>{timezone}</timezone>
        <platform>{system_info['platform']}</platform>
        <shell>{system_info['shell']}</shell>
      </system_info>
      <conversation_history>
        {formatted_history}
      </conversation_history>
      <memory>
        {memory_content}
      </memory>
      {formatted_message}
    </context>
    <response_schema>
      {response_schema}
    </response_schema>
  </system>
</xml>"""
    
    # Print the full prompt for debugging
    print("\n=== Message Sent to Model ===\n")
    print(prompt)
    print("\n=== End Message ===\n")
    
    # Return the XML-formatted prompt
    
    return prompt

def _should_continue_execution(execution_contexts: List[str]) -> bool:
    """Determine if we should continue execution based on command results"""
    # Parse each execution context to check for success
    for context_xml in execution_contexts:
        try:
            root = ET.fromstring(context_xml)
            success_elem = root.find("./success")
            if success_elem is not None and success_elem.text == "true":
                # At least one successful command means we should continue
                return True
        except ET.ParseError:
            continue
    
    # Ask the user if we should continue despite no successful commands
    confirm = Prompt.ask(
        "\nNo commands succeeded. Continue with model execution?", 
        choices=["Y", "n"], 
        default="Y"
    )
    return confirm.lower() == "y"

def _continue_execution_with_context(
    agent,
    console: Console,
    previous_message_xml: str, 
    execution_contexts: List[str],
    process_chat_response_callback: Callable
):
    """Continue execution with the model using command execution context"""
    console.print("\n[bold blue]Continuing execution with command results...[/bold blue]")
    
    # Extract message content if available
    message_content = ""
    if previous_message_xml:
        try:
            root = ET.fromstring(previous_message_xml)
            message_content = root.text if root.text else ""
        except ET.ParseError:
            message_content = "Error parsing previous message"
    
    # Construct a prompt with execution contexts
    contexts_xml = "\n".join(execution_contexts)
    
    # Get current date, time and timezone for context
    now = datetime.datetime.now()
    timezone = datetime.datetime.now().astimezone().tzinfo
    
    # Get the XML schema
    xml_schema = get_schema()
    
    # Get system information
    from src.interface.display import get_system_info
    system_info = get_system_info()
    
    # Import the input schema formatter
    from src.utils.input_schema import format_input_message
    
    # Format the execution context
    execution_context = {
        "command": "Previous commands",
        "output": contexts_xml,
        "exit_code": 0
    }
    
    # Format the message with XML tags using the schema
    formatted_message = format_input_message(
        message=message_content,
        system_info=system_info,
        execution_context=execution_context
    )
    
    # Print the model being used
    print("\n=== Message Sent to Model ===\n")
    print(f"Model: {agent.model_name}")
    
    # Get the response schema
    response_schema = xml_schema
    
    prompt = f"""<xml>
  <system>
    <instructions>
      You are continuing a task based on the results of previous commands.
      Based on these results, please continue with the task. 
      You must respond using the response schema provided below.
    </instructions>
    <context>
      <previous_message>{message_content}</previous_message>
      <command_results>
        {contexts_xml}
      </command_results>
      <system_info>
        <date>{now.strftime('%Y-%m-%d')}</date>
        <time>{now.strftime('%H:%M:%S')}</time>
        <timezone>{timezone}</timezone>
      </system_info>
      {formatted_message}
    </context>
    <response_schema>
      {response_schema}
    </response_schema>
  </system>
</xml>"""
    
    # Print the full prompt
    print(prompt)
    print("\n=== End Message ===\n")
    
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
    
    # Process the response using the provided callback
    process_chat_response_callback(response)

def process_chat_response(
    agent,
    console: Console,
    response: str, 
    chat_history: List[Dict[str, Any]],
    update_memory_callback: Callable,
    get_terminal_height_callback: Callable,
    load_memory_callback: Callable,
    format_history_callback: Callable,
    save_history_callback: Callable
):
    """Process the XML response from the model chat"""
    console.print("\n")
    
    # Display full XML response
    console.print("[bold blue]Full Agent Response XML:[/bold blue]")
    try:
        formatted_xml = agent.pretty_format_xml(response)
        console.print(Syntax(formatted_xml, "xml", theme="monokai", line_numbers=True))
    except Exception as e:
        console.print(f"[red]Error formatting XML: {e}[/red]")
        console.print(response)

    # Extract different parts of the response
    message_xml = agent.extract_xml_from_response(response, "message")
    actions_xml = agent.extract_xml_from_response(response, "actions")
    shell_commands_xml = agent.extract_xml_from_response(response, "shell_commands")
    file_edits_xml = agent.extract_xml_from_response(response, "file_edits")
    memory_updates_xml = agent.extract_xml_from_response(response, "memory_updates")
    execution_status_xml = agent.extract_xml_from_response(response, "execution_status")
    
    # Extract only the non-reasoning part for history
    # We don't want to save the reasoning tokens to avoid polluting the context
        
    # Combine the extracted parts for history
    history_content = ""
    for xml_part in [message_xml, actions_xml, shell_commands_xml, file_edits_xml, execution_status_xml]:
        if xml_part:
            history_content += xml_part + "\n"
        
    if not history_content:
        history_content = response  # Fallback to full response if extraction failed
        
    # Add response to history
    timestamp = datetime.datetime.now().isoformat()
    chat_history.append({
        "role": "assistant",
        "content": history_content,
        "timestamp": timestamp
    })
        
    # Save updated history
    save_history_callback()
    
    # Process memory updates if present
    if memory_updates_xml:
        update_memory_callback(memory_updates_xml)
    
    # Process message if present
    if message_xml:
        try:
            # Parse the XML to get just the text content
            root = ET.fromstring(message_xml)
            message_text = root.text if root.text else ""
            
            # Display the message as markdown
            console.print("")
            console.print(Markdown(message_text))
            console.print("")
        except ET.ParseError:
            # Fallback if parsing fails
            console.print(f"\n{message_xml}\n")
    
    # Process actions if present
    if actions_xml:
        try:
            actions_root = ET.fromstring(actions_xml)
            actions = actions_root.findall("./action")
            
            if actions:
                console.print("[bold blue]The model suggests the following actions:[/bold blue]")
                
                for action in actions:
                    execute_action(action, console)
                    
        except ET.ParseError as e:
            console.print(f"[bold red]Error parsing actions XML: {e}[/bold red]")
    
    # Process file edits if present
    if file_edits_xml:
        try:
            edits_root = ET.fromstring(file_edits_xml)
            edits = edits_root.findall("./edit")
            
            if edits:
                console.print("[bold blue]The model suggests the following file edits:[/bold blue]")
                
                for edit in edits:
                    execute_file_edit(edit, console)
                    
        except ET.ParseError as e:
            console.print(f"[bold red]Error parsing file edits XML: {e}[/bold red]")
    
    # Process shell commands if present
    if shell_commands_xml:
        try:
            commands_root = ET.fromstring(shell_commands_xml)
            commands = commands_root.findall("./command")
            
            execution_contexts = []
            
            if commands:
                console.print("[bold blue]The model suggests the following shell commands:[/bold blue]")
                
                for cmd_elem in commands:
                    command = cmd_elem.text.strip() if cmd_elem.text else ""
                    auto_run = cmd_elem.get("safe_to_autorun", "false").lower() == "true"
                    
                    if auto_run:
                        console.print(f"[bold green]Auto-running safe command:[/bold green] {command}")
                        success, context_xml = execute_shell_command(command, console, auto_run=True)
                    else:
                        success, context_xml = execute_shell_command(command, console, auto_run=False)
                    
                    execution_contexts.append(context_xml)
            
            # If there are execution contexts and we need to continue with the model
            if execution_contexts and _should_continue_execution(execution_contexts):
                # Create a callback that will call this function again
                def process_response_callback(response):
                    process_chat_response(
                        agent, 
                        console, 
                        response, 
                        chat_history,
                        update_memory_callback,
                        get_terminal_height_callback,
                        load_memory_callback,
                        format_history_callback,
                        save_history_callback
                    )
                
                _continue_execution_with_context(
                    agent,
                    console,
                    message_xml, 
                    execution_contexts,
                    process_response_callback
                )
                    
        except ET.ParseError as e:
            console.print(f"[bold red]Error parsing shell commands XML: {e}[/bold red]")
    
    # Process execution status if present
    if execution_status_xml:
        try:
            status_root = ET.fromstring(execution_status_xml)
            complete = status_root.get("complete", "false").lower() == "true"
            needs_input = status_root.get("needs_user_input", "false").lower() == "true"
            
            status_message = ""
            message_elem = status_root.find("./message")
            if message_elem is not None and message_elem.text:
                status_message = message_elem.text
            
            if complete:
                console.print("[bold green]✓ Task completed[/bold green]")
                if status_message:
                    console.print(f"[green]{status_message}[/green]")
            elif needs_input:
                console.print("[bold yellow]⚠ Waiting for user input[/bold yellow]")
                if status_message:
                    console.print(f"[yellow]{status_message}[/yellow]")
            else:
                console.print("[bold blue]⟳ Task in progress[/bold blue]")
                if status_message:
                    console.print(f"[blue]{status_message}[/blue]")
            
        except ET.ParseError as e:
            console.print(f"[bold red]Error parsing execution status XML: {e}[/bold red]")
