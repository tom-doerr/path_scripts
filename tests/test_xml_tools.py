"""Tests for XML tools functionality."""

from src.utils.xml_tools import (
    extract_xml_from_response,
    pretty_format_xml,
    validate_xml,
)

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


def test_extract_xml_nested_tag():
    """Test extraction of nested XML tags."""
    nested_xml = (
        """Before<outer><response><message>Nested</message></response></outer>After"""
    )
    result = extract_xml_from_response(nested_xml, "response")
    assert "<message>Nested</message>" in result


def test_extract_xml_multiple_matches():
    """Test extraction returns first match when multiple exist."""
    multi_xml = "<response>First</response><response>Second</response>"
    result = extract_xml_from_response(multi_xml, "response")
    assert "First" in result and "Second" not in result


def test_pretty_format_xml():
    """Test XML formatting produces indented output."""
    compressed_xml = (
        "<response><message>Test</message><data><item>1</item></data></response>"
    )
    formatted = pretty_format_xml(compressed_xml)
    # Check indentation
    assert formatted == (
        "<response>\n"
        "  <message>\n"
        "    Test\n"
        "  </message>\n"
        "  <data>\n"
        "    <item>\n"
        "      1\n"
        "    </item>\n"
        "  </data>\n"
        "</response>"
    )


def test_extract_xml_with_whitespace():
    """Test XML extraction with surrounding whitespace."""
    wrapped_xml = "\n\n   <response>\n     <data>Content</data>\n   </response>\n\n"
    result = extract_xml_from_response(wrapped_xml, "response")
    assert result.strip() == "<response>\n     <data>Content</data>\n   </response>"


def test_validate_good_xml():
    """Test validation of properly formatted XML."""
    valid_xml = "<root><element>text</element></root>"
    assert validate_xml(valid_xml) is True


def test_validate_bad_xml():
    """Test validation detects malformed XML."""
    invalid_xml = "<root><element>text</root>"
    assert validate_xml(invalid_xml) is False
