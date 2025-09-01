"""
Playwright Action JSON Structure Definitions

This module defines the JSON structure for various Playwright actions including
click, drag_and_drop, enter_text_and_click, enter_text_using_selector, 
open_url, and submit_form actions.

Each action follows a consistent structure with action type, parameters, and
selector specifications.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class SelectorType(str, Enum):
    """Enumeration of supported selector types."""
    ATTRIBUTE_VALUE = "attributeValueSelector"
    TAG_CONTAINS = "tagContainsSelector"
    XPATH = "xpathSelector"


@dataclass
class Selector:
    """Base selector class for all selector types."""
    type: SelectorType
    value: str
    attribute: Optional[str] = None


@dataclass
class AttributeValueSelector(Selector):
    """Selector for elements based on specific attributes."""
    type: SelectorType = SelectorType.ATTRIBUTE_VALUE
    attribute: str = "id"  # "id", "class", or "name"
    value: str = ""

    def to_playwright_selector(self) -> str:
        """Convert to Playwright-compatible selector string."""
        if self.attribute == "id":
            return f"#{self.value}"
        elif self.attribute == "class":
            return f".{self.value}"
        elif self.attribute == "name":
            return f"[name='{self.value}']"
        else:
            return f"[{self.attribute}='{self.value}']"


@dataclass
class TagContainsSelector(Selector):
    """Selector for elements based on tag name and content."""
    type: SelectorType = SelectorType.TAG_CONTAINS
    value: str = ""

    def to_playwright_selector(self) -> str:
        """Convert to Playwright-compatible selector string."""
        return f"text={self.value}"


@dataclass
class XPathSelector(Selector):
    """Selector for elements using XPath expressions."""
    type: SelectorType = SelectorType.XPATH
    value: str = ""

    def to_playwright_selector(self) -> str:
        """Convert to Playwright-compatible selector string."""
        return self.value


# Action Definitions
@dataclass
class ClickAction:
    """JSON structure for click action."""
    action: str = "click"
    selector: Dict[str, Any] = None
    wait_before_execution: float = 0.0
    description: str = "Click on an element identified by the selector"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "action": self.action,
            "selector": self.selector,
            "wait_before_execution": self.wait_before_execution,
            "description": self.description
        }


@dataclass
class DragAndDropAction:
    """JSON structure for drag and drop action."""
    action: str = "drag_and_drop"
    source_selector: Dict[str, Any] = None
    target_selector: Dict[str, Any] = None
    wait_before_execution: float = 0.0
    description: str = "Drag an element and drop it onto another element"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "action": self.action,
            "source_selector": self.source_selector,
            "target_selector": self.target_selector,
            "wait_before_execution": self.wait_before_execution,
            "description": self.description
        }


@dataclass
class EnterTextAndClickAction:
    """JSON structure for enter text and click action."""
    action: str = "enter_text_and_click"
    text_selector: Dict[str, Any] = None
    text_to_enter: str = ""
    click_selector: Dict[str, Any] = None
    wait_before_click_execution: float = 0.0
    description: str = "Enter text into an element and then click another element"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "action": self.action,
            "text_selector": self.text_selector,
            "text_to_enter": self.text_to_enter,
            "click_selector": self.click_selector,
            "wait_before_click_execution": self.wait_before_click_execution,
            "description": self.description
        }


@dataclass
class EnterTextAction:
    """JSON structure for enter text action."""
    action: str = "enter_text"
    selector: Dict[str, Any] = None
    text_to_enter: str = ""
    use_keyboard_fill: bool = True
    description: str = "Enter text into an element identified by the selector"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "action": self.action,
            "selector": self.selector,
            "text_to_enter": self.text_to_enter,
            "use_keyboard_fill": self.use_keyboard_fill,
            "description": self.description
        }


@dataclass
class OpenUrlAction:
    """JSON structure for open URL action."""
    action: str = "open_url"
    url: str = ""
    description: str = "Open a specified URL in the web browser"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "action": self.action,
            "url": self.url,
            "description": self.description
        }


@dataclass
class SubmitFormAction:
    """JSON structure for submit form action."""
    action: str = "submit_form"
    selector: Dict[str, Any] = None
    wait_before_execution: float = 0.0
    description: str = "Submit a form element identified by the selector"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "action": self.action,
            "selector": self.selector,
            "wait_before_execution": self.wait_before_execution,
            "description": self.description
        }


# Utility functions for creating selectors
def create_attribute_value_selector(attribute: str, value: str) -> Dict[str, Any]:
    """Create an attribute value selector JSON structure."""
    return {
        "type": SelectorType.ATTRIBUTE_VALUE.value,
        "attribute": attribute,
        "value": value
    }


def create_tag_contains_selector(value: str) -> Dict[str, Any]:
    """Create a tag contains selector JSON structure."""
    return {
        "type": SelectorType.TAG_CONTAINS.value,
        "value": value
    }


def create_xpath_selector(value: str) -> Dict[str, Any]:
    """Create an XPath selector JSON structure."""
    return {
        "type": SelectorType.XPATH.value,
        "value": value
    }


def selector_to_playwright_string(selector_dict: Dict[str, Any]) -> str:
    """Convert a selector JSON structure to a Playwright-compatible string."""
    selector_type = selector_dict.get("type")
    
    if selector_type == SelectorType.ATTRIBUTE_VALUE.value:
        attribute = selector_dict.get("attribute", "id")
        value = selector_dict.get("value", "")
        if attribute == "id":
            return f"#{value}"
        elif attribute == "class":
            return f".{value}"
        elif attribute == "name":
            return f"[name='{value}']"
        else:
            return f"[{attribute}='{value}']"
    
    elif selector_type == SelectorType.TAG_CONTAINS.value:
        value = selector_dict.get("value", "")
        return f"text={value}"
    
    elif selector_type == SelectorType.XPATH.value:
        value = selector_dict.get("value", "")
        return value
    
    else:
        raise ValueError(f"Unknown selector type: {selector_type}")


# Example usage and validation
def validate_selector(selector_dict: Dict[str, Any]) -> bool:
    """Validate a selector JSON structure."""
    required_fields = ["type", "value"]
    
    # Check required fields
    for field in required_fields:
        if field not in selector_dict:
            return False
    
    selector_type = selector_dict.get("type")
    
    # Validate based on type
    if selector_type == SelectorType.ATTRIBUTE_VALUE.value:
        if "attribute" not in selector_dict:
            return False
        attribute = selector_dict.get("attribute")
        if attribute not in ["id", "class", "name"]:
            return False
    
    elif selector_type == SelectorType.TAG_CONTAINS.value:
        # No additional validation needed
        pass
    
    elif selector_type == SelectorType.XPATH.value:
        # Basic XPath validation - should start with / or //
        value = selector_dict.get("value", "")
        if not (value.startswith("/") or value.startswith("//")):
            return False
    
    else:
        return False
    
    return True


# Example JSON structures
EXAMPLE_ACTIONS = {
    "click_example": {
        "action": "click",
        "selector": {
            "type": "attributeValueSelector",
            "attribute": "id",
            "value": "submit-button"
        },
        "wait_before_execution": 1.0,
        "description": "Click the submit button"
    },
    
    "drag_and_drop_example": {
        "action": "drag_and_drop",
        "source_selector": {
            "type": "attributeValueSelector",
            "attribute": "id",
            "value": "draggable-item"
        },
        "target_selector": {
            "type": "attributeValueSelector",
            "attribute": "class",
            "value": "drop-zone"
        },
        "wait_before_execution": 0.5,
        "description": "Drag item to drop zone"
    },
    
    "enter_text_example": {
        "action": "enter_text",
        "selector": {
            "type": "xpathSelector",
            "value": "//input[@name='username']"
        },
        "text_to_enter": "john_doe",
        "use_keyboard_fill": True,
        "description": "Enter username in the username field"
    },
    
    "submit_form_example": {
        "action": "submit_form",
        "selector": {
            "type": "tagContainsSelector",
            "value": "Submit"
        },
        "wait_before_execution": 0.0,
        "description": "Submit the form by clicking the submit button"
    }
}
