"""Tests for XML schema functionality."""

import xml.etree.ElementTree as ET
from src.utils.xml_schema import get_schema  # pylint: disable=no-name-in-module
from src.utils.xml_tools import validate_xml  # pylint: disable=no-name-in-module


def test_schema_is_valid_xml():
    """Test that the schema itself is valid XML."""
    schema = get_schema()
    assert validate_xml(schema), "Schema should be valid XML"


def test_schema_contains_required_elements():
    """Test that the schema contains required elements."""
    schema = get_schema()
    required_elements = {
        "response",
        "actions",
        "file_edits",
        "shell_commands",
        "memory_updates",
        "execution_status",
    }

    for element in required_elements:
        assert f"<{element}" in schema, f"Schema should contain {element} element"
        assert f"</{element}>" in schema, f"Schema should close {element} element"


def test_schema_example_structures():
    """Test that example structures in schema are valid"""
    schema = get_schema()
    assert 'type="create_file"' in schema, "Should contain file creation example"
    assert 'type="modify_file"' in schema, "Should contain file modification example"
    assert 'type="run_command"' in schema, "Should contain command execution example"


def test_get_schema_returns_string():
    """Test that get_schema returns a non-empty string."""
    schema = get_schema()
    assert isinstance(schema, str), "Schema should be a string"
    assert len(schema) > 100, "Schema should be a meaningful length string"


def test_execution_status_structure():
    """Test execution_status element has required attributes"""
    schema = get_schema()
    root = ET.fromstring(schema)
    status_elem = root.find(".//execution_status")

    assert status_elem is not None, "execution_status element missing"
    assert "complete" in status_elem.attrib, "Missing complete attribute"
    assert (
        "needs_user_input" in status_elem.attrib
    ), "Missing needs_user_input attribute"

def test_schema_root_element():
    """Test schema contains root xml_schema element"""
    schema = get_schema()
    root = ET.fromstring(schema)
    assert root.tag == "xml_schema", "Schema should have xml_schema root element"
