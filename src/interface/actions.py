import os
import subprocess
import datetime
from typing import Tuple, Dict, List, Optional
import xml.etree.ElementTree as ET
from rich.console import Console
from rich.syntax import Syntax
from rich.prompt import Prompt

def execute_action(action_element, console: Console) -> bool:
    """Execute a single action from the XML"""
    try:
        action_type = action_element.get("type", "unknown")
        path = action_element.get("path", "")
        command = action_element.get("command", "")
        
        # Determine syntax highlighting language based on file extension
        language = "python"  # default
        if path:
            ext = os.path.splitext(path)[1].lower()
            if ext in ['.js', '.jsx']:
                language = "javascript"
            elif ext in ['.html', '.htm']:
                language = "html"
            elif ext in ['.css']:
                language = "css"
            elif ext in ['.json']:
                language = "json"
            elif ext in ['.md']:
                language = "markdown"
            elif ext in ['.sh']:
                language = "bash"
            elif ext in ['.yml', '.yaml']:
                language = "yaml"
        
        # Ask for confirmation before executing
        if action_type == "create_file":
            content = action_element.text.strip() if action_element.text else ""
            console.print(f"[bold cyan]Action:[/bold cyan] Create file '{path}'")
            console.print(Syntax(content, language, theme="monokai"))
            
        elif action_type == "modify_file":
            console.print(f"[bold cyan]Action:[/bold cyan] Modify file '{path}'")
            for change in action_element.findall("./change"):
                original = change.find("original").text if change.find("original") is not None else ""
                new = change.find("new").text if change.find("new") is not None else ""
                console.print("[bold red]- Original:[/bold red]")
                console.print(Syntax(original, language, theme="monokai"))
                console.print("[bold green]+ New:[/bold green]")
                console.print(Syntax(new, language, theme="monokai"))
                
        elif action_type == "run_command":
            console.print(f"[bold cyan]Action:[/bold cyan] Run command '{command}'")
        
        # Ask for confirmation
        confirm = Prompt.ask(
            "\nExecute this action?", 
            choices=["Y", "n"], 
            default="Y"
        )
            
        if confirm.lower() != "y":
            console.print("[bold yellow]Action skipped[/bold yellow]")
            return False
        
        # Execute the action
        if action_type == "create_file":
            # Create the file with the content
            content = action_element.text.strip() if action_element.text else ""
            
            # Create directory if it doesn't exist
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                console.print(f"[bold green]Created directory: {directory}[/bold green]")
            
            with open(path, 'w') as f:
                f.write(content)
            console.print(f"[bold green]Created file: {path}[/bold green]")
            
            # Make executable if it's a script
            if path.endswith('.py') or not os.path.splitext(path)[1]:
                os.chmod(path, 0o755)
                console.print(f"[bold green]Made file executable: {path}[/bold green]")
            
            return True
            
        elif action_type == "modify_file":
            if not os.path.exists(path):
                console.print(f"[bold red]Error: File {path} does not exist[/bold red]")
                return False
            
            # Read the original file
            with open(path, 'r') as f:
                file_content = f.read()
            
            # Apply each change
            changes_applied = False
            for change in action_element.findall("./change"):
                original = change.find("original").text if change.find("original") is not None else ""
                new = change.find("new").text if change.find("new") is not None else ""
                
                if original in file_content:
                    file_content = file_content.replace(original, new)
                    changes_applied = True
                else:
                    console.print(f"[bold yellow]Warning: Could not find text to replace in {path}[/bold yellow]")
            
            # Write the modified content back
            if changes_applied:
                with open(path, 'w') as f:
                    f.write(file_content)
                console.print(f"[bold green]Modified file: {path}[/bold green]")
                return True
            else:
                console.print(f"[bold yellow]No changes applied to {path}[/bold yellow]")
                return False
            
        elif action_type == "run_command":
            console.print(f"[bold blue]Running command: {command}[/bold blue]")
            
            # Run the command and capture output
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Stream output in real-time
            for line in process.stdout:
                console.print(line.rstrip())
            
            # Wait for process to complete
            process.wait()
            
            if process.returncode == 0:
                console.print(f"[bold green]Command completed successfully[/bold green]")
                return True
            else:
                stderr = process.stderr.read()
                console.print(f"[bold red]Command failed with exit code {process.returncode}[/bold red]")
                if stderr:
                    console.print(f"[bold red]Error: {stderr}[/bold red]")
                return False
        
        else:
            console.print(f"[bold yellow]Unknown action type: {action_type}[/bold yellow]")
            return False
            
    except Exception as e:
        console.print(f"[bold red]Error executing action: {e}[/bold red]")
        return False

def execute_file_edit(edit_element, console: Console) -> bool:
    """Execute a file edit from the XML"""
    try:
        path = edit_element.get("path", "")
        if not path:
            console.print("[bold red]Error: Missing file path in edit[/bold red]")
            return False
            
        # Determine syntax highlighting language based on file extension
        language = "python"  # default
        if path:
            ext = os.path.splitext(path)[1].lower()
            if ext in ['.js', '.jsx']:
                language = "javascript"
            elif ext in ['.html', '.htm']:
                language = "html"
            elif ext in ['.css']:
                language = "css"
            elif ext in ['.json']:
                language = "json"
            elif ext in ['.md']:
                language = "markdown"
            elif ext in ['.sh']:
                language = "bash"
            elif ext in ['.yml', '.yaml']:
                language = "yaml"
        
        # Get search and replace elements
        search_elem = edit_element.find("search")
        replace_elem = edit_element.find("replace")
        
        if search_elem is None or replace_elem is None:
            console.print("[bold red]Error: Missing search or replace elements[/bold red]")
            return False
            
        search_text = search_elem.text if search_elem.text else ""
        replace_text = replace_elem.text if replace_elem.text else ""
        
        # Display the edit
        console.print(f"[bold cyan]File Edit:[/bold cyan] {path}")
        console.print("[bold red]- Search:[/bold red]")
        console.print(Syntax(search_text, language, theme="monokai"))
        console.print("[bold green]+ Replace:[/bold green]")
        console.print(Syntax(replace_text, language, theme="monokai"))
        
        # Ask for confirmation
        confirm = Prompt.ask(
            "\nApply this edit?", 
            choices=["Y", "n"], 
            default="Y"
        )
        
        if confirm.lower() != "y":
            console.print("[bold yellow]Edit skipped[/bold yellow]")
            return False
            
        # Check if file exists
        if not os.path.exists(path):
            # Ask if we should create the file
            create_file = Prompt.ask(
                f"File {path} does not exist. Create it?",
                choices=["Y", "n"],
                default="Y"
            )
            
            if create_file.lower() != "y":
                console.print("[bold yellow]Edit skipped[/bold yellow]")
                return False
                
            # Create directory if it doesn't exist
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                console.print(f"[bold green]Created directory: {directory}[/bold green]")
            
            # Create empty file
            with open(path, 'w') as f:
                pass
            console.print(f"[bold green]Created file: {path}[/bold green]")
            
            # For new files, just write the replace text
            with open(path, 'w') as f:
                f.write(replace_text)
            console.print(f"[bold green]Applied edit to {path}[/bold green]")
            return True
        
        # Read the file content
        with open(path, 'r') as f:
            content = f.read()
            
        # Apply the search and replace
        if search_text == "":
            # Empty search means append to the file
            new_content = content + replace_text
            console.print("[bold blue]Appending to file[/bold blue]")
        else:
            # Replace the search text with the replace text
            if search_text not in content:
                console.print(f"[bold yellow]Warning: Search text not found in {path}[/bold yellow]")
                return False
                
            new_content = content.replace(search_text, replace_text, 1)
            
        # Write the new content
        with open(path, 'w') as f:
            f.write(new_content)
            
        console.print(f"[bold green]Applied edit to {path}[/bold green]")
        return True
        
    except Exception as e:
        console.print(f"[bold red]Error executing file edit: {e}[/bold red]")
        return False

def execute_shell_command(command: str, console: Console, auto_run: bool = False) -> Tuple[bool, str]:
    """Execute a shell command with optional auto-run"""
    console.print(f"[bold cyan]Shell Command:[/bold cyan] {command}")
    
    execution_context = {
        "command": command,
        "auto_run": auto_run,
        "user_approved": False,
        "success": False,
        "output": "",
        "error": "",
        "return_code": None,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    if not auto_run:
        confirm = Prompt.ask(
            "\nExecute this shell command?", 
            choices=["Y", "n"], 
            default="Y"
        )
        
        if confirm.lower() != "y":
            console.print("[bold yellow]Command execution skipped[/bold yellow]")
            execution_context["user_approved"] = False
            return False, _format_execution_context(execution_context)
        
        execution_context["user_approved"] = True
    else:
        execution_context["user_approved"] = True
    
    console.print(f"[bold blue]Running command: {command}[/bold blue]")
    
    # Run the command and capture output
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Collect output while streaming
    output_lines = []
    
    # Stream output in real-time
    for line in process.stdout:
        output_lines.append(line.rstrip())
        console.print(line.rstrip())
    
    # Wait for process to complete
    process.wait()
    
    # Get stderr if any
    stderr = process.stderr.read()
    
    # Truncate output to last 5000 characters
    full_output = "\n".join(output_lines)
    if len(full_output) > 5000:
        truncated_output = "... (output truncated) ...\n" + full_output[-5000:]
    else:
        truncated_output = full_output
        
    execution_context["output"] = truncated_output
    execution_context["error"] = stderr
    execution_context["return_code"] = process.returncode
    execution_context["success"] = (process.returncode == 0)
    
    if process.returncode == 0:
        console.print(f"[bold green]Command completed successfully[/bold green]")
        return True, _format_execution_context(execution_context)
    else:
        console.print(f"[bold red]Command failed with exit code {process.returncode}[/bold red]")
        if stderr:
            console.print(f"[bold red]Error: {stderr}[/bold red]")
        return False, _format_execution_context(execution_context)

def _format_execution_context(context: Dict) -> str:
    """Format execution context as XML"""
    xml = f"""<execution_context>
  <command>{context['command']}</command>
  <auto_run>{str(context['auto_run']).lower()}</auto_run>
  <user_approved>{str(context['user_approved']).lower()}</user_approved>
  <success>{str(context['success']).lower()}</success>
  <return_code>{context['return_code']}</return_code>
  <timestamp>{context['timestamp']}</timestamp>
  <output><![CDATA[{context['output']}]]></output>
  <error><![CDATA[{context['error']}]]></error>
</execution_context>"""
    return xml

def update_dependent_tasks(root, completed_task_id, console: Console):
    """Update tasks that depend on the completed task"""
    # Find all tasks that depend on the completed task
    for task in root.findall(".//task"):
        depends_on = task.get("depends_on", "")
        if depends_on:
            dependencies = [dep.strip() for dep in depends_on.split(",")]
            if completed_task_id in dependencies:
                # Check if all dependencies are completed
                all_deps_completed = True
                for dep_id in dependencies:
                    if dep_id == completed_task_id:
                        continue  # This one is completed
                    
                    dep_task = root.find(f".//task[@id='{dep_id}']")
                    if dep_task is None or dep_task.get("status") != "completed":
                        all_deps_completed = False
                        break
                
                # If all dependencies are completed, mark this task as ready
                if all_deps_completed:
                    current_status = task.get("status", "pending")
                    if current_status == "pending":
                        task.set("status", "ready")
                        console.print(f"[bold blue]Task {task.get('id')} is now ready to be executed[/bold blue]")
