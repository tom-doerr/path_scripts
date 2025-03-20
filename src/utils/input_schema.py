"""
XML schema definitions for input messages to the model.
"""
from typing import Dict, Any, Optional

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
    </system_info>
    
    <!-- User message -->
    <message>User's input text</message>
    
    <!-- Optional context from previous commands -->
    <execution_context>
      <command>Previously executed command</command>
      <output>Command output (truncated if very long)</output>
      <exit_code>Command exit code</exit_code>
    </execution_context>
    
    <!-- Optional plan information -->
    <plan>Current plan XML</plan>
    
    <!-- Optional repository information -->
    <repository>
      <files>List of files in repository</files>
      <branches>List of git branches</branches>
      <current_branch>Current git branch</current_branch>
    </repository>
    
    <!-- Optional memory content -->
    <memory>Persistent memory content</memory>
    
    <!-- Optional conversation history -->
    <history>
      <message role="user">Previous user message</message>
      <message role="assistant">Previous assistant response</message>
    </history>
  </input>
</xml_schema>
"""

def get_input_schema() -> str:
    """
    Get the XML schema for input messages.
    
    Returns:
        XML schema string
    """
    return INPUT_SCHEMA

def format_input_message(
    message: str,
    system_info: Dict[str, str],
    execution_context: Optional[Dict[str, Any]] = None,
    plan: Optional[str] = None,
    repository_info: Optional[Dict[str, Any]] = None,
    memory: Optional[str] = None,
    history: Optional[str] = None
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
        xml_parts.append("  </repository>")
    
    # Add memory if provided
    if memory:
        xml_parts.append(f"  <memory>{memory}</memory>")
    
    # Add history if provided
    if history:
        xml_parts.append("  <history>")
        xml_parts.append(f"    {history}")
        xml_parts.append("  </history>")
    
    xml_parts.append("</input>")
    
    return "\n".join(xml_parts)
