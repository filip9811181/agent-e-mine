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
        Generate XPath selector for a given element.
        
        Args:
            page: The Playwright Page object
            element: The element to generate XPath for
            
        Returns:
            XPath selector string
        """
        try:
            # Use Playwright's built-in XPath generation
            xpath = await page.evaluate("""
                (element) => {
                    function getXPath(element) {
                        if (element.id !== '') {
                            return 'id("' + element.id + '")';
                        }
                        if (element === document.body) {
                            return element.tagName;
                        }
                        
                        var ix = 0;
                        var siblings = element.parentNode.childNodes;
                        for (var i = 0; i < siblings.length; i++) {
                            var sibling = siblings[i];
                            if (sibling === element) {
                                return getXPath(element.parentNode) + '/' + element.tagName + '[' + (ix + 1) + ']';
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
            # Fallback: try to generate a simple XPath based on tag and attributes
            try:
                tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                element_id = await element.evaluate('el => el.id')
                element_class = await element.evaluate('el => el.className')
                
                if element_id:
                    return f'//{tag_name}[@id="{element_id}"]'
                elif element_class:
                    # Take the first class if multiple classes exist
                    first_class = element_class.split()[0] if element_class else ''
                    if first_class:
                        return f'//{tag_name}[@class="{first_class}"]'
                
                return f'//{tag_name}'
                
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
