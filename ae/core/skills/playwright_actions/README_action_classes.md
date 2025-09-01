# Playwright Action Classes

This module provides a comprehensive class-based implementation of the JSON structure for Playwright automation actions. Each action type is represented by a specific Python class with appropriate fields, validation, and conversion methods.

## Overview

The action system consists of:

1. **Action Classes** - Python classes representing different action types
2. **Selector Classes** - Classes for identifying HTML elements
3. **ActionFactory** - Factory class for creating actions from dictionaries
4. **Utility Functions** - Helper functions for JSON conversion

## Core Components

### Selector System

The `Selector` class supports three types of selectors:

#### 1. `attributeValueSelector`
Selects elements based on specific attributes (`id`, `class`, or `name`).

```python
from ae.core.skills.action_classes import Selector, SelectorType

# ID selector
id_selector = Selector(
    type=SelectorType.ATTRIBUTE_VALUE,
    attribute="id",
    value="submit-button"
)

# Class selector
class_selector = Selector(
    type=SelectorType.ATTRIBUTE_VALUE,
    attribute="class",
    value="btn-primary"
)

# Name selector
name_selector = Selector(
    type=SelectorType.ATTRIBUTE_VALUE,
    attribute="name",
    value="username"
)
```

#### 2. `tagContainsSelector`
Selects elements based on tag name and partial content.

```python
text_selector = Selector(
    type=SelectorType.TAG_CONTAINS,
    value="Submit"
)
```

#### 3. `xpathSelector`
Selects elements using XPath expressions.

```python
xpath_selector = Selector(
    type=SelectorType.XPATH,
    value="//button[@type='submit']"
)
```

### Action Types

The system supports 13 different action types:

#### 1. `ClickAction`
Performs a click on a specified HTML element.

```python
from ae.core.skills.action_classes import ClickAction

# Click with selector
click_action = ClickAction(
    selector=id_selector,
    description="Click submit button"
)

# Click at coordinates
click_action = ClickAction(
    x=100,
    y=200,
    description="Click at coordinates (100, 200)"
)
```

#### 2. `DoubleClickAction`
Performs a double-click on the specified element.

```python
from ae.core.skills.action_classes import DoubleClickAction

double_click_action = DoubleClickAction(
    selector=id_selector,
    description="Double-click on editable text"
)
```

#### 3. `NavigateAction`
Navigates to a different page or moves forward/backward in browsing history.

```python
from ae.core.skills.action_classes import NavigateAction

# Navigate to URL
navigate_action = NavigateAction(
    url="https://example.com",
    description="Navigate to example.com"
)

# Go back in history
go_back_action = NavigateAction(
    go_back=True,
    description="Go back to previous page"
)

# Go forward in history
go_forward_action = NavigateAction(
    go_forward=True,
    description="Go forward to next page"
)
```

#### 4. `TypeAction`
Types text into an input field.

```python
from ae.core.skills.action_classes import TypeAction

type_action = TypeAction(
    selector=name_selector,
    text="test_user",
    description="Enter username"
)
```

#### 5. `SelectAction`
Selects an option from a dropdown menu or selection field.

```python
from ae.core.skills.action_classes import SelectAction

select_action = SelectAction(
    selector=name_selector,
    value="US",
    description="Select US from country dropdown"
)
```

#### 6. `HoverAction`
Moves the cursor over a specified element.

```python
from ae.core.skills.action_classes import HoverAction

hover_action = HoverAction(
    selector=class_selector,
    description="Hover over menu item"
)
```

#### 7. `WaitAction`
Pauses execution for a specified duration.

```python
from ae.core.skills.action_classes import WaitAction

wait_action = WaitAction(
    time_seconds=2.5,
    description="Wait for page to load"
)
```

#### 8. `ScrollAction`
Scrolls up or down within a page or element.

```python
from ae.core.skills.action_classes import ScrollAction

# Scroll down
scroll_down = ScrollAction(
    down=True,
    description="Scroll down the page"
)

# Scroll to specific text
scroll_to_text = ScrollAction(
    selector=id_selector,
    value="Latest message",
    description="Scroll to latest message"
)
```

#### 9. `SubmitAction`
Submits a form by pressing Enter or clicking the submit button.

```python
from ae.core.skills.action_classes import SubmitAction

submit_action = SubmitAction(
    selector=id_selector,
    description="Submit the form"
)
```

#### 10. `DragAndDropAction`
Drags one element and drops it onto another.

```python
from ae.core.skills.action_classes import DragAndDropAction

drag_drop_action = DragAndDropAction(
    source_selector=id_selector,
    target_selector=class_selector,
    description="Drag item to drop zone"
)
```

#### 11. `ScreenshotAction`
Captures a screenshot of the page.

```python
from ae.core.skills.action_classes import ScreenshotAction

screenshot_action = ScreenshotAction(
    file_path="screenshots/page.png",
    description="Take page screenshot"
)
```

#### 12. `GetDropDownOptionsAction`
Retrieves the available options in a dropdown menu.

```python
from ae.core.skills.action_classes import GetDropDownOptionsAction

get_options_action = GetDropDownOptionsAction(
    selector=name_selector,
    description="Get dropdown options"
)
```

#### 13. `SelectDropDownOptionAction`
Selects an option from a dropdown menu based on its visible text.

```python
from ae.core.skills.action_classes import SelectDropDownOptionAction

select_option_action = SelectDropDownOptionAction(
    selector=id_selector,
    text="Premium Plan",
    description="Select Premium Plan option"
)
```

## Usage Examples

### Creating Actions Programmatically

```python
from ae.core.skills.action_classes import (
    ClickAction, TypeAction, NavigateAction, Selector, SelectorType
)

# Create selectors
username_selector = Selector(
    type=SelectorType.ATTRIBUTE_VALUE,
    attribute="name",
    value="username"
)

submit_selector = Selector(
    type=SelectorType.ATTRIBUTE_VALUE,
    attribute="id",
    value="submit-button"
)

# Create actions
navigate_action = NavigateAction(
    url="https://example.com/login",
    description="Navigate to login page"
)

type_action = TypeAction(
    selector=username_selector,
    text="test_user",
    description="Enter username"
)

click_action = ClickAction(
    selector=submit_selector,
    description="Click submit button"
)

# Convert to dictionary
actions_dict = [
    navigate_action.to_dict(),
    type_action.to_dict(),
    click_action.to_dict()
]
```

### Creating Actions from JSON

```python
from ae.core.skills.action_classes import ActionFactory

# JSON action data
action_data = {
    "type": "click",
    "selector": {
        "type": "attributeValueSelector",
        "attribute": "id",
        "value": "submit-button"
    },
    "description": "Click submit button"
}

# Create action instance
action = ActionFactory.create_action(action_data)
print(f"Action type: {action.type}")
print(f"Selector: {action.selector}")
```

### Batch Action Creation

```python
# List of action dictionaries
actions_data = [
    {
        "type": "navigate",
        "selector": null,
        "url": "https://example.com"
    },
    {
        "type": "type",
        "selector": {
            "type": "attributeValueSelector",
            "attribute": "name",
            "value": "search"
        },
        "text": "automation"
    },
    {
        "type": "click",
        "selector": {
            "type": "attributeValueSelector",
            "attribute": "id",
            "value": "search-button"
        }
    }
]

# Create all actions
actions = ActionFactory.create_actions_from_list(actions_data)
for action in actions:
    print(f"Created {action.type} action")
```

## Utility Functions

### JSON Conversion

```python
from ae.core.skills.action_classes import (
    action_to_json, json_to_action, actions_to_json, json_to_actions
)

# Single action to JSON
json_str = action_to_json(click_action)
print(json_str)

# JSON to action
action = json_to_action(json_str)

# Multiple actions to JSON
actions_json = actions_to_json([navigate_action, type_action, click_action])

# JSON to multiple actions
actions = json_to_actions(actions_json)
```

### Selector Conversion

```python
# Convert selector to Playwright-compatible string
playwright_selector = id_selector.to_playwright_selector()
print(playwright_selector)  # Output: #submit-button

# Convert selector to dictionary
selector_dict = id_selector.to_dict()
print(selector_dict)

# Create selector from dictionary
selector = Selector.from_dict(selector_dict)
```

## Validation and Error Handling

### Action Validation

The system automatically validates actions when creating them:

```python
try:
    # This will raise an error - missing required fields
    invalid_action = ClickAction()
except Exception as e:
    print(f"Validation error: {e}")
```

### Selector Validation

Selectors are validated for proper structure:

```python
try:
    # This will raise an error - missing attribute for attributeValueSelector
    invalid_selector = Selector(
        type=SelectorType.ATTRIBUTE_VALUE,
        value="button"
    )
except Exception as e:
    print(f"Selector validation error: {e}")
```

## Complex Workflows

### User Registration Workflow

```python
def create_registration_workflow():
    """Create a complete user registration workflow."""
    
    # Define selectors
    username_selector = Selector(
        type=SelectorType.ATTRIBUTE_VALUE,
        attribute="name",
        value="username"
    )
    
    email_selector = Selector(
        type=SelectorType.ATTRIBUTE_VALUE,
        attribute="name",
        value="email"
    )
    
    password_selector = Selector(
        type=SelectorType.ATTRIBUTE_VALUE,
        attribute="name",
        value="password"
    )
    
    submit_selector = Selector(
        type=SelectorType.ATTRIBUTE_VALUE,
        attribute="id",
        value="submit-button"
    )
    
    # Create workflow actions
    workflow = [
        NavigateAction(
            url="https://example.com/register",
            description="Navigate to registration page"
        ),
        WaitAction(
            time_seconds=2,
            description="Wait for page to load"
        ),
        TypeAction(
            selector=username_selector,
            text="newuser123",
            description="Enter username"
        ),
        TypeAction(
            selector=email_selector,
            text="user@example.com",
            description="Enter email"
        ),
        TypeAction(
            selector=password_selector,
            text="securepassword123",
            description="Enter password"
        ),
        ClickAction(
            selector=submit_selector,
            description="Submit registration form"
        ),
        WaitAction(
            time_seconds=3,
            description="Wait for form submission"
        )
    ]
    
    return workflow

# Create and execute workflow
workflow = create_registration_workflow()
workflow_json = actions_to_json(workflow)
print("Workflow JSON:")
print(workflow_json)
```

## Best Practices

1. **Always include descriptions** for better action documentation
2. **Use appropriate selector types** for different scenarios
3. **Prefer `attributeValueSelector`** for stable elements (id, name)
4. **Use `tagContainsSelector`** for text-based selection
5. **Use `xpathSelector`** for complex element relationships
6. **Set appropriate wait times** for page interactions
7. **Handle errors gracefully** with proper validation
8. **Use meaningful file paths** for screenshots
9. **Group related actions** into workflows
10. **Test selectors** before using them in automation

## Error Handling

### Common Error Scenarios

1. **Element not found** - Selector may be invalid or element not loaded
2. **Timeout errors** - Increase wait times or check page state
3. **Invalid selector format** - Ensure proper JSON structure
4. **Missing required fields** - Check action type requirements
5. **Conflicting parameters** - Avoid setting both go_back and go_forward

### Validation Rules

- All actions must have a `type` field
- Selectors must have `type` and `value` fields
- `attributeValueSelector` requires `attribute` field
- Navigate actions cannot have both go_back and go_forward true
- Wait actions must have selector set to null
- Screenshot actions must have selector set to null

## Integration with Playwright

The action classes are designed to work seamlessly with Playwright:

```python
from playwright.async_api import async_playwright
from ae.core.skills.action_classes import ActionFactory

async def execute_actions(page, actions_json):
    """Execute actions on a Playwright page."""
    
    actions = json_to_actions(actions_json)
    
    for action in actions:
        try:
            if action.type == ActionType.CLICK:
                if action.selector:
                    selector = action.selector.to_playwright_selector()
                    await page.click(selector)
                elif action.x is not None and action.y is not None:
                    await page.click(position={"x": action.x, "y": action.y})
                    
            elif action.type == ActionType.TYPE:
                selector = action.selector.to_playwright_selector()
                await page.fill(selector, action.text)
                
            elif action.type == ActionType.NAVIGATE:
                if action.url:
                    await page.goto(action.url)
                elif action.go_back:
                    await page.go_back()
                elif action.go_forward:
                    await page.go_forward()
                    
            elif action.type == ActionType.WAIT:
                await page.wait_for_timeout(action.time_seconds * 1000)
                
            print(f"Executed {action.type} action successfully")
            
        except Exception as e:
            print(f"Error executing {action.type} action: {e}")
            break

# Usage example
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Execute actions
        await execute_actions(page, workflow_json)
        
        await browser.close()

# Run the automation
# await main()
```

This provides a powerful, type-safe, and flexible way to define and execute Playwright automation workflows using structured JSON actions.
