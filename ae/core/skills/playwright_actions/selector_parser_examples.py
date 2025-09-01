"""
Selector Parser Examples

This module demonstrates how to use the selector parser to convert string selectors
into structured JSON format for Playwright actions.
"""

from selector_parser import (
    parse_selector, 
    parse_selectors, 
    selector_to_json, 
    validate_selector_string,
    get_selector_parser
)


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
    
    parser = get_selector_parser()
    
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


def main():
    """Run all demonstration examples."""
    demonstrate_selector_parsing()
    demonstrate_playwright_integration()
    demonstrate_batch_processing()
    demonstrate_validation()
    demonstrate_conversion_back_to_playwright()


if __name__ == "__main__":
    main()
