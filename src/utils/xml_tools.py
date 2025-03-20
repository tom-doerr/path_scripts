"""XML parsing and formatting utilities."""
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List

def extract_xml_from_response(response: str, tag_name: str) -> Optional[str]:
    """Extract XML content for a specific tag from a response string."""
    try:
        start_tag = f"<{tag_name}"
        end_tag = f"</{tag_name}>"
        
        start_index = response.find(start_tag)
        if start_index == -1:
            return None
            
        end_index = response.find(end_tag, start_index)
        if end_index == -1:
            return None
            
        return response[start_index:end_index+len(end_tag)]
    except Exception as e:
        return None

def validate_xml(xml_str: str) -> bool:
    """Basic XML validation."""
    try:
        ET.fromstring(xml_str)
        return True
    except ET.ParseError:
        return False

def escape_xml_content(content: str) -> str:
    """Escape special XML characters."""
    return content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')

def format_xml_response(content_dict: Dict[str, Any]) -> str:
    """
    Format various content pieces into an XML response.
    
    Args:
        content_dict: Dictionary of content to format
        
    Returns:
        Formatted XML string
    """
    root = ET.Element("agent-response")
    
    for key, value in content_dict.items():
        if value is None:
            continue
            
        if isinstance(value, str) and value.strip().startswith("<") and value.strip().endswith(">"):
            # This is already XML content, parse it and add as a subtree
            try:
                # Parse the XML string
                element = ET.fromstring(value)
                root.append(element)
            except ET.ParseError:
                # If parsing fails, add as text
                child = ET.SubElement(root, key)
                child.text = value
        else:
            # Add as regular element
            child = ET.SubElement(root, key)
            if isinstance(value, dict):
                child.text = json.dumps(value)
            else:
                child.text = str(value)
    
    # Convert to string with pretty formatting
    xml_str = ET.tostring(root, encoding='unicode')
    
    # Use a custom function to format XML more cleanly
    return pretty_format_xml(xml_str)

def pretty_format_xml(xml_string: str) -> str:
    """
    Format XML string in a cleaner way than minidom.
    
    Args:
        xml_string: Raw XML string
        
    Returns:
        Formatted XML string with proper indentation
    """
    try:
        # Parse the XML
        root = ET.fromstring(xml_string)
        
        # Function to recursively format XML
        def format_elem(elem, level=0):
            indent = "  " * level
            result = []
            
            # Add opening tag with attributes
            attrs = " ".join([f'{k}="{v}"' for k, v in elem.attrib.items()])
            tag_open = f"{indent}<{elem.tag}{' ' + attrs if attrs else ''}>"
            
            # Check if element has children or text
            children = list(elem)
            if children or (elem.text and elem.text.strip()):
                result.append(tag_open)
                
                # Add text if present
                if elem.text and elem.text.strip():
                    text_lines = elem.text.strip().split('\n')
                    if len(text_lines) > 1:
                        # Multi-line text
                        result.append("")
                        for line in text_lines:
                            result.append(f"{indent}  {line}")
                        result.append("")
                    else:
                        # Single line text
                        result.append(f"{indent}  {elem.text.strip()}")
                
                # Add children
                for child in children:
                    result.extend(format_elem(child, level + 1))
                
                # Add closing tag
                result.append(f"{indent}</{elem.tag}>")
            else:
                # Empty element
                result.append(f"{tag_open}</{elem.tag}>")
            
            return result
        
        # Format the XML
        formatted = format_elem(root)
        return "\n".join(formatted)
        
    except ET.ParseError:
        # Fallback to minidom if our custom formatter fails
        try:
            pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ")
            lines = [line for line in pretty_xml.split('\n') if line.strip()]
            return '\n'.join(lines)
        except:
            # If all else fails, return the original string
            return xml_string


if __name__ == "__main__":
    # Simple test when run directly
    test_xml = """<root><child attr="value">Text</child><empty/></root>"""
    print(pretty_format_xml(test_xml))
