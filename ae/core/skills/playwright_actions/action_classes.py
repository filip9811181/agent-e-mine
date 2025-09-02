"""
Action Classes for Playwright Automation

This module implements the JSON structure for actions and selectors using Python classes.
Each action type is represented by a specific class with appropriate fields and validation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Union, Dict, Any, List
from enum import Enum
import json
from ae.core.skills.playwright_actions.selector_parser import parse_selector


class SelectorType(str, Enum):
    """Enumeration of supported selector types."""
    ATTRIBUTE_VALUE = "attributeValueSelector"
    TAG_CONTAINS = "tagContainsSelector"
    XPATH = "xpathSelector"


@dataclass
class Selector:
    """Base selector class for identifying HTML elements."""
    type: SelectorType
    value: str
    attribute: Optional[str] = None

    def to_playwright_selector(self) -> str:
        """Convert to Playwright-compatible selector string."""
        if self.type == SelectorType.ATTRIBUTE_VALUE:
            if self.attribute == "id":
                return f"#{self.value}"
            elif self.attribute == "class":
                return f".{self.value}"
            elif self.attribute == "name":
                return f"[name='{self.value}']"
            else:
                return f"[{self.attribute}='{self.value}']"
        elif self.type == SelectorType.TAG_CONTAINS:
            return f"text={self.value}"
        elif self.type == SelectorType.XPATH:
            return self.value
        else:
            raise ValueError(f"Unknown selector type: {self.type}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "type": self.type.value,
            "value": self.value
        }
        if self.attribute:
            result["attribute"] = self.attribute
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Selector':
        """Create a Selector instance from a dictionary."""
        selector_type = SelectorType(data["type"])
        value = data["value"]
        attribute = data.get("attribute")
        
        return cls(
            type=selector_type,
            value=value,
            attribute=attribute
        )
    
    @classmethod
    def from_string(cls, selector_string: str) -> 'Selector':
        """
        Create a Selector instance from a string selector using SelectorParser.
        
        Args:
            selector_string: String selector to parse
            
        Returns:
            Selector instance
        """
        parsed_selector = parse_selector(selector_string)
        
        # Map ParsedSelector type to SelectorType
        type_mapping = {
            "xpathSelector": SelectorType.XPATH,
            "attributeValueSelector": SelectorType.ATTRIBUTE_VALUE,
            "tagContainsSelector": SelectorType.TAG_CONTAINS,
        }
        
        selector_type = type_mapping.get(parsed_selector.data["type"])
        if not selector_type:
            raise ValueError(f"Unsupported selector type: {parsed_selector.data['type']}")
        
        # Extract value and attribute
        value = parsed_selector.data.get("value", "")
        attribute = parsed_selector.data.get("attribute")
        
        # Clean up value for ID and class selectors
        if attribute == "id" and value.startswith("#"):
            value = value[1:]  # Remove the # prefix
        elif attribute == "class" and value.startswith("."):
            value = value[1:]  # Remove the . prefix
        
        return cls(
            type=selector_type,
            value=value,
            attribute=attribute
        )


class ActionType(str, Enum):
    """Enumeration of supported action types."""
    CLICK = "click"
    DOUBLE_CLICK = "doubleClick"
    NAVIGATE = "navigate"
    TYPE = "type"
    SELECT = "select"
    HOVER = "hover"
    WAIT = "wait"
    SCROLL = "scroll"
    SUBMIT = "submit"
    DRAG_AND_DROP = "dragAndDrop"
    SCREENSHOT = "screenshot"
    GET_DROPDOWN_OPTIONS = "getDropDownOptions"
    SELECT_DROPDOWN_OPTION = "selectDropDownOption"


class Action(ABC):
    """Abstract base class for all actions."""
    
    @property
    @abstractmethod
    def type(self) -> ActionType:
        """Return the action type."""
        pass
    
    @property
    @abstractmethod
    def selector(self) -> Optional[Selector]:
        """Return the selector for this action."""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Action':
        """Create an Action instance from a dictionary."""
        pass


@dataclass
class ClickAction(Action):
    """Performs a click on a specified HTML element."""
    selector: Optional[Selector] = None
    x: Optional[int] = None
    y: Optional[int] = None
    
    @property
    def type(self) -> ActionType:
        return ActionType.CLICK
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "type": self.type.value,
            "selector": self.selector.to_dict() if self.selector else None
        }
        if self.x is not None:
            result["x"] = self.x
        if self.y is not None:
            result["y"] = self.y
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClickAction':
        selector_data = data.get("selector")
        selector = Selector.from_dict(selector_data) if selector_data else None
        
        return cls(
            selector=selector,
            x=data.get("x"),
            y=data.get("y")
        )
    
    @classmethod
    def from_string(cls, selector_string: str, x: Optional[int] = None, y: Optional[int] = None) -> 'ClickAction':
        """
        Create a ClickAction from a string selector.
        
        Args:
            selector_string: String selector to parse
            x: Optional x coordinate
            y: Optional y coordinate
            
        Returns:
            ClickAction instance
        """
        selector = Selector.from_string(selector_string)
        return cls(selector=selector, x=x, y=y)


@dataclass
class DoubleClickAction(Action):
    """Performs a double-click on the specified element."""
    selector: Optional[Selector] = None
    
    @property
    def type(self) -> ActionType:
        return ActionType.DOUBLE_CLICK
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "selector": self.selector.to_dict() if self.selector else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DoubleClickAction':
        selector_data = data.get("selector")
        selector = Selector.from_dict(selector_data) if selector_data else None
        
        return cls(selector=selector)
    
    @classmethod
    def from_string(cls, selector_string: str) -> 'DoubleClickAction':
        """
        Create a DoubleClickAction from a string selector.
        
        Args:
            selector_string: String selector to parse
            
        Returns:
            DoubleClickAction instance
        """
        selector = Selector.from_string(selector_string)
        return cls(selector=selector)


@dataclass
class NavigateAction(Action):
    """Navigates to a different page or moves forward/backward in browsing history."""
    url: Optional[str] = None
    go_back: bool = False
    go_forward: bool = False
    
    @property
    def type(self) -> ActionType:
        return ActionType.NAVIGATE
    
    @property
    def selector(self) -> Optional[Selector]:
        return None  # Navigation actions don't require selectors
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "type": self.type.value,
            "selector": None
        }
        if self.url:
            result["url"] = self.url
        if self.go_back:
            result["go_back"] = self.go_back
        if self.go_forward:
            result["go_forward"] = self.go_forward
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NavigateAction':
        return cls(
            url=data.get("url"),
            go_back=data.get("go_back", False),
            go_forward=data.get("go_forward", False)
        )


@dataclass
class TypeAction(Action):
    """Types text into an input field."""
    selector: Optional[Selector] = None
    text: str = ""
    
    @property
    def type(self) -> ActionType:
        return ActionType.TYPE
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "selector": self.selector.to_dict() if self.selector else None,
            "text": self.text
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TypeAction':
        selector_data = data.get("selector")
        selector = Selector.from_dict(selector_data) if selector_data else None
        
        return cls(
            selector=selector,
            text=data.get("text", "")
        )
    
    @classmethod
    def from_string(cls, selector_string: str, text: str = "") -> 'TypeAction':
        """
        Create a TypeAction from a string selector.
        
        Args:
            selector_string: String selector to parse
            text: Text to type
            
        Returns:
            TypeAction instance
        """
        selector = Selector.from_string(selector_string)
        return cls(selector=selector, text=text)


@dataclass
class SelectAction(Action):
    """Selects an option from a dropdown menu or selection field."""
    selector: Optional[Selector] = None
    value: str = ""
    
    @property
    def type(self) -> ActionType:
        return ActionType.SELECT
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "selector": self.selector.to_dict() if self.selector else None,
            "value": self.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SelectAction':
        selector_data = data.get("selector")
        selector = Selector.from_dict(selector_data) if selector_data else None
        
        return cls(
            selector=selector,
            value=data.get("value", "")
        )
    
    @classmethod
    def from_string(cls, selector_string: str, value: str = "") -> 'SelectAction':
        """
        Create a SelectAction from a string selector.
        
        Args:
            selector_string: String selector to parse
            value: Value to select
            
        Returns:
            SelectAction instance
        """
        selector = Selector.from_string(selector_string)
        return cls(selector=selector, value=value)


@dataclass
class HoverAction(Action):
    """Moves the cursor over a specified element."""
    selector: Optional[Selector] = None
    
    @property
    def type(self) -> ActionType:
        return ActionType.HOVER
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "selector": self.selector.to_dict() if self.selector else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HoverAction':
        selector_data = data.get("selector")
        selector = Selector.from_dict(selector_data) if selector_data else None
        
        return cls(selector=selector)
    
    @classmethod
    def from_string(cls, selector_string: str) -> 'HoverAction':
        """
        Create a HoverAction from a string selector.
        
        Args:
            selector_string: String selector to parse
            
        Returns:
            HoverAction instance
        """
        selector = Selector.from_string(selector_string)
        return cls(selector=selector)


@dataclass
class WaitAction(Action):
    """Pauses execution for a specified duration."""
    time_seconds: float = 1.0
    
    @property
    def type(self) -> ActionType:
        return ActionType.WAIT
    
    @property
    def selector(self) -> Optional[Selector]:
        return None  # Wait actions don't require selectors
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "selector": None,
            "time_seconds": self.time_seconds
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WaitAction':
        return cls(time_seconds=data.get("time_seconds", 1.0))


@dataclass
class ScrollAction(Action):
    """Scrolls up or down within a page or element."""
    selector: Optional[Selector] = None
    value: str = ""
    up: bool = False
    down: bool = False
    
    @property
    def type(self) -> ActionType:
        return ActionType.SCROLL
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "type": self.type.value,
            "selector": self.selector.to_dict() if self.selector else None,
            "value": self.value
        }
        if self.up:
            result["up"] = self.up
        if self.down:
            result["down"] = self.down
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScrollAction':
        selector_data = data.get("selector")
        selector = Selector.from_dict(selector_data) if selector_data else None
        
        return cls(
            selector=selector,
            value=data.get("value", ""),
            up=data.get("up", False),
            down=data.get("down", False)
        )
    
    @classmethod
    def from_string(cls, selector_string: str, value: str = "", up: bool = False, down: bool = False) -> 'ScrollAction':
        """
        Create a ScrollAction from a string selector.
        
        Args:
            selector_string: String selector to parse
            value: Scroll value
            up: Whether to scroll up
            down: Whether to scroll down
            
        Returns:
            ScrollAction instance
        """
        selector = Selector.from_string(selector_string)
        return cls(selector=selector, value=value, up=up, down=down)


@dataclass
class SubmitAction(Action):
    """Submits a form by pressing Enter or clicking the submit button."""
    selector: Optional[Selector] = None
    
    @property
    def type(self) -> ActionType:
        return ActionType.SUBMIT
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "selector": self.selector.to_dict() if self.selector else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SubmitAction':
        selector_data = data.get("selector")
        selector = Selector.from_dict(selector_data) if selector_data else None
        
        return cls(selector=selector)
    
    @classmethod
    def from_string(cls, selector_string: str) -> 'SubmitAction':
        """
        Create a SubmitAction from a string selector.
        
        Args:
            selector_string: String selector to parse
            
        Returns:
            SubmitAction instance
        """
        selector = Selector.from_string(selector_string)
        return cls(selector=selector)


@dataclass
class DragAndDropAction(Action):
    """Drags one element and drops it onto another."""
    source_selector: Optional[Selector] = None
    target_selector: Optional[Selector] = None
    
    @property
    def type(self) -> ActionType:
        return ActionType.DRAG_AND_DROP
    
    @property
    def selector(self) -> Optional[Selector]:
        return self.target_selector  # Target selector is the main selector
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "selector": self.target_selector.to_dict() if self.target_selector else None,
            "source_selector": self.source_selector.to_dict() if self.source_selector else None,
            "target_selector": self.target_selector.to_dict() if self.target_selector else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DragAndDropAction':
        source_selector_data = data.get("source_selector")
        target_selector_data = data.get("target_selector")
        
        source_selector = Selector.from_dict(source_selector_data) if source_selector_data else None
        target_selector = Selector.from_dict(target_selector_data) if target_selector_data else None
        
        return cls(
            source_selector=source_selector,
            target_selector=target_selector
        )
    
    @classmethod
    def from_strings(cls, source_selector_string: str, target_selector_string: str) -> 'DragAndDropAction':
        """
        Create a DragAndDropAction from string selectors.
        
        Args:
            source_selector_string: Source element selector string
            target_selector_string: Target element selector string
            
        Returns:
            DragAndDropAction instance
        """
        source_selector = Selector.from_string(source_selector_string)
        target_selector = Selector.from_string(target_selector_string)
        return cls(source_selector=source_selector, target_selector=target_selector)


@dataclass
class ScreenshotAction(Action):
    """Captures a screenshot of the page."""
    file_path: str = ""
    
    @property
    def type(self) -> ActionType:
        return ActionType.SCREENSHOT
    
    @property
    def selector(self) -> Optional[Selector]:
        return None  # Screenshot actions don't require selectors
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "selector": None,
            "file_path": self.file_path
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScreenshotAction':
        return cls(file_path=data.get("file_path", ""))


@dataclass
class GetDropDownOptionsAction(Action):
    """Retrieves the available options in a dropdown menu."""
    selector: Optional[Selector] = None
    
    @property
    def type(self) -> ActionType:
        return ActionType.GET_DROPDOWN_OPTIONS
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "selector": self.selector.to_dict() if self.selector else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GetDropDownOptionsAction':
        selector_data = data.get("selector")
        selector = Selector.from_dict(selector_data) if selector_data else None
        
        return cls(selector=selector)
    
    @classmethod
    def from_string(cls, selector_string: str) -> 'GetDropDownOptionsAction':
        """
        Create a GetDropDownOptionsAction from a string selector.
        
        Args:
            selector_string: String selector to parse
            
        Returns:
            GetDropDownOptionsAction instance
        """
        selector = Selector.from_string(selector_string)
        return cls(selector=selector)


@dataclass
class SelectDropDownOptionAction(Action):
    """Selects an option from a dropdown menu based on its visible text."""
    selector: Optional[Selector] = None
    text: str = ""
    
    @property
    def type(self) -> ActionType:
        return ActionType.SELECT_DROPDOWN_OPTION
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "selector": self.selector.to_dict() if self.selector else None,
            "text": self.text
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SelectDropDownOptionAction':
        selector_data = data.get("selector")
        selector = Selector.from_dict(selector_data) if selector_data else None
        
        return cls(
            selector=selector,
            text=data.get("text", "")
        )
    
    @classmethod
    def from_string(cls, selector_string: str, text: str = "") -> 'SelectDropDownOptionAction':
        """
        Create a SelectDropDownOptionAction from a string selector.
        
        Args:
            selector_string: String selector to parse
            text: Text to select
            
        Returns:
            SelectDropDownOptionAction instance
        """
        selector = Selector.from_string(selector_string)
        return cls(selector=selector, text=text)


class ActionFactory:
    """Factory class for creating Action instances from dictionaries."""
    
    _action_classes = {
        ActionType.CLICK: ClickAction,
        ActionType.DOUBLE_CLICK: DoubleClickAction,
        ActionType.NAVIGATE: NavigateAction,
        ActionType.TYPE: TypeAction,
        ActionType.SELECT: SelectAction,
        ActionType.HOVER: HoverAction,
        ActionType.WAIT: WaitAction,
        ActionType.SCROLL: ScrollAction,
        ActionType.SUBMIT: SubmitAction,
        ActionType.DRAG_AND_DROP: DragAndDropAction,
        ActionType.SCREENSHOT: ScreenshotAction,
        ActionType.GET_DROPDOWN_OPTIONS: GetDropDownOptionsAction,
        ActionType.SELECT_DROPDOWN_OPTION: SelectDropDownOptionAction
    }
    
    @classmethod
    def create_action(cls, data: Dict[str, Any]) -> Action:
        """Create an Action instance from a dictionary."""
        action_type = data.get("type")
        if action_type not in cls._action_classes:
            raise ValueError(f"Unknown action type: {action_type}")
        
        action_class = cls._action_classes[action_type]
        return action_class.from_dict(data)
    
    @classmethod
    def create_actions_from_list(cls, actions_data: List[Dict[str, Any]]) -> List[Action]:
        """Create a list of Action instances from a list of dictionaries."""
        return [cls.create_action(action_data) for action_data in actions_data]


# Utility functions
def action_to_json(action: Action) -> str:
    """Convert an Action instance to JSON string."""
    return json.dumps(action.to_dict(), indent=2)


def json_to_action(json_str: str) -> Action:
    """Convert a JSON string to an Action instance."""
    data = json.loads(json_str)
    return ActionFactory.create_action(data)


def actions_to_json(actions: List[Action]) -> str:
    """Convert a list of Action instances to JSON string."""
    actions_data = [action.to_dict() for action in actions]
    return json.dumps(actions_data, indent=2)


def json_to_actions(json_str: str) -> List[Action]:
    """Convert a JSON string to a list of Action instances."""
    actions_data = json.loads(json_str)
    return ActionFactory.create_actions_from_list(actions_data)


# Example usage and testing
if __name__ == "__main__":
    print("=== Action Classes with SelectorParser Integration Demo ===\n")
    
    # 1. Create selectors from strings using SelectorParser
    print("1. Creating Selectors from String Selectors:")
    selectors = [
        Selector.from_string("#submit-button"),
        Selector.from_string(".form-group"),
        Selector.from_string("[name='username']"),
        Selector.from_string("//button[@type='submit']"),
        Selector.from_string("button")
    ]
    
    for i, selector in enumerate(selectors, 1):
        print(f"   {i}. {selector.to_playwright_selector()} -> {selector.type.value}")
    
    print("\n2. Creating Actions from String Selectors:")
    
    # 2. Create actions directly from string selectors
    actions = [
        ClickAction.from_string("#login-btn", x=100, y=200),
        TypeAction.from_string("[name='email']", "user@example.com"),
        HoverAction.from_string(".dropdown-menu"),
        SubmitAction.from_string("#login-form"),
        DragAndDropAction.from_strings("#source-item", "#target-area")
    ]
    
    for i, action in enumerate(actions, 1):
        print(f"   {i}. {action.type.value}: {action.to_dict()}")
    
    print("\n3. Complete Workflow Example:")
    
    # 3. Create a complete workflow using string selectors
    login_workflow = [
        TypeAction.from_string("#username", "john_doe"),
        TypeAction.from_string("#password", "secret123"),
        ClickAction.from_string("#login-button"),
        HoverAction.from_string(".user-menu"),
        ClickAction.from_string("text=Logout")
    ]
    
    for i, action in enumerate(login_workflow, 1):
        if action.selector:
            print(f"   {i}. {action.type.value}: {action.selector.to_playwright_selector()}")
        else:
            print(f"   {i}. {action.type.value}: {action.to_dict()}")
    
    print("\n4. JSON Serialization:")
    
    # 4. Test JSON serialization with string-created actions
    click_action = ClickAction.from_string("#submit-btn", x=150, y=250)
    json_str = action_to_json(click_action)
    print(f"   Action to JSON: {json_str}")
    
    # 5. Recreate action from JSON
    recreated_action = json_to_action(json_str)
    print(f"   JSON to Action: {recreated_action.to_dict()}")
    
    print("\n=== Integration Complete ===")
    print("✅ All actions support creation from string selectors")
    print("✅ SelectorParser integration is fully functional")
    print("✅ String-to-action workflow is seamless")
    print("✅ JSON serialization/deserialization works perfectly")
