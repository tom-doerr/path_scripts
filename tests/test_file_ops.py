"""Tests for file operations."""

import os
import tempfile
from src.utils.file_ops import read_file, write_file, edit_file, append_to_file

def test_read_file_success():
    """Test reading an existing file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        path = f.name
    
    success, content = read_file(path)
    assert success is True
    assert content == "test content"
    os.unlink(path)

def test_read_file_not_found():
    """Test reading a non-existent file."""
    success, content = read_file("/nonexistent/file")
    assert success is False
    assert "not found" in content.lower()

def test_write_file_new():
    """Test writing to a new file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "new.txt")
        success, _ = write_file(path, "new content")
        assert success is True
        assert os.path.exists(path)
        with open(path) as f:
            assert f.read() == "new content"

def test_edit_file_success():
    """Test editing a file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("old content")
        path = f.name
    
    success, _ = edit_file(path, "old", "new")
    assert success is True
    with open(path) as f:
        assert f.read() == "new content"
    os.unlink(path)

def test_append_to_file():
    """Test appending to a file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("original")
        path = f.name
    
    success, _ = append_to_file(path, "\nappended")
    assert success is True
    with open(path) as f:
        assert f.read() == "original\nappended"
    os.unlink(path)
