#!/usr/bin/env python3
"""Shell command execution utilities."""

import subprocess
from typing import Tuple, Dict, Any

def execute_command(command: str, cwd: str = None) -> Tuple[bool, Dict[str, Any]]:
    """
    Execute a shell command and return the result.
    
    Args:
        command: The command to execute
        cwd: Working directory for the command
        
    Returns:
        Tuple of (success, result_dict)
    """
    result = {
        "command": command,
        "returncode": None,
        "stdout": "",
        "stderr": "",
        "success": False
    }
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd
        )
        
        # Collect output while streaming
        output_lines = []
        
        # Stream output in real-time
        for line in process.stdout:
            output_lines.append(line.rstrip())
        
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
            
        result["stdout"] = truncated_output
        result["stderr"] = stderr
        result["returncode"] = process.returncode
        result["success"] = (process.returncode == 0)
        
        return result["success"], result
            
    except Exception as e:
        result["stderr"] = str(e)
        return False, result

def is_command_safe(command: str) -> bool:
    """
    Check if a command is safe to run automatically.
    
    Args:
        command: The command to check
        
    Returns:
        True if the command is considered safe, False otherwise
    """
    # List of dangerous commands or patterns
    dangerous_patterns = [
        "rm -rf", "rm -r", "rmdir", 
        "dd", "> /dev/", "mkfs", 
        "fdisk", "format", "chmod -R", 
        "chown -R", ":(){:|:&};:",  # Fork bomb
        "wget", "curl", "> /etc/",
        "> ~/.ssh/", "sudo", "su",
        "shutdown", "reboot", "halt",
        "mv /* ", "find / -delete"
    ]
    
    # Check for dangerous patterns
    for pattern in dangerous_patterns:
        if pattern in command:
            return False
    
    # List of safe commands
    safe_commands = [
        "ls", "dir", "echo", "cat", "head", "tail",
        "pwd", "cd", "mkdir", "touch",
        "grep", "find", "wc", "sort", "uniq",
        "git status", "git log", "git branch", "git diff",
        "python", "python3", "pip", "pip3",
        "pytest", "npm test", "npm run",
        "ps", "top", "htop", "df", "du"
    ]
    
    # Check if command starts with a safe command
    for safe in safe_commands:
        if command.startswith(safe):
            return True
    
    # By default, consider commands unsafe
    return False


if __name__ == "__main__":
    # Simple test when run directly
    test_commands = [
        "echo 'Hello, world!'",
        "ls -la",
        "rm -rf /",  # Should be unsafe
        "sudo apt-get update",  # Should be unsafe
        "git status"
    ]
    
    print("Safety check:")
    for cmd in test_commands:
        print(f"{cmd}: {'Safe' if is_command_safe(cmd) else 'Unsafe'}")
    
    print("\nExecution test (safe commands only):")
    for cmd in test_commands:
        if is_command_safe(cmd):
            success, result = execute_command(cmd)
            print(f"{cmd}: {'Success' if success else 'Failed'}")
            print(f"  stdout: {result['stdout'][:50]}...")
            if result['stderr']:
                print(f"  stderr: {result['stderr']}")
