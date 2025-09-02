"""
Selector Generator Module

This module provides functionality to generate XPath selectors from mmid-based selectors
for Playwright actions. It queries elements from the current page and generates XPath
selectors when elements are found.
"""

import re
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from enum import Enum
from playwright.async_api import Page


class SelectorType(Enum):
    """Enumeration of supported selector types."""
    XPATH = "xpathSelector"
    ATTRIBUTE_VALUE = "attributeValueSelector"
    TAG_CONTAINS = "tagContainsSelector"


@dataclass
class ParsedSelector:
    """Represents a parsed selector with its type and data."""
    type: SelectorType
    data: Dict[str, Any]
    original_string: str


class SelectorGenerator:
    """Generator for creating XPath selectors from mmid-based selectors."""
    
    def __init__(self):
        """Initialize the selector generator."""
        pass
    
    async def parse(self, page: Page, selector_with_mmid: str) -> Optional[str]:
        """
        Generate XPath selector from mmid-based selector by querying elements from current page.
        
        Args:
            page: The Playwright Page object representing the browser tab
            selector_with_mmid: The selector string with mmid attribute
            
        Returns:
            XPath selector string if elements found, None if no elements found
        """
        if not selector_with_mmid or not isinstance(selector_with_mmid, str):
            return None
        
        selector_with_mmid = selector_with_mmid.strip()
        
        try:
            # Query elements from current page using the mmid selector
            elements = await page.query_selector_all(selector_with_mmid)
            
            # If element count is greater than 0, generate XPath selector
            if len(elements) > 0:
                # Generate XPath for the first element
                xpath_selector = await self._generate_xpath_for_element(page, elements[0])
                return xpath_selector
            else:
                # If count is 0, return None
                return None
                
        except Exception:
            # If there's any error, return None
            return None
    
    async def _generate_xpath_for_element(self, page: Page, element) -> str:
        """
        Generate XPath selector for a given element with priority on id and class attributes.
        
        Args:
            page: The Playwright Page object
            element: The element to generate XPath for
            
        Returns:
            XPath selector string
        """
        try:
            # Get element attributes for better XPath generation
            element_info = await page.evaluate("""
                (element) => {
                    return {
                        tagName: element.tagName.toLowerCase(),
                        id: element.id || '',
                        className: element.className || '',
                        name: element.name || '',
                        type: element.type || '',
                        value: element.value || '',
                        text: element.textContent ? element.textContent.trim() : '',
                        href: element.href || '',
                        src: element.src || '',
                        title: element.title || '',
                        placeholder: element.placeholder || '',
                        'data-testid': element.getAttribute('data-testid') || '',
                        'data-id': element.getAttribute('data-id') || '',
                        'data-value': element.getAttribute('data-value') || ''
                    };
                }
            """, element)
            
            tag_name = element_info['tagName']
            
            # Priority 1: Use ID if available and unique
            if element_info['id']:
                # Check if ID is unique on the page
                id_count = await page.evaluate(f"document.querySelectorAll('#{element_info['id']}').length")
                if id_count == 1:
                    return f"//*[@id='{element_info['id']}']"
                else:
                    # If ID is not unique, use tag + ID combination
                    return f"//{tag_name}[@id='{element_info['id']}']"
            
            # Priority 2: Use class if available and meaningful
            if element_info['className']:
                classes = element_info['className'].split()
                # Filter out common utility classes that might not be unique
                meaningful_classes = [cls for cls in classes if not cls.startswith(('col-', 'row-', 'd-', 'p-', 'm-', 'text-', 'bg-', 'border-'))]
                
                if meaningful_classes:
                    # Use the first meaningful class
                    primary_class = meaningful_classes[0]
                    # Check if this class combination is unique
                    class_selector = f".{'.'.join(meaningful_classes)}"
                    class_count = await page.evaluate(f"document.querySelectorAll('{class_selector}').length")
                    
                    if class_count == 1:
                        return f"//*[@class='{element_info['className']}']"
                    else:
                        return f"//{tag_name}[@class='{element_info['className']}']"
            
            # Priority 3: Use other unique attributes
            unique_attrs = ['name', 'data-testid', 'data-id', 'href', 'src', 'title', 'placeholder']
            for attr in unique_attrs:
                if element_info[attr]:
                    # Check if this attribute value is unique
                    attr_count = await page.evaluate(f"document.querySelectorAll('[{attr}=\"{element_info[attr]}\"]').length")
                    if attr_count == 1:
                        return f"//*[@{attr}='{element_info[attr]}']"
                    else:
                        return f"//{tag_name}[@{attr}='{element_info[attr]}']"
            
            # Priority 4: Use text content if it's unique and meaningful
            if element_info['text'] and len(element_info['text']) > 0 and len(element_info['text']) < 50:
                # Check if this text is unique
                text_count = await page.evaluate(f"document.evaluate('count(//*[text()=\"{element_info['text']}\"])', document, null, XPathResult.NUMBER_TYPE, null).numberValue")
                if text_count == 1:
                    return f"//*[text()='{element_info['text']}']"
                else:
                    return f"//{tag_name}[text()='{element_info['text']}']"
            
            # Priority 5: Use combination of tag + multiple attributes
            if element_info['className'] and element_info['name']:
                return f"//{tag_name}[@class='{element_info['className']}' and @name='{element_info['name']}']"
            elif element_info['className'] and element_info['type']:
                return f"//{tag_name}[@class='{element_info['className']}' and @type='{element_info['type']}']"
            elif element_info['name'] and element_info['type']:
                return f"//{tag_name}[@name='{element_info['name']}' and @type='{element_info['type']}']"
            
            # Priority 6: Use tag with class (even if not unique)
            if element_info['className']:
                return f"//{tag_name}[@class='{element_info['className']}']"
            
            # Priority 7: Use tag with name
            if element_info['name']:
                return f"//{tag_name}[@name='{element_info['name']}']"
            
            # Priority 8: Use tag with type
            if element_info['type']:
                return f"//{tag_name}[@type='{element_info['type']}']"
            
            # Priority 9: Fallback to hierarchical XPath with position
            return await self._generate_hierarchical_xpath(page, element)
            
        except Exception:
            # Final fallback: try to generate a simple XPath based on tag
            try:
                tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                return f'//{tag_name}'
            except Exception:
                return '//*'
    
    async def _generate_hierarchical_xpath(self, page: Page, element) -> str:
        """
        Generate hierarchical XPath using element position as fallback.
        
        Args:
            page: The Playwright Page object
            element: The element to generate XPath for
            
        Returns:
            XPath selector string
        """
        try:
            xpath = await page.evaluate("""
                (element) => {
                    function getXPath(element) {
                        if (element === document.body) {
                            return element.tagName.toLowerCase();
                        }
                        
                        var ix = 0;
                        var siblings = element.parentNode.childNodes;
                        for (var i = 0; i < siblings.length; i++) {
                            var sibling = siblings[i];
                            if (sibling === element) {
                                return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                            }
                            if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                                ix++;
                            }
                        }
                    }
                    return getXPath(element);
                }
            """, element)
            
            # Ensure it starts with //
            if not xpath.startswith('//'):
                xpath = '//' + xpath
                
            return xpath
            
        except Exception:
            return '//*'
    



# Global selector generator instance
_selector_generator: Optional[SelectorGenerator] = None


def get_selector_generator() -> SelectorGenerator:
    """Get the global selector generator instance."""
    global _selector_generator
    if _selector_generator is None:
        _selector_generator = SelectorGenerator()
    return _selector_generator


async def generate_selector(page: Page, selector_with_mmid: str) -> Optional[str]:
    """
    Convenience function to generate XPath selector from mmid-based selector.
    
    Args:
        page: The Playwright Page object
        selector_with_mmid: The selector string with mmid attribute
        
    Returns:
        XPath selector string if elements found, None if no elements found
    """
    generator = get_selector_generator()
    return await generator.parse(page, selector_with_mmid)





# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from playwright.async_api import async_playwright
    
    async def test_selector_generator():
        generator = SelectorGenerator()
        
        # Test cases with mmid selectors
        test_selectors = [
            "[mmid='114']",  # mmid selector
            "[mmid='submit-button']",  # mmid selector
            "[mmid='form-group']",  # mmid selector
            "[mmid='username-input']",  # mmid selector
            "[mmid='login-form']",  # mmid selector
            "[mmid='forgot-link']",  # mmid selector
            "[mmid='logo']",  # mmid selector
        ]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_content("""
                <html>
                    <body>
                        <div mmid="114" id="unique-div" class="container">Test Element 1</div>
                        <button mmid="submit-button" id="submit-btn" class="btn btn-primary" type="submit">Submit</button>
                        <div mmid="form-group" class="form-group" name="user-form">
                            <input mmid="username-input" id="username" class="form-control" name="username" type="text" placeholder="Enter username">
                        </div>
                        <form mmid="login-form" id="login-form" class="login-form" action="/login" method="post">
                            <input type="email" name="email" class="form-control">
                            <input type="password" name="password" class="form-control">
                        </form>
                        <a mmid="forgot-link" href="/forgot-password" class="forgot-link">Forgot Password?</a>
                        <img mmid="logo" src="/logo.png" alt="Company Logo" class="logo">
                    </body>
                </html>
            """)
            
            print("=== Selector Generator Test Results ===")
            for selector in test_selectors:
                try:
                    xpath = await generator.parse(page, selector)
                    print(f"\nOriginal: {selector}")
                    print(f"Generated XPath: {xpath}")
                except Exception as e:
                    print(f"\nError generating XPath for '{selector}': {e}")
            
            await browser.close()
    
    # Run the test
    asyncio.run(test_selector_generator())
