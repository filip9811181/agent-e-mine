import asyncio
import inspect
import traceback
from typing import Annotated

from playwright.async_api import Page

from ae.core.playwright_manager import PlaywrightManager
from ae.utils.dom_helper import get_element_outer_html
from ae.utils.dom_mutation_observer import subscribe  # type: ignore
from ae.utils.dom_mutation_observer import unsubscribe  # type: ignore
from ae.utils.logger import logger
from ae.utils.ui_messagetype import MessageType
from ae.core.skills.playwright_actions.playwright_action_history import add_playwright_action
from ae.core.skills.playwright_actions.action_classes import SelectOptionAction, action_to_json


async def select_option(selector: Annotated[str, "The properly formed query selector string to identify the select element (e.g. [mmid='114']). When \"mmid\" attribute is present, use it for the query selector."],
                       value: Annotated[str, "The value attribute of the option to select"],
                       wait_before_execution: Annotated[float, "Optional wait time in seconds before executing the select option logic.", float] = 0.0) -> Annotated[str, "A message indicating success or failure of the option selection."]:
    """
    Selects an option from a dropdown/select element matching the given query selector string within the currently open web page.
    The option is selected by its value attribute.
    If there is no page open, it will raise a ValueError. An optional wait time can be specified before executing the select logic.

    Parameters:
    - selector: The query selector string to identify the select element.
    - value: The value attribute of the option to select.
    - wait_before_execution: Optional wait time in seconds before executing the select option logic. Defaults to 0.0 seconds.

    Returns:
    - Success if the option was selected successfully, appropriate error message otherwise.
    """    
    logger.info(f"Executing SelectOption with \"{selector}\" as the selector and \"{value}\" as the value")

    # Initialize PlaywrightManager and get the active browser page
    browser_manager = PlaywrightManager(browser_type='chromium', headless=False)
    page = await browser_manager.get_current_page()

    if page is None: # type: ignore
        raise ValueError('No active page found. OpenURL command opens a new page.')
        
    select_action = await SelectOptionAction.from_string_with_generator(page, selector, value)
    if select_action:
        add_playwright_action(select_action)
        logger.info(f"Added select option action to history: {action_to_json(select_action)}")
    else:
        logger.warning(f"Could not create select option action for selector: {selector}")

    function_name = inspect.currentframe().f_code.co_name # type: ignore

    await browser_manager.take_screenshots(f"{function_name}_start", page)

    await browser_manager.highlight_element(selector, True)

    dom_changes_detected=None
    def detect_dom_changes(changes:str): # type: ignore
        nonlocal dom_changes_detected
        dom_changes_detected = changes # type: ignore

    subscribe(detect_dom_changes)
    result = await do_select_option(page, selector, value, wait_before_execution)
    await asyncio.sleep(0.1) # sleep for 100ms to allow the mutation observer to detect changes
    unsubscribe(detect_dom_changes)
    await browser_manager.take_screenshots(f"{function_name}_end", page)
    await browser_manager.notify_user(result["summary_message"], message_type=MessageType.ACTION)

    if dom_changes_detected:
        return f"Success: {result['summary_message']}.\n As a consequence of this action, new elements have appeared in view: {dom_changes_detected}. This means that the action to select option {value} from {selector} is not yet executed and needs further interaction. Get all_fields DOM to complete the interaction."
    return result["detailed_message"]


async def do_select_option(page: Page, selector: str, value: str, wait_before_execution: float) -> dict[str, str]:
    """
    Executes the select option action on the element with the given selector within the provided page.

    Parameters:
    - page: The Playwright page instance.
    - selector: The query selector string to identify the select element.
    - value: The value attribute of the option to select.
    - wait_before_execution: Optional wait time in seconds before executing the select option logic.

    Returns:
    dict[str,str] - Explanation of the outcome of this operation represented as a dictionary with 'summary_message' and 'detailed_message'.
    """
    logger.info(f"Executing SelectOption with \"{selector}\" as the selector and \"{value}\" as the value. Wait time before execution: {wait_before_execution} seconds.")

    # Wait before execution if specified
    if wait_before_execution > 0:
        await asyncio.sleep(wait_before_execution)

    # Wait for the selector to be present and ensure it's attached and visible
    try:
        logger.info(f"Executing SelectOption with \"{selector}\" as the selector. Waiting for the element to be attached and visible.")

        element = await asyncio.wait_for(
            page.wait_for_selector(selector, state="attached", timeout=2000),
            timeout=2000
        )
        if element is None:
            raise ValueError(f"Select element with selector: \"{selector}\" not found")

        logger.info(f"Select element with selector: \"{selector}\" is attached. Scrolling it into view if needed.")
        try:
            await element.scroll_into_view_if_needed(timeout=200)
            logger.info(f"Select element with selector: \"{selector}\" is attached and scrolled into view. Waiting for the element to be visible.")
        except Exception:
            # If scrollIntoView fails, just move on, not a big deal
            pass

        try:
            await element.wait_for_element_state("visible", timeout=200)
            logger.info(f"Executing SelectOption with \"{selector}\" as the selector. Element is attached and visible. Selecting the option.")
        except Exception:
            # If the element is not visible, try to select it anyway
            pass

        element_tag_name = await element.evaluate("element => element.tagName.toLowerCase()")
        element_outer_html = await get_element_outer_html(element, page, element_tag_name)

        if element_tag_name != "select":
            raise ValueError(f"Element with selector: \"{selector}\" is not a select element. Found: {element_tag_name}")

        # Select the option by value
        await element.select_option(value=value)

        logger.info(f'Select menu option with value "{value}" selected')

        return {"summary_message": f'Select menu option with value "{value}" selected',
                "detailed_message": f'Select menu option with value "{value}" selected. The select element\'s outer HTML is: {element_outer_html}.'}

    except Exception as e:
        logger.error(f"Unable to select option with value \"{value}\" from element with selector: \"{selector}\". Error: {e}")
        traceback.print_exc()
        msg = f"Unable to select option with value \"{value}\" from element with selector: \"{selector}\" since the selector is invalid or the value doesn't exist. Proceed by retrieving DOM again."
        return {"summary_message": msg, "detailed_message": f"{msg}. Error: {e}"}
