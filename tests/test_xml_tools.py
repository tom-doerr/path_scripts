"""Tests for XML tools functionality."""
from src.xml_tools import extract_xml_from_response, pretty_format_xml

SAMPLE_XML = """<response>
    <message>Test content</message>
    <data>123</data>
</response>"""

def test_extract_xml_simple():
    """Test basic XML extraction."""
    wrapped_xml = f"Some text before {SAMPLE_XML} some text after"
    result = extract_xml_from_response(wrapped_xml, "response")
    assert result.strip() == SAMPLE_XML.strip()

def test_extract_xml_no_match():
    """Test XML extraction when no match exists."""
    result = extract_xml_from_response("No XML here", "response")
    assert result is None

def test_pretty_format_xml():
    """Test XML formatting produces indented output."""
    compressed_xml = "<response><message>Test</message></response>"
    formatted = pretty_format_xml(compressed_xml)
    assert "    <message>" in formatted
    assert "\n" in formatted
