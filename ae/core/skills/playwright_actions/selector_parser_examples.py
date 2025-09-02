"""
Selector Parser and Generator Examples

This module demonstrates how to use the selector parser to convert string selectors
into structured JSON format for Playwright actions, and how to use the new SelectorGenerator
to create XPath selectors from mmid-based selectors.
"""

try:
    from .selector_parser import (
        parse_selector, 
        parse_selectors, 
        selector_to_json, 
        validate_selector_string,
        generate_selector,
        get_selector_generator
    )
    from .action_classes import Selector, ClickAction, TypeAction
except ImportError:
    from selector_parser import (
        parse_selector, 
        parse_selectors, 
        selector_to_json, 
        validate_selector_string,
        generate_selector,
        get_selector_generator
    )
    from action_classes import Selector, ClickAction, TypeAction


def demonstrate_selector_parsing():
    """Demonstrate various selector parsing examples."""
    
    print("=== Selector Parser Examples ===\n")
    
    # Example selectors
    examples = [
        {
            "description": "XPath selectors",
            "selectors": [
                "//div[@class='container']",
                "//input[@type='text' and @placeholder='Enter name']",
                "//button[contains(text(), 'Submit')]",
                "/html/body/div[1]/form/input[1]"
            ]
        },
        {
            "description": "ID selectors",
            "selectors": [
                "#submit-button",
                "#username",
                "#login-form"
            ]
        },
        {
            "description": "Class selectors", 
            "selectors": [
                ".form-group",
                ".btn-primary",
                ".container-fluid"
            ]
        },
        {
            "description": "Attribute selectors",
            "selectors": [
                "[name='username']",
                "[type='submit']",
                "[data-testid='login-button']",
                "[placeholder='Enter email']"
            ]
        },
        {
            "description": "Text selectors",
            "selectors": [
                "text=Submit",
                "text:Login",
                "text=Click here to continue"
            ]
        },
        {
            "description": "Tag selectors",
            "selectors": [
                "button",
                "input",
                "div",
                "form"
            ]
        },
        {
            "description": "CSS selectors",
            "selectors": [
                "div.container > input",
                "form .form-group input[type='text']",
                "button.btn-primary:hover"
            ]
        }
    ]
    
    for example_group in examples:
        print(f"--- {example_group['description']} ---")
        
        for selector in example_group['selectors']:
            try:
                # Parse the selector
                parsed = parse_selector(selector)
                
                # Convert to JSON
                json_data = selector_to_json(selector)
                
                # Validate
                is_valid = validate_selector_string(selector)
                
                print(f"\nSelector: {selector}")
                print(f"Type: {parsed.type.value}")
                print(f"JSON: {json_data}")
                print(f"Valid: {is_valid}")
                
            except Exception as e:
                print(f"\nSelector: {selector}")
                print(f"Error: {e}")
        
        print("\n" + "="*50 + "\n")


def demonstrate_playwright_integration():
    """Demonstrate how to use parsed selectors with Playwright actions."""
    
    print("=== Playwright Integration Examples ===\n")
    
    # Example: Converting string selectors to JSON for Playwright actions
    action_examples = [
        {
            "action": "click",
            "selector": "#submit-button",
            "description": "Click a submit button by ID"
        },
        {
            "action": "type",
            "selector": "[name='username']",
            "text": "john_doe",
            "description": "Type text into username field"
        },
        {
            "action": "select",
            "selector": "//select[@name='country']",
            "value": "US",
            "description": "Select option from dropdown using XPath"
        },
        {
            "action": "hover",
            "selector": ".menu-item",
            "description": "Hover over menu item"
        }
    ]
    
    for example in action_examples:
        print(f"Action: {example['action']}")
        print(f"Description: {example['description']}")
        print(f"Original Selector: {example['selector']}")
        
        # Parse selector to JSON
        selector_json = selector_to_json(example['selector'])
        
        # Create action JSON structure
        action_json = {
            "action": example['action'],
            "selector": selector_json
        }
        
        # Add additional fields if present
        if 'text' in example:
            action_json['text'] = example['text']
        if 'value' in example:
            action_json['value'] = example['value']
        
        print(f"Action JSON: {action_json}")
        print("-" * 40 + "\n")


def demonstrate_batch_processing():
    """Demonstrate batch processing of multiple selectors."""
    
    print("=== Batch Processing Examples ===\n")
    
    # List of selectors to process
    selectors = [
        "#login-form",
        ".username-field", 
        "[name='password']",
        "//button[@type='submit']",
        "text=Remember me",
        "input[type='checkbox']"
    ]
    
    print("Processing multiple selectors:")
    for selector in selectors:
        print(f"  - {selector}")
    
    print(f"\nParsing {len(selectors)} selectors...")
    
    # Parse all selectors at once
    parsed_selectors = parse_selectors(selectors)
    
    print(f"\nResults:")
    for i, (original, parsed) in enumerate(zip(selectors, parsed_selectors)):
        print(f"{i+1}. {original}")
        print(f"   Type: {parsed.type.value}")
        print(f"   JSON: {parsed.data}")
        print()


def demonstrate_validation():
    """Demonstrate selector validation."""
    
    print("=== Selector Validation Examples ===\n")
    
    test_cases = [
        ("#valid-id", True),
        ("//valid/xpath", True),
        (".valid-class", True),
        ("[name='valid']", True),
        ("text=Valid text", True),
        ("", False),  # Empty string
        ("invalid selector with spaces and special chars !@#$%", True),  # Will be treated as tag
        (None, False),  # None value
    ]
    
    for selector, expected in test_cases:
        try:
            is_valid = validate_selector_string(selector) if selector is not None else False
            status = "✅ PASS" if is_valid == expected else "❌ FAIL"
            print(f"{status} | Selector: {repr(selector)} | Valid: {is_valid} | Expected: {expected}")
        except Exception as e:
            status = "❌ ERROR" if expected else "✅ PASS"
            print(f"{status} | Selector: {repr(selector)} | Error: {e} | Expected: {expected}")


def demonstrate_conversion_back_to_playwright():
    """Demonstrate converting parsed selectors back to Playwright format."""
    
    print("=== Conversion Back to Playwright Format ===\n")
    
    # Create a temporary parser for legacy functionality
    class LegacySelectorParser:
        def __init__(self):
            self.xpath_patterns = [
                r'^//', r'^/html', r'^\.\./', r'^ancestor::', r'^descendant::',
                r'^following::', r'^preceding::', r'^parent::', r'^child::',
                r'^self::', r'^attribute::', r'^namespace::',
            ]
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
        
        def to_playwright_selector(self, parsed_selector) -> str:
            """Convert parsed selector back to Playwright-compatible string."""
            from selector_parser import SelectorType
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
            else:  # TAG_CONTAINS
                return data["value"]
    
    parser = LegacySelectorParser()
    
    selectors = [
        "#submit-button",
        ".form-group",
        "[name='username']",
        "//div[@class='container']",
        "text=Submit",
        "button"
    ]
    
    for selector in selectors:
        try:
            # Parse the selector
            parsed = parse_selector(selector)
            
            # Convert back to Playwright format
            playwright_selector = parser.to_playwright_selector(parsed)
            
            print(f"Original: {selector}")
            print(f"Parsed Type: {parsed.type.value}")
            print(f"Playwright Format: {playwright_selector}")
            print(f"Round-trip Match: {selector == playwright_selector}")
            print("-" * 40)
            
        except Exception as e:
            print(f"Error processing '{selector}': {e}")


async def demonstrate_selector_generator():
    """Demonstrate the new SelectorGenerator functionality."""
    import asyncio
    from playwright.async_api import async_playwright
    
    print("=== Selector Generator Examples ===\n")
    
    # Test cases with mmid selectors
    test_selectors = [
        "[mmid='114']",  # mmid selector
        "[mmid='submit-button']",  # mmid selector
        "[mmid='form-group']",  # mmid selector
        "[mmid='nonexistent']",  # Non-existent mmid selector
    ]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_content("""
            <html>
                <body>
                    <div mmid="114">Test Element 1</div>
                    <button mmid="submit-button">Submit</button>
                    <div mmid="form-group">Form Group</div>
                    <input mmid="username" type="text" placeholder="Username">
                </body>
            </html>
        """)
        
        print("1. Generating XPath selectors from mmid-based selectors:")
        for selector in test_selectors:
            try:
                xpath = await generate_selector(page, selector)
                if xpath:
                    print(f"   {selector} -> {xpath}")
                else:
                    print(f"   {selector} -> No elements found (returned None)")
            except Exception as e:
                print(f"   {selector} -> Error: {e}")
        
        print("\n2. Using SelectorGenerator directly:")
        generator = get_selector_generator()
        for selector in test_selectors[:2]:  # Test first two
            try:
                xpath = await generator.parse(page, selector)
                if xpath:
                    print(f"   {selector} -> {xpath}")
                else:
                    print(f"   {selector} -> No elements found (returned None)")
            except Exception as e:
                print(f"   {selector} -> Error: {e}")
        
        await browser.close()
    
    print("\n✅ SelectorGenerator demonstration complete!")


async def demonstrate_action_classes_with_generator():
    """Demonstrate using action classes with SelectorGenerator."""
    import asyncio
    from playwright.async_api import async_playwright
    
    print("=== Action Classes with SelectorGenerator Examples ===\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_content("""
            <html>
                <body>
                    <div mmid="114">Test Element 1</div>
                    <button mmid="submit-button">Submit</button>
                    <input mmid="username" type="text" placeholder="Username">
                    <div mmid="form-group">Form Group</div>
                </body>
            </html>
        """)
        
        print("1. Creating Selector instances with SelectorGenerator:")
        selectors = [
            "[mmid='114']",
            "[mmid='submit-button']",
            "[mmid='username']",
            "[mmid='nonexistent']",  # This should return None
        ]
        
        for selector in selectors:
            try:
                selector_obj = await Selector.from_string_with_generator(page, selector)
                if selector_obj:
                    print(f"   {selector} -> {selector_obj.type.value}: {selector_obj.value}")
                else:
                    print(f"   {selector} -> None (no elements found)")
            except Exception as e:
                print(f"   {selector} -> Error: {e}")
        
        print("\n2. Creating Action instances with SelectorGenerator:")
        
        # Create ClickAction
        try:
            click_action = await ClickAction.from_string_with_generator(page, "[mmid='submit-button']", x=100, y=200)
            if click_action:
                print(f"   ClickAction: {click_action.to_dict()}")
            else:
                print("   ClickAction: None (no elements found)")
        except Exception as e:
            print(f"   ClickAction: Error: {e}")
        
        # Create TypeAction
        try:
            type_action = await TypeAction.from_string_with_generator(page, "[mmid='username']", "test_user")
            if type_action:
                print(f"   TypeAction: {type_action.to_dict()}")
            else:
                print("   TypeAction: None (no elements found)")
        except Exception as e:
            print(f"   TypeAction: Error: {e}")
        
        # Test with non-existent selector
        try:
            non_existent_action = await ClickAction.from_string_with_generator(page, "[mmid='nonexistent']")
            if non_existent_action:
                print(f"   Non-existent ClickAction: {non_existent_action.to_dict()}")
            else:
                print("   Non-existent ClickAction: None (no elements found)")
        except Exception as e:
            print(f"   Non-existent ClickAction: Error: {e}")
        
        await browser.close()
    
    print("\n✅ Action classes with SelectorGenerator demonstration complete!")


def main():
    """Run all demonstration examples."""
    demonstrate_selector_parsing()
    demonstrate_playwright_integration()
    demonstrate_batch_processing()
    demonstrate_validation()
    demonstrate_conversion_back_to_playwright()
    
    # Run the async demos
    import asyncio
    asyncio.run(demonstrate_selector_generator())
    asyncio.run(demonstrate_action_classes_with_generator())


if __name__ == "__main__":
    main()
