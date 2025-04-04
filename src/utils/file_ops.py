#!/usr/bin/env python3
"""File operation utilities."""

import os
from typing import Tuple


def read_file(path: str) -> Tuple[bool, str]:
    """
    Read a file and return its contents.

    Args:
        path: Path to the file

    Returns:
        Tuple of (success, content_or_error_message)
    """
    try:
        if not os.path.exists(path):
            return False, f"File not found: {path}"
        if not os.path.isfile(path):
            return False, f"Path is not a file: {path}"

        with open(path, "r", encoding='utf-8') as f:
            file_content = f.read()
        return True, file_content
    except FileNotFoundError:
        return False, f"File not found: {path}"
    except PermissionError:
        return False, f"Permission denied: {path}"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"


def write_file(
    path: str, file_content: str, create_dirs: bool = True
) -> Tuple[bool, str]:
    """
    Write content to a file.

    Args:
        path: Path to the file
        content: Content to write
        create_dirs: Whether to create parent directories if they don't exist

    Returns:
        Tuple of (success, message)
    """
    try:
        if os.path.exists(path) and not os.path.isfile(path):
            return False, f"Path exists but is not a file: {path}"

        # Create parent directories if needed
        if create_dirs:
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

        with open(path, "w", encoding='utf-8') as f:
            f.write(file_content)

        # Make executable if it's a Python file or has no extension
        if path.endswith(".py") or not os.path.splitext(path)[1]:
            os.chmod(path, 0o755)
            return True, f"File written and made executable: {path}"

        return True, f"File written: {path}"
    except PermissionError:
        return False, f"Permission denied: {path}"
    except Exception as e:
        return False, f"Error writing file: {str(e)}"


def edit_file(path: str, search_text: str, replace_text: str) -> Tuple[bool, str]:
    """
    Edit a file by replacing text.

    Args:
        path: Path to the file
        search: Text to search for
        replace: Text to replace with

    Returns:
        Tuple of (success, message)
    """
    try:
        if not os.path.exists(path):
            return False, f"File not found: {path}"
        if not os.path.isfile(path):
            return False, f"Path is not a file: {path}"

        with open(path, "r", encoding='utf-8') as f:
            existing_content = f.read()

        if search_text not in existing_content:
            return False, f"Search text not found in {path}"

        new_content = existing_content.replace(search_text, replace_text, 1)

        with open(path, "w", encoding='utf-8') as f:
            f.write(new_content)

        return True, f"File edited: {path}"
    except PermissionError:
        return False, f"Permission denied: {path}"
    except Exception as e:
        return False, f"Error editing file: {str(e)}"


def append_to_file(path: str, text_to_append: str) -> Tuple[bool, str]:
    """
    Append content to a file.

    Args:
        path: Path to the file
        content: Content to append

    Returns:
        Tuple of (success, message)
    """
    try:
        if not os.path.exists(path):
            return False, f"File not found: {path}"
        if not os.path.isfile(path):
            return False, f"Path is not a file: {path}"

        with open(path, "a", encoding='utf-8') as f:
            f.write(text_to_append)

        return True, f"Content appended to: {path}"
    except PermissionError:
        return False, f"Permission denied: {path}"
    except Exception as e:
        return False, f"Error appending to file: {str(e)}"


if __name__ == "__main__":
    # Simple test when run directly
    import tempfile

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp:
        temp_path = temp.name

    # Test write
    success, msg = write_file(temp_path, "Hello, world!")
    print(f"Write: {success} - {msg}")

    # Test read
    success, content = read_file(temp_path)
    print(f"Read: {success} - {content}")

    # Test edit
    success, msg = edit_file(temp_path, "Hello", "Goodbye")
    print(f"Edit: {success} - {msg}")

    # Test append
    success, msg = append_to_file(temp_path, "\nAppended text")
    print(f"Append: {success} - {msg}")

    # Read final content
    success, content = read_file(temp_path)
    print(f"Final content: {content}")

    # Clean up
    os.unlink(temp_path)
