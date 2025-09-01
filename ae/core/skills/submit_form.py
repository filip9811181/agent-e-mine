import asyncio
import inspect
import traceback
from typing import Annotated

from playwright.async_api import ElementHandle
from playwright.async_api import Page

from ae.core.playwright_manager import PlaywrightManager
from ae.utils.dom_helper import get_element_outer_html
from ae.utils.dom_mutation_observer import subscribe  # type: ignore
from ae.utils.dom_mutation_observer import unsubscribe  # type: ignore
from ae.utils.logger import logger
from ae.utils.ui_messagetype import MessageType


async def submit_form(
    selector: Annotated[str, "The mmid-based query selector string to identify either the form element or a submit button within the form (e.g. [mmid='114']). When \"mmid\" attribute is present, use it for the query selector."],
    wait_before_execution: Annotated[float, "Optional wait time in seconds before executing the form submission logic.", float] = 0.0
) -> Annotated[str, "A message indicating success or failure of the form submission."]:
    """
    Submits a form by either clicking a submit button or directly triggering the form's submit event.
    Works with form elements or submit buttons identified by their mmid selector.
    
    Parameters:
    - selector: The query selector string to identify either the form or submit button element.
    - wait_before_execution: Optional wait time in seconds before executing the submission logic.
    
    Returns:
    - Success message if form submission was successful, or appropriate error message otherwise.
    """
    logger.info(f"Executing submit_form with \"{selector}\" as the selector")

    # Initialize PlaywrightManager and get the active browser page
    browser_manager = PlaywrightManager(browser_type='chromium', headless=False)
    page = await browser_manager.get_current_page()

    if page is None:  # type: ignore
        raise ValueError('No active page found. OpenURL command opens a new page.')

    function_name = inspect.currentframe().f_code.co_name  # type: ignore

    await browser_manager.take_screenshots(f"{function_name}_start", page)
    await browser_manager.highlight_element(selector, True)

    dom_changes_detected: str | None = None
    
    def detect_dom_changes(changes: str):  # type: ignore
        nonlocal dom_changes_detected
        dom_changes_detected = changes  # type: ignore

    subscribe(detect_dom_changes)
    result = await do_submit_form(page, selector, wait_before_execution)
    await asyncio.sleep(0.1)  # sleep for 100ms to allow the mutation observer to detect changes
    unsubscribe(detect_dom_changes)
    await browser_manager.take_screenshots(f"{function_name}_end", page)
    await browser_manager.notify_user(result["summary_message"], message_type=MessageType.ACTION)

    if dom_changes_detected:
        return f"Success: {result['summary_message']}.\n As a consequence of this action, new elements have appeared in view: {dom_changes_detected}. This means that the form submission triggered page changes. Get all_fields DOM to see the updated page content."
    return result["detailed_message"]


async def do_submit_form(page: Page, selector: str, wait_before_execution: float) -> dict[str, str]:
    """
    Executes the form submission action on the element with the given selector.

    Parameters:
    - page: The Playwright page instance.
    - selector: The query selector string to identify the form or submit button element.
    - wait_before_execution: Optional wait time in seconds before executing the submission logic.

    Returns:
    dict[str,str] - Explanation of the outcome of this operation represented as a dictionary with 'summary_message' and 'detailed_message'.
    """
    logger.info(f"Executing submit_form with \"{selector}\" as the selector. Wait time before execution: {wait_before_execution} seconds.")

    # Wait before execution if specified
    if wait_before_execution > 0:
        await asyncio.sleep(wait_before_execution)

    try:
        logger.info(f"Executing submit_form with \"{selector}\" as the selector. Waiting for the element to be attached and visible.")

        element = await asyncio.wait_for(
            page.wait_for_selector(selector, state="attached", timeout=2000),
            timeout=2000
        )
        if element is None:
            raise ValueError(f"Element with selector: \"{selector}\" not found")

        logger.info(f"Element with selector: \"{selector}\" is attached. Scrolling it into view if needed.")
        try:
            await element.scroll_into_view_if_needed(timeout=200)
            logger.info(f"Element with selector: \"{selector}\" is attached and scrolled into view. Waiting for the element to be visible.")
        except Exception:
            # If scrollIntoView fails, just move on, not a big deal
            pass

        try:
            await element.wait_for_element_state("visible", timeout=200)
            logger.info(f"Executing submit_form with \"{selector}\" as the selector. Element is attached and visible. Submitting the form.")
        except Exception:
            # If the element is not visible, try to submit it anyway
            pass

        element_tag_name = await element.evaluate("element => element.tagName.toLowerCase()")
        element_outer_html = await get_element_outer_html(element, page, element_tag_name)

        # Handle different types of form submission
        if element_tag_name == "form":
            # Direct form submission
            msg = await submit_form_element(page, selector, element)
            return {
                "summary_message": msg,
                "detailed_message": f"{msg} The submitted form's outer HTML is: {element_outer_html}."
            }
        elif element_tag_name in ["button", "input"]:
            # Check if it's a submit button
            element_type = await element.get_attribute("type")
            if element_type == "submit" or element_tag_name == "button":
                # Click the submit button
                msg = await perform_submit_button_click(page, selector)
                return {
                    "summary_message": msg,
                    "detailed_message": f"{msg} The clicked submit element's outer HTML is: {element_outer_html}."
                }
            else:
                # Try to find the parent form and submit it
                msg = await submit_parent_form(page, element)
                return {
                    "summary_message": msg,
                    "detailed_message": f"{msg} The element's outer HTML is: {element_outer_html}."
                }
        else:
            # For other elements, try to find the parent form
            msg = await submit_parent_form(page, element)
            return {
                "summary_message": msg,
                "detailed_message": f"{msg} The element's outer HTML is: {element_outer_html}."
            }

    except Exception as e:
        logger.error(f"Unable to submit form with selector: \"{selector}\". Error: {e}")
        traceback.print_exc()
        msg = f"Unable to submit form with selector: \"{selector}\" since the selector is invalid or the form submission failed. Proceed by retrieving DOM again."
        return {"summary_message": msg, "detailed_message": f"{msg}. Error: {e}"}


async def submit_form_element(page: Page, selector: str, form_element: ElementHandle) -> str:
    """
    Submits a form element directly using JavaScript.
    
    Parameters:
    - page: The Playwright page instance.
    - selector: The query selector string of the form element.
    - form_element: The form ElementHandle.
    
    Returns:
    - Success message string.
    """
    js_code = """(selector) => {
        let form = document.querySelector(selector);
        if (!form) {
            return `submit_form: Form element with selector ${selector} not found`;
        }
        if (form.tagName.toLowerCase() !== 'form') {
            return `submit_form: Element with selector ${selector} is not a form`;
        }
        
        try {
            form.submit();
            return `Successfully submitted form with selector: ${selector}`;
        } catch (error) {
            return `Failed to submit form with selector: ${selector}. Error: ${error.message}`;
        }
    }"""
    
    try:
        logger.info(f"Submitting form element with selector: {selector}")
        result: str = await page.evaluate(js_code, selector)
        logger.debug(f"Form submission result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error submitting form element with selector: {selector}. Error: {e}")
        return f"Error submitting form with selector: {selector}. Error: {e}"


async def perform_submit_button_click(page: Page, selector: str) -> str:
    """
    Clicks a submit button using JavaScript.
    
    Parameters:
    - page: The Playwright page instance.
    - selector: The query selector string of the submit button.
    
    Returns:
    - Success message string.
    """
    js_code = """(selector) => {
        let button = document.querySelector(selector);
        if (!button) {
            return `submit_form: Submit button with selector ${selector} not found`;
        }
        
        try {
            button.click();
            return `Successfully clicked submit button with selector: ${selector}`;
        } catch (error) {
            return `Failed to click submit button with selector: ${selector}. Error: ${error.message}`;
        }
    }"""
    
    try:
        logger.info(f"Clicking submit button with selector: {selector}")
        result: str = await page.evaluate(js_code, selector)
        logger.debug(f"Submit button click result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error clicking submit button with selector: {selector}. Error: {e}")
        return f"Error clicking submit button with selector: {selector}. Error: {e}"


async def submit_parent_form(page: Page, element: ElementHandle) -> str:
    """
    Finds the parent form of an element and submits it.
    
    Parameters:
    - page: The Playwright page instance.
    - element: The ElementHandle of the child element.
    
    Returns:
    - Success message string.
    """
    try:
        # Find the parent form using JavaScript
        js_code = """(element) => {
            let current = element;
            while (current && current.parentNode) {
                current = current.parentNode;
                if (current.tagName && current.tagName.toLowerCase() === 'form') {
                    try {
                        current.submit();
                        return 'Successfully submitted parent form';
                    } catch (error) {
                        return `Failed to submit parent form. Error: ${error.message}`;
                    }
                }
            }
            return 'No parent form found for the element';
        }"""
        
        result: str = await element.evaluate(js_code)
        logger.debug(f"Parent form submission result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error finding/submitting parent form. Error: {e}")
        return f"Error finding/submitting parent form. Error: {e}"
