"""
Selector Parser Module

This module provides functionality to parse string selectors into structured JSON format
for Playwright actions. It supports various selector types including XPath, CSS selectors,
attribute selectors, and text-based selectors.
"""

import re
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from enum import Enum


class SelectorType(Enum):
    """Enumeration of supported selector types."""
    XPATH = "xpathSelector"
    ATTRIBUTE_VALUE = "attributeValueSelector"
    TAG_CONTAINS = "tagContainsSelector"
    CSS = "cssSelector"
    TEXT = "textSelector"


@dataclass
class ParsedSelector:
    """Represents a parsed selector with its type and data."""
    type: SelectorType
    data: Dict[str, Any]
    original_string: str


class SelectorParser:
    """Parser for converting string selectors to structured JSON format."""
    
    def __init__(self):
        """Initialize the selector parser with regex patterns."""
        # XPath patterns
        self.xpath_patterns = [
            r'^//',  # XPath starting with //
            r'^/html',  # XPath starting with /html
            r'^\.\./',  # XPath with parent navigation
            r'^ancestor::',  # XPath ancestor
            r'^descendant::',  # XPath descendant
            r'^following::',  # XPath following
            r'^preceding::',  # XPath preceding
            r'^parent::',  # XPath parent
            r'^child::',  # XPath child
            r'^self::',  # XPath self
            r'^attribute::',  # XPath attribute
            r'^namespace::',  # XPath namespace
        ]
        
        # CSS selector patterns
        self.css_patterns = [
            r'^[a-zA-Z][a-zA-Z0-9_-]*$',  # Simple tag name
            r'^#[a-zA-Z][a-zA-Z0-9_-]*$',  # ID selector
            r'^\.[a-zA-Z][a-zA-Z0-9_-]*$',  # Class selector
            r'^[a-zA-Z][a-zA-Z0-9_-]*\[',  # Attribute selector
            r'^[a-zA-Z][a-zA-Z0-9_-]*:',  # Pseudo selector
            r'^[a-zA-Z][a-zA-Z0-9_-]*\s',  # Descendant selector
            r'^[a-zA-Z][a-zA-Z0-9_-]*>',  # Child selector
            r'^[a-zA-Z][a-zA-Z0-9_-]*\+',  # Adjacent sibling
            r'^[a-zA-Z][a-zA-Z0-9_-]*~',  # General sibling
        ]
        
        # Attribute selector patterns
        self.attribute_patterns = {
            'id': r'^#([a-zA-Z][a-zA-Z0-9_-]*)$',
            'class': r'^\.([a-zA-Z][a-zA-Z0-9_-]*)$',
            'name': r'^\[name="([^"]+)"\]$',
            'type': r'^\[type="([^"]+)"\]$',
            'value': r'^\[value="([^"]+)"\]$',
            'placeholder': r'^\[placeholder="([^"]+)"\]$',
            'title': r'^\[title="([^"]+)"\]$',
            'alt': r'^\[alt="([^"]+)"\]$',
            'src': r'^\[src="([^"]+)"\]$',
            'href': r'^\[href="([^"]+)"\]$',
        }
        
        # Text selector patterns
        self.text_patterns = [
            r'^text=',
            r'^text:',
            r'^contains\(text\(\)',
            r'^normalize-space\(text\(\)',
        ]
    
    def parse(self, selector_string: str) -> ParsedSelector:
        """
        Parse a string selector into structured JSON format.
        
        Args:
            selector_string: The selector string to parse
            
        Returns:
            ParsedSelector object with type and structured data
            
        Raises:
            ValueError: If the selector string cannot be parsed
        """
        if not selector_string or not isinstance(selector_string, str):
            raise ValueError("Selector string must be a non-empty string")
        
        selector_string = selector_string.strip()
        
        # Try to parse as XPath
        if self._is_xpath(selector_string):
            return self._parse_xpath(selector_string)
        
        # Try to parse as attribute selector
        attribute_selector = self._parse_attribute_selector(selector_string)
        if attribute_selector:
            return attribute_selector
        
        # Try to parse as text selector
        text_selector = self._parse_text_selector(selector_string)
        if text_selector:
            return text_selector
        
        # Try to parse as CSS selector
        if self._is_css_selector(selector_string):
            return self._parse_css_selector(selector_string)
        
        # Default to tag contains selector
        return self._parse_tag_contains(selector_string)
    
    def _is_xpath(self, selector: str) -> bool:
        """Check if selector is an XPath expression."""
        return any(re.match(pattern, selector) for pattern in self.xpath_patterns)
    
    def _is_css_selector(self, selector: str) -> bool:
        """Check if selector is a CSS selector."""
        return any(re.match(pattern, selector) for pattern in self.css_patterns)
    
    def _parse_xpath(self, selector: str) -> ParsedSelector:
        """Parse XPath selector."""
        return ParsedSelector(
            type=SelectorType.XPATH,
            data={
                "type": "xpathSelector",
                "value": selector
            },
            original_string=selector
        )
    
    def _parse_attribute_selector(self, selector: str) -> Optional[ParsedSelector]:
        """Parse attribute-based selector."""
        for attribute, pattern in self.attribute_patterns.items():
            match = re.match(pattern, selector)
            if match:
                value = match.group(1)
                
                if attribute == 'id':
                    return ParsedSelector(
                        type=SelectorType.ATTRIBUTE_VALUE,
                        data={
                            "type": "attributeValueSelector",
                            "attribute": "id",
                            "value": f"#{value}"
                        },
                        original_string=selector
                    )
                elif attribute == 'class':
                    return ParsedSelector(
                        type=SelectorType.ATTRIBUTE_VALUE,
                        data={
                            "type": "attributeValueSelector",
                            "attribute": "class",
                            "value": f".{value}"
                        },
                        original_string=selector
                    )
                else:
                    return ParsedSelector(
                        type=SelectorType.ATTRIBUTE_VALUE,
                        data={
                            "type": "attributeValueSelector",
                            "attribute": attribute,
                            "value": value
                        },
                        original_string=selector
                    )
        
        return None
    
    def _parse_text_selector(self, selector: str) -> Optional[ParsedSelector]:
        """Parse text-based selector."""
        for pattern in self.text_patterns:
            if re.match(pattern, selector):
                # Extract text content
                if selector.startswith('text='):
                    text_content = selector[5:]  # Remove 'text=' prefix
                elif selector.startswith('text:'):
                    text_content = selector[5:]  # Remove 'text:' prefix
                elif 'contains(text()' in selector:
                    # Extract text from contains(text(), "text")
                    match = re.search(r'contains\(text\(\),\s*"([^"]+)"', selector)
                    if match:
                        text_content = match.group(1)
                    else:
                        continue
                elif 'normalize-space(text()' in selector:
                    # Extract text from normalize-space(text()) = "text"
                    match = re.search(r'normalize-space\(text\(\)\)\s*=\s*"([^"]+)"', selector)
                    if match:
                        text_content = match.group(1)
                    else:
                        continue
                else:
                    continue
                
                return ParsedSelector(
                    type=SelectorType.TEXT,
                    data={
                        "type": "tagContainsSelector",
                        "value": text_content
                    },
                    original_string=selector
                )
        
        return None
    
    def _parse_css_selector(self, selector: str) -> ParsedSelector:
        """Parse CSS selector."""
        return ParsedSelector(
            type=SelectorType.CSS,
            data={
                "type": "cssSelector",
                "value": selector
            },
            original_string=selector
        )
    
    def _parse_tag_contains(self, selector: str) -> ParsedSelector:
        """Parse as tag contains selector (default fallback)."""
        return ParsedSelector(
            type=SelectorType.TAG_CONTAINS,
            data={
                "type": "tagContainsSelector",
                "value": selector
            },
            original_string=selector
        )
    
    def parse_multiple(self, selectors: List[str]) -> List[ParsedSelector]:
        """
        Parse multiple selector strings.
        
        Args:
            selectors: List of selector strings to parse
            
        Returns:
            List of ParsedSelector objects
        """
        return [self.parse(selector) for selector in selectors]
    
    def to_playwright_selector(self, parsed_selector: ParsedSelector) -> str:
        """
        Convert parsed selector back to Playwright-compatible string.
        
        Args:
            parsed_selector: ParsedSelector object
            
        Returns:
            Playwright-compatible selector string
        """
        selector_type = parsed_selector.type
        data = parsed_selector.data
        
        if selector_type == SelectorType.XPATH:
            return data["value"]
        elif selector_type == SelectorType.ATTRIBUTE_VALUE:
            attribute = data["attribute"]
            value = data["value"]
            
            if attribute == "id":
                return f"#{value[1:]}" if value.startswith("#") else f"#{value}"
            elif attribute == "class":
                return f".{value[1:]}" if value.startswith(".") else f".{value}"
            else:
                return f'[{attribute}="{value}"]'
        elif selector_type == SelectorType.TEXT:
            return f'text={data["value"]}'
        elif selector_type == SelectorType.CSS:
            return data["value"]
        else:  # TAG_CONTAINS
            return data["value"]
    
    def validate_selector(self, selector_string: str) -> bool:
        """
        Validate if a selector string can be parsed.
        
        Args:
            selector_string: The selector string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            self.parse(selector_string)
            return True
        except (ValueError, Exception):
            return False


# Global selector parser instance
_selector_parser: Optional[SelectorParser] = None


def get_selector_parser() -> SelectorParser:
    """Get the global selector parser instance."""
    global _selector_parser
    if _selector_parser is None:
        _selector_parser = SelectorParser()
    return _selector_parser


def parse_selector(selector_string: str) -> ParsedSelector:
    """
    Convenience function to parse a single selector string.
    
    Args:
        selector_string: The selector string to parse
        
    Returns:
        ParsedSelector object
    """
    parser = get_selector_parser()
    return parser.parse(selector_string)


def parse_selectors(selectors: List[str]) -> List[ParsedSelector]:
    """
    Convenience function to parse multiple selector strings.
    
    Args:
        selectors: List of selector strings to parse
        
    Returns:
        List of ParsedSelector objects
    """
    parser = get_selector_parser()
    return parser.parse_multiple(selectors)


def selector_to_json(selector_string: str) -> Dict[str, Any]:
    """
    Convert a selector string to JSON format.
    
    Args:
        selector_string: The selector string to convert
        
    Returns:
        Dictionary representing the selector in JSON format
    """
    parsed = parse_selector(selector_string)
    return parsed.data


def validate_selector_string(selector_string: str) -> bool:
    """
    Validate if a selector string can be parsed.
    
    Args:
        selector_string: The selector string to validate
        
    Returns:
        True if valid, False otherwise
    """
    parser = get_selector_parser()
    return parser.validate_selector(selector_string)


# Example usage and testing
if __name__ == "__main__":
    parser = SelectorParser()
    
    # Test cases
    test_selectors = [
        "//div[@class='container']",  # XPath
        "#submit-button",  # ID selector
        ".form-group",  # Class selector
        "[name='username']",  # Name attribute
        "text=Submit",  # Text selector
        "button",  # Tag selector
        "div.container > input",  # CSS selector
        "//input[@type='text' and @placeholder='Enter name']",  # Complex XPath
        "[data-testid='login-form']",  # Data attribute
        "text:Login",  # Text selector variant
    ]
    
    print("=== Selector Parser Test Results ===")
    for selector in test_selectors:
        try:
            parsed = parser.parse(selector)
            print(f"\nOriginal: {selector}")
            print(f"Type: {parsed.type.value}")
            print(f"JSON: {parsed.data}")
            print(f"Playwright: {parser.to_playwright_selector(parsed)}")
            print(f"Valid: {parser.validate_selector(selector)}")
        except Exception as e:
            print(f"\nError parsing '{selector}': {e}")
    
    # Test multiple selectors
    print(f"\n=== Multiple Selector Parsing ===")
    multiple_parsed = parser.parse_multiple(test_selectors[:5])
    for i, parsed in enumerate(multiple_parsed):
        print(f"{i+1}. {test_selectors[i]} -> {parsed.type.value}")
    
    # Test convenience functions
    print(f"\n=== Convenience Functions ===")
    json_result = selector_to_json("#test-id")
    print(f"selector_to_json('#test-id'): {json_result}")
    
    is_valid = validate_selector_string("//div[@id='test']")
    print(f"validate_selector_string('//div[@id='test']'): {is_valid}")
