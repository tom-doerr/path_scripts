"""XML schema definitions for agent responses."""

RESPONSE_SCHEMA = """
<xml_schema>
  <!-- Response schema - all responses must follow this structure -->
  <response>
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
    
    <!-- Optional execution status -->
    <execution_status complete="true|false" needs_user_input="true|false">
      <message>Status message explaining what's done or what's needed</message>
    </execution_status>
  </response>
</xml_schema>
"""

def get_schema():
    """Return the XML schema for agent responses."""
    return RESPONSE_SCHEMA
