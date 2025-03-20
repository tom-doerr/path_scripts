"""Tests for XML schema functionality."""

from src.utils.xml_schema import get_schema  # pylint: disable=no-name-in-module
from src.utils.xml_tools import validate_xml  # pylint: disable=no-name-in-module


def test_schema_is_valid_xml():
    """Test that the schema itself is valid XML."""
    schema = get_schema()
    assert validate_xml(schema), "Schema should be valid XML"


def test_schema_contains_required_elements():
    """Test that the schema contains required elements."""
    schema = get_schema()
    assert "<response>" in schema, "Schema should contain response element"
    assert "<actions>" in schema, "Schema should contain actions element"
    assert "<file_edits>" in schema, "Schema should contain file_edits element"
    assert "<shell_commands>" in schema, "Schema should contain shell_commands element"
    assert "<memory_updates>" in schema, "Schema should contain memory_updates element"
    assert "<execution_status>" in schema, "Schema should contain execution_status element"

def test_schema_example_structures():
    """Test that example structures in schema are valid"""
    schema = get_schema()
    assert "type=\"create_file\"" in schema, "Should contain file creation example"
    assert "type=\"modify_file\"" in schema, "Should contain file modification example"
    assert "type=\"run_command\"" in schema, "Should contain command execution example"


def test_get_schema_returns_string():
    """Test that get_schema returns a non-empty string."""
    schema = get_schema()
    assert isinstance(schema, str), "Schema should be a string"
    assert len(schema) > 100, "Schema should be a meaningful length string"
