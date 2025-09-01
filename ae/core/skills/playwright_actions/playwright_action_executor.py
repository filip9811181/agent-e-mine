"""
Playwright Action Executor

This module provides functionality to execute Playwright actions defined in JSON format.
It parses the JSON action structures and calls the appropriate skill functions.
"""

import json
import logging
from typing import Any, Dict, List, Union
from playwright.async_api import Page

from ae.core.skills.click_using_selector import click
from ae.core.skills.drag_and_drop import drag_and_drop
from ae.core.skills.enter_text_and_click import enter_text_and_click
from ae.core.skills.enter_text_using_selector import entertext, EnterTextEntry
from ae.core.skills.open_url import openurl
from ae.core.skills.submit_form import submit_form
from ae.core.skills.playwright_actions import (
    selector_to_playwright_string,
    validate_selector,
    SelectorType
)

logger = logging.getLogger(__name__)


class PlaywrightActionExecutor:
    """
    Executes Playwright actions defined in JSON format.
    
    This class provides methods to parse and execute JSON action definitions
    for various Playwright automation tasks.
    """
    
    def __init__(self):
        """Initialize the action executor."""
        self.supported_actions = {
            "click": self._execute_click,
            "drag_and_drop": self._execute_drag_and_drop,
            "enter_text_and_click": self._execute_enter_text_and_click,
            "enter_text": self._execute_enter_text,
            "open_url": self._execute_open_url,
            "submit_form": self._execute_submit_form
        }
    
    async def execute_action(self, action_json: Union[str, Dict[str, Any]]) -> str:
        """
        Execute a single action defined in JSON format.
        
        Args:
            action_json: JSON string or dictionary defining the action
            
        Returns:
            Result of the action execution
            
        Raises:
            ValueError: If the action is invalid or unsupported
        """
        if isinstance(action_json, str):
            try:
                action_data = json.loads(action_json)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format: {e}")
        else:
            action_data = action_json
        
        action_type = action_data.get("action")
        if not action_type:
            raise ValueError("Action type is required")
        
        if action_type not in self.supported_actions:
            raise ValueError(f"Unsupported action type: {action_type}")
        
        logger.info(f"Executing action: {action_type}")
        return await self.supported_actions[action_type](action_data)
    
    async def execute_actions(self, actions_json: Union[str, List[Dict[str, Any]]]) -> List[str]:
        """
        Execute multiple actions defined in JSON format.
        
        Args:
            actions_json: JSON string or list of action dictionaries
            
        Returns:
            List of results from action executions
        """
        if isinstance(actions_json, str):
            try:
                actions_data = json.loads(actions_json)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format: {e}")
        else:
            actions_data = actions_json
        
        if not isinstance(actions_data, list):
            actions_data = [actions_data]
        
        results = []
        for action_data in actions_data:
            try:
                result = await self.execute_action(action_data)
                results.append({
                    "action": action_data.get("action"),
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                logger.error(f"Action execution failed: {e}")
                results.append({
                    "action": action_data.get("action"),
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    async def _execute_click(self, action_data: Dict[str, Any]) -> str:
        """Execute a click action."""
        selector = action_data.get("selector")
        if not selector:
            raise ValueError("Selector is required for click action")
        
        if not validate_selector(selector):
            raise ValueError("Invalid selector format")
        
        playwright_selector = selector_to_playwright_string(selector)
        wait_time = action_data.get("wait_before_execution", 0.0)
        
        return await click(playwright_selector, wait_time)
    
    async def _execute_drag_and_drop(self, action_data: Dict[str, Any]) -> str:
        """Execute a drag and drop action."""
        source_selector = action_data.get("source_selector")
        target_selector = action_data.get("target_selector")
        
        if not source_selector or not target_selector:
            raise ValueError("Both source_selector and target_selector are required for drag_and_drop action")
        
        if not validate_selector(source_selector) or not validate_selector(target_selector):
            raise ValueError("Invalid selector format")
        
        source_playwright_selector = selector_to_playwright_string(source_selector)
        target_playwright_selector = selector_to_playwright_string(target_selector)
        wait_time = action_data.get("wait_before_execution", 0.0)
        
        return await drag_and_drop(source_playwright_selector, target_playwright_selector, wait_time)
    
    async def _execute_enter_text_and_click(self, action_data: Dict[str, Any]) -> str:
        """Execute an enter text and click action."""
        text_selector = action_data.get("text_selector")
        text_to_enter = action_data.get("text_to_enter")
        click_selector = action_data.get("click_selector")
        
        if not all([text_selector, text_to_enter, click_selector]):
            raise ValueError("text_selector, text_to_enter, and click_selector are required for enter_text_and_click action")
        
        if not validate_selector(text_selector) or not validate_selector(click_selector):
            raise ValueError("Invalid selector format")
        
        text_playwright_selector = selector_to_playwright_string(text_selector)
        click_playwright_selector = selector_to_playwright_string(click_selector)
        wait_time = action_data.get("wait_before_click_execution", 0.0)
        
        return await enter_text_and_click(
            text_playwright_selector,
            text_to_enter,
            click_playwright_selector,
            wait_time
        )
    
    async def _execute_enter_text(self, action_data: Dict[str, Any]) -> str:
        """Execute an enter text action."""
        selector = action_data.get("selector")
        text_to_enter = action_data.get("text_to_enter")
        
        if not selector or not text_to_enter:
            raise ValueError("selector and text_to_enter are required for enter_text action")
        
        if not validate_selector(selector):
            raise ValueError("Invalid selector format")
        
        playwright_selector = selector_to_playwright_string(selector)
        
        # Create EnterTextEntry object
        entry = EnterTextEntry(
            query_selector=playwright_selector,
            text=text_to_enter
        )
        
        return await entertext(entry)
    
    async def _execute_open_url(self, action_data: Dict[str, Any]) -> str:
        """Execute an open URL action."""
        url = action_data.get("url")
        if not url:
            raise ValueError("URL is required for open_url action")
        
        return await openurl(url)
    
    async def _execute_submit_form(self, action_data: Dict[str, Any]) -> str:
        """Execute a submit form action."""
        selector = action_data.get("selector")
        if not selector:
            raise ValueError("Selector is required for submit_form action")
        
        if not validate_selector(selector):
            raise ValueError("Invalid selector format")
        
        playwright_selector = selector_to_playwright_string(selector)
        wait_time = action_data.get("wait_before_execution", 0.0)
        
        return await submit_form(playwright_selector, wait_time)


# Convenience functions for common use cases
async def execute_action_from_json(action_json: Union[str, Dict[str, Any]]) -> str:
    """
    Convenience function to execute a single action from JSON.
    
    Args:
        action_json: JSON string or dictionary defining the action
        
    Returns:
        Result of the action execution
    """
    executor = PlaywrightActionExecutor()
    return await executor.execute_action(action_json)


async def execute_actions_from_json(actions_json: Union[str, List[Dict[str, Any]]]) -> List[str]:
    """
    Convenience function to execute multiple actions from JSON.
    
    Args:
        actions_json: JSON string or list of action dictionaries
        
    Returns:
        List of results from action executions
    """
    executor = PlaywrightActionExecutor()
    return await executor.execute_actions(actions_json)


# Example usage and testing
if __name__ == "__main__":
    # Example action definitions
    example_actions = [
        {
            "action": "open_url",
            "url": "https://example.com",
            "description": "Open example website"
        },
        {
            "action": "enter_text",
            "selector": {
                "type": "attributeValueSelector",
                "attribute": "id",
                "value": "username"
            },
            "text_to_enter": "test_user",
            "description": "Enter username"
        },
        {
            "action": "click",
            "selector": {
                "type": "tagContainsSelector",
                "value": "Submit"
            },
            "description": "Click submit button"
        }
    ]
    
    # Convert to JSON string
    actions_json = json.dumps(example_actions, indent=2)
    print("Example actions JSON:")
    print(actions_json)
    
    # Example of individual action
    click_action = {
        "action": "click",
        "selector": {
            "type": "xpathSelector",
            "value": "//button[@type='submit']"
        },
        "description": "Click submit button using XPath"
    }
    
    print("\nExample click action:")
    print(json.dumps(click_action, indent=2))
