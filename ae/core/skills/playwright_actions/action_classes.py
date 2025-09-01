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
    # Create a selector
    selector = Selector(
        type=SelectorType.ATTRIBUTE_VALUE,
        attribute="id",
        value="submit-button"
    )
    
    # Create various actions
    click_action = ClickAction(selector=selector, x=100, y=200)
    navigate_action = NavigateAction(url="https://example.com")
    type_action = TypeAction(selector=selector, text="Hello World")
    
    # Convert to dictionary
    print("Click Action Dict:")
    print(click_action.to_dict())
    
    print("\nNavigate Action Dict:")
    print(navigate_action.to_dict())
    
    print("\nType Action Dict:")
    print(type_action.to_dict())
    
    # Convert to JSON
    print("\nClick Action JSON:")
    print(action_to_json(click_action))
    
    # Create action from dictionary
    action_data = {
        "type": "click",
        "selector": {
            "type": "attributeValueSelector",
            "attribute": "class",
            "value": "btn-primary"
        },
        "x": 150,
        "y": 250
    }
    
    recreated_action = ActionFactory.create_action(action_data)
    print(f"\nRecreated Action Type: {recreated_action.type}")
    print(f"Recreated Action Selector: {recreated_action.selector}")
