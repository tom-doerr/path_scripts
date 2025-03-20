"""
XML schema definitions for input messages to the model.
"""
from typing import Dict, Any, Optional, List

INPUT_SCHEMA = """
<xml_schema>
  <!-- Input schema - all messages to the model should follow this structure -->
  <input>
    <!-- System context information -->
    <system_info>
      <platform>Operating system and version</platform>
      <python_version>Python version</python_version>
      <shell>User's shell</shell>
      <date>Current date</date>
      <time>Current time</time>
      <timezone>User's timezone</timezone>
      <working_directory>Current working directory</working_directory>
    </system_info>
    
    <!-- User message -->
    <message>User's input text</message>
    
    <!-- Optional context from previous commands -->
    <execution_context>
      <command>Previously executed command</command>
      <output>Command output (truncated if very long)</output>
      <exit_code>Command exit code</exit_code>
      <execution_time>Time taken to execute the command</execution_time>
    </execution_context>
    
    <!-- Optional plan information -->
    <plan>Current plan XML</plan>
    
    <!-- Optional repository information -->
    <repository>
      <files>List of files in repository</files>
      <branches>List of git branches</branches>
      <current_branch>Current git branch</current_branch>
      <status>Git status output</status>
    </repository>
    
    <!-- Optional memory content -->
    <memory>Persistent memory content</memory>
    
    <!-- Optional conversation history -->
    <history>
      <message role="user">Previous user message</message>
      <message role="assistant">Previous assistant response</message>
    </history>
    
    <!-- Optional error information -->
    <error_context>
      <error_type>Type of error that occurred</error_type>
      <error_message>Error message</error_message>
      <traceback>Stack trace if available</traceback>
    </error_context>
  </input>
</xml_schema>
"""

RESPONSE_SCHEMA = """<response>
  <!-- Optional message to the user -->
  <message>Your response text here. Can include markdown formatting.</message>
  
  <!-- Optional actions to execute -->
  <actions>
    <!-- Create a new file -->
    <action type="create_file" path="example.py">
      # Python code here
    </action>
    
    <!-- Modify an existing file -->
    <action type="modify_file" path="existing.py">
      <change>
        <original>def old_function():</original>
        <new>def new_function():</new>
      </change>
    </action>
    
    <!-- Run a shell command -->
    <action type="run_command" command="echo 'Hello World'">
    </action>
  </actions>
  
  <!-- Optional file edits (search and replace) -->
  <file_edits>
    <edit path="path/to/file.py">
      <search>def old_function():</search>
      <replace>def new_function():</replace>
    </edit>
    <edit path="path/to/new_file.py">
      <search></search>
      <replace># New file content here</replace>
    </edit>
  </file_edits>
  
  <!-- Optional shell commands -->
  <shell_commands>
    <command safe_to_autorun="true">echo "Hello World"</command>
    <command safe_to_autorun="false">rm -rf some_directory</command>
  </shell_commands>
  
  <!-- Optional memory updates -->
  <memory_updates>
    <edit>
      <search>Old information to replace</search>
      <replace>Updated information</replace>
    </edit>
    <append>New information to remember</append>
  </memory_updates>
  
  <!-- Optional plan updates -->
  <plan_updates>
    <task id="task1" status="completed">Task description</task>
    <task id="task2" status="in_progress">Task description</task>
    <new_task id="task3" depends_on="task1,task2">New task description</new_task>
  </plan_updates>
  
  <!-- Optional execution status -->
  <execution_status complete="true|false" needs_user_input="true|false">
    <message>Status message explaining what's done or what's needed</message>
    <progress percent="50">Optional progress information</progress>
  </execution_status>
  
  <!-- Optional error reporting -->
  <error>
    <type>Error type (e.g., API_ERROR, EXECUTION_ERROR)</type>
    <message>Error message</message>
    <suggestion>Suggested action to resolve the error</suggestion>
  </error>
</response>"""

def get_input_schema() -> str:
    """
    Get the XML schema for input messages.
    
    Returns:
        XML schema string
    """
    return INPUT_SCHEMA

def get_response_schema() -> str:
    """
    Get the XML schema for response messages.
    
    Returns:
        XML schema string
    """
    return RESPONSE_SCHEMA

def get_schema() -> str:
    """
    Get the XML schema for response messages.
    
    Returns:
        XML schema string
    """
    return RESPONSE_SCHEMA  # Kept for backward compatibility

def format_input_message(
    message: str,
    system_info: Dict[str, str],
    execution_context: Optional[Dict[str, Any]] = None,
    plan: Optional[str] = None,
    repository_info: Optional[Dict[str, Any]] = None,
    memory: Optional[str] = None,
    history: Optional[str] = None,
    error_context: Optional[Dict[str, str]] = None
) -> str:
    """
    Format an input message according to the XML schema.
    
    Args:
        message: User message
        system_info: System information dictionary
        execution_context: Optional execution context from previous commands
        plan: Optional plan XML
        repository_info: Optional repository information
        memory: Optional persistent memory content
        history: Optional conversation history
        error_context: Optional error information
        
    Returns:
        Formatted XML input message
    """
    # Start with basic structure
    xml_parts = [
        "<input>",
        "  <system_info>",
    ]
    
    # Add system info
    for key, value in system_info.items():
        xml_parts.append(f"    <{key}>{value}</{key}>")
    
    xml_parts.append("  </system_info>")
    xml_parts.append(f"  <message>{message}</message>")
    
    # Add execution context if provided
    if execution_context:
        xml_parts.append("  <execution_context>")
        xml_parts.append(f"    <command>{execution_context.get('command', '')}</command>")
        xml_parts.append(f"    <output>{execution_context.get('output', '')}</output>")
        xml_parts.append(f"    <exit_code>{execution_context.get('exit_code', 0)}</exit_code>")
        if 'execution_time' in execution_context:
            xml_parts.append(f"    <execution_time>{execution_context['execution_time']}</execution_time>")
        xml_parts.append("  </execution_context>")
    
    # Add plan if provided
    if plan:
        xml_parts.append(f"  <plan>{plan}</plan>")
    
    # Add repository info if provided
    if repository_info:
        xml_parts.append("  <repository>")
        if "files" in repository_info:
            xml_parts.append(f"    <files>{repository_info['files']}</files>")
        if "branches" in repository_info:
            xml_parts.append(f"    <branches>{repository_info['branches']}</branches>")
        if "current_branch" in repository_info:
            xml_parts.append(f"    <current_branch>{repository_info['current_branch']}</current_branch>")
        if "status" in repository_info:
            xml_parts.append(f"    <status>{repository_info['status']}</status>")
        xml_parts.append("  </repository>")
    
    # Add memory if provided
    if memory:
        xml_parts.append(f"  <memory>{memory}</memory>")
    
    # Add history if provided
    if history:
        xml_parts.append("  <history>")
        xml_parts.append(f"    {history}")
        xml_parts.append("  </history>")
    
    # Add error context if provided
    if error_context:
        xml_parts.append("  <error_context>")
        if "error_type" in error_context:
            xml_parts.append(f"    <error_type>{error_context['error_type']}</error_type>")
        if "error_message" in error_context:
            xml_parts.append(f"    <error_message>{error_context['error_message']}</error_message>")
        if "traceback" in error_context:
            xml_parts.append(f"    <traceback>{error_context['traceback']}</traceback>")
        xml_parts.append("  </error_context>")
    
    xml_parts.append("</input>")
    
    return "\n".join(xml_parts)
def escape_xml_content(content: str) -> str:
    """
    Escape special characters in XML content.
    
    Args:
        content: The string to escape
        
    Returns:
        Escaped string safe for XML inclusion
    """
    if not content:
        return ""
        
    # Replace special characters with their XML entities
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&apos;'
    }
    
    for char, entity in replacements.items():
        content = content.replace(char, entity)
        
    return content

def format_response_message(
    message: Optional[str] = None,
    actions: Optional[List[Dict[str, Any]]] = None,
    file_edits: Optional[List[Dict[str, Any]]] = None,
    shell_commands: Optional[List[Dict[str, str]]] = None,
    memory_updates: Optional[Dict[str, Any]] = None,
    plan_updates: Optional[List[Dict[str, Any]]] = None,
    execution_status: Optional[Dict[str, Any]] = None,
    error: Optional[Dict[str, str]] = None
) -> str:
    """
    Format a response message according to the XML schema.
    
    Args:
        message: Optional message to the user
        actions: Optional list of actions to execute
        file_edits: Optional list of file edits
        shell_commands: Optional list of shell commands
        memory_updates: Optional memory updates
        plan_updates: Optional plan updates
        execution_status: Optional execution status
        error: Optional error information
        
    Returns:
        Formatted XML response message
    """
    xml_parts = ["<response>"]
    
    # Add message if provided
    if message:
        xml_parts.append(f"  <message>{escape_xml_content(message)}</message>")
    
    # Add actions if provided
    if actions and len(actions) > 0:
        xml_parts.append("  <actions>")
        for action in actions:
            action_type = action.get('type', '')
            if action_type == 'create_file':
                xml_parts.append(f"    <action type=\"create_file\" path=\"{action.get('path', '')}\">")
                xml_parts.append(f"      {escape_xml_content(action.get('content', ''))}")
                xml_parts.append("    </action>")
            elif action_type == 'modify_file':
                xml_parts.append(f"    <action type=\"modify_file\" path=\"{action.get('path', '')}\">")
                for change in action.get('changes', []):
                    xml_parts.append("      <change>")
                    xml_parts.append(f"        <original>{escape_xml_content(change.get('original', ''))}</original>")
                    xml_parts.append(f"        <new>{escape_xml_content(change.get('new', ''))}</new>")
                    xml_parts.append("      </change>")
                xml_parts.append("    </action>")
            elif action_type == 'run_command':
                xml_parts.append(f"    <action type=\"run_command\" command=\"{escape_xml_content(action.get('command', ''))}\">")
                xml_parts.append("    </action>")
        xml_parts.append("  </actions>")
    
    # Add file edits if provided
    if file_edits and len(file_edits) > 0:
        xml_parts.append("  <file_edits>")
        for edit in file_edits:
            xml_parts.append(f"    <edit path=\"{edit.get('path', '')}\">")
            xml_parts.append(f"      <search>{escape_xml_content(edit.get('search', ''))}</search>")
            xml_parts.append(f"      <replace>{escape_xml_content(edit.get('replace', ''))}</replace>")
            xml_parts.append("    </edit>")
        xml_parts.append("  </file_edits>")
    
    # Add shell commands if provided
    if shell_commands and len(shell_commands) > 0:
        xml_parts.append("  <shell_commands>")
        for cmd in shell_commands:
            safe = cmd.get('safe_to_autorun', False)
            xml_parts.append(f"    <command safe_to_autorun=\"{str(safe).lower()}\">{escape_xml_content(cmd.get('command', ''))}</command>")
        xml_parts.append("  </shell_commands>")
    
    # Add memory updates if provided
    if memory_updates:
        xml_parts.append("  <memory_updates>")
        if 'edits' in memory_updates:
            for edit in memory_updates['edits']:
                xml_parts.append("    <edit>")
                xml_parts.append(f"      <search>{escape_xml_content(edit.get('search', ''))}</search>")
                xml_parts.append(f"      <replace>{escape_xml_content(edit.get('replace', ''))}</replace>")
                xml_parts.append("    </edit>")
        if 'append' in memory_updates:
            xml_parts.append(f"    <append>{escape_xml_content(memory_updates['append'])}</append>")
        xml_parts.append("  </memory_updates>")
    
    # Add plan updates if provided
    if plan_updates and len(plan_updates) > 0:
        xml_parts.append("  <plan_updates>")
        for task in plan_updates:
            if 'id' in task and 'status' in task:
                xml_parts.append(f"    <task id=\"{task['id']}\" status=\"{task['status']}\">{escape_xml_content(task.get('description', ''))}</task>")
            elif 'id' in task and task.get('is_new', False):
                depends = task.get('depends_on', '')
                xml_parts.append(f"    <new_task id=\"{task['id']}\" depends_on=\"{depends}\">{escape_xml_content(task.get('description', ''))}</new_task>")
        xml_parts.append("  </plan_updates>")
    
    # Add execution status if provided
    if execution_status:
        complete = execution_status.get('complete', False)
        needs_input = execution_status.get('needs_user_input', False)
        xml_parts.append(f"  <execution_status complete=\"{str(complete).lower()}\" needs_user_input=\"{str(needs_input).lower()}\">")
        if 'message' in execution_status:
            xml_parts.append(f"    <message>{escape_xml_content(execution_status['message'])}</message>")
        if 'progress' in execution_status:
            percent = execution_status.get('progress', {}).get('percent', 0)
            progress_text = escape_xml_content(execution_status.get('progress', {}).get('text', ''))
            xml_parts.append(f"    <progress percent=\"{percent}\">{progress_text}</progress>")
        xml_parts.append("  </execution_status>")
    
    # Add error if provided
    if error:
        xml_parts.append("  <error>")
        if 'type' in error:
            xml_parts.append(f"    <type>{escape_xml_content(error['type'])}</type>")
        if 'message' in error:
            xml_parts.append(f"    <message>{escape_xml_content(error['message'])}</message>")
        if 'suggestion' in error:
            xml_parts.append(f"    <suggestion>{escape_xml_content(error['suggestion'])}</suggestion>")
        xml_parts.append("  </error>")
    
    xml_parts.append("</response>")
    
    return "\n".join(xml_parts)
