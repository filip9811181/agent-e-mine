# Playwright Actions JSON Structure

This module provides a structured JSON format for defining Playwright automation actions, making it easy to create, validate, and execute web automation tasks.

## Overview

The JSON structure supports six main action types:
- `click` - Click on elements
- `drag_and_drop` - Drag elements from one location to another
- `enter_text` - Enter text into input fields
- `enter_text_and_click` - Enter text and then click another element
- `open_url` - Navigate to a URL
- `submit_form` - Submit forms

## Selector Types

### 1. attributeValueSelector
Selects elements based on specific attributes.

**Fields:**
- `type`: Must be `"attributeValueSelector"`
- `attribute`: The attribute to use (`"id"`, `"class"`, or `"name"`)
- `value`: The attribute's value

**Examples:**
```json
{
  "type": "attributeValueSelector",
  "attribute": "id",
  "value": "submit-button"
}
```

**Playwright Conversion:**
- `id` → `#value`
- `class` → `.value`
- `name` → `[name='value']`

### 2. tagContainsSelector
Selects elements based on tag content.

**Fields:**
- `type`: Must be `"tagContainsSelector"`
- `value`: The text content to match

**Example:**
```json
{
  "type": "tagContainsSelector",
  "value": "Submit"
}
```

**Playwright Conversion:** `text=value`

### 3. xpathSelector
Selects elements using XPath expressions.

**Fields:**
- `type`: Must be `"xpathSelector"`
- `value`: The XPath query (must start with `/` or `//`)

**Example:**
```json
{
  "type": "xpathSelector",
  "value": "//button[@type='submit']"
}
```

**Playwright Conversion:** Used directly as XPath

## Action Definitions

### Click Action
```json
{
  "action": "click",
  "selector": {
    "type": "attributeValueSelector",
    "attribute": "id",
    "value": "submit-button"
  },
  "wait_before_execution": 1.0,
  "description": "Click the submit button"
}
```

### Drag and Drop Action
```json
{
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
}
```

### Enter Text Action
```json
{
  "action": "enter_text",
  "selector": {
    "type": "attributeValueSelector",
    "attribute": "id",
    "value": "username"
  },
  "text_to_enter": "john_doe",
  "use_keyboard_fill": true,
  "description": "Enter username"
}
```

### Enter Text and Click Action
```json
{
  "action": "enter_text_and_click",
  "text_selector": {
    "type": "attributeValueSelector",
    "attribute": "id",
    "value": "search-input"
  },
  "text_to_enter": "playwright automation",
  "click_selector": {
    "type": "tagContainsSelector",
    "value": "Search"
  },
  "description": "Enter search text and click search button"
}
```

### Submit Form Action
```json
{
  "action": "submit_form",
  "selector": {
    "type": "tagContainsSelector",
    "value": "Submit"
  },
  "description": "Submit the form"
}
```

### Open URL Action
```json
{
  "action": "open_url",
  "url": "https://example.com",
  "description": "Open example website"
}
```

## Usage

### Basic Usage
```python
from ae.core.skills.playwright_action_executor import execute_action_from_json

# Execute a single action
action_json = {
    "action": "click",
    "selector": {
        "type": "attributeValueSelector",
        "attribute": "id",
        "value": "submit-button"
    }
}

result = await execute_action_from_json(action_json)
print(result)
```

### Execute Multiple Actions
```python
from ae.core.skills.playwright_action_executor import execute_actions_from_json

# Execute multiple actions
actions_json = [
    {
        "action": "open_url",
        "url": "https://example.com"
    },
    {
        "action": "enter_text",
        "selector": {
            "type": "attributeValueSelector",
            "attribute": "id",
            "value": "username"
        },
        "text_to_enter": "test_user"
    },
    {
        "action": "click",
        "selector": {
            "type": "tagContainsSelector",
            "value": "Login"
        }
    }
]

results = await execute_actions_from_json(actions_json)
for result in results:
    print(f"Action: {result['action']}, Status: {result['status']}")
```

### Using the Executor Class
```python
from ae.core.skills.playwright_action_executor import PlaywrightActionExecutor

executor = PlaywrightActionExecutor()

# Execute single action
result = await executor.execute_action(action_json)

# Execute multiple actions
results = await executor.execute_actions(actions_json)
```

## Validation

The system automatically validates:
- Required fields for each action type
- Selector format and type
- XPath syntax (must start with `/` or `//`)
- Attribute values (must be `id`, `class`, or `name`)

## Error Handling

Actions return structured results:
```python
{
    "action": "click",
    "status": "success",  # or "error"
    "result": "Success message"  # or "error": "error message"
}
```

## Best Practices

1. **Use appropriate selector types:**
   - `attributeValueSelector` for stable IDs and names
   - `tagContainsSelector` for descriptive button/link text
   - `xpathSelector` for complex selection scenarios

2. **Include descriptions** for better documentation

3. **Use wait times** when actions need timing considerations

4. **Validate selectors** before execution

5. **Handle errors** gracefully in your automation scripts

## Examples

See `playwright_actions_examples.json` for comprehensive examples of all action types and selector combinations.

## Schema Validation

The JSON schema is defined in `playwright_actions_schema.json` and can be used with JSON schema validators to ensure proper format.
