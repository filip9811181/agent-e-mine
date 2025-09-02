import asyncio
import inspect
from this import d
import traceback
from typing import Annotated

from playwright.async_api import Page

from ae.core.playwright_manager import PlaywrightManager
from ae.core.skills.playwright_actions.action_classes import DragAndDropAction, action_to_json
from ae.core.skills.playwright_actions.playwright_action_history import add_playwright_action
from ae.utils.dom_helper import get_element_outer_html
from ae.utils.dom_mutation_observer import subscribe  # type: ignore
from ae.utils.dom_mutation_observer import unsubscribe  # type: ignore
from ae.utils.logger import logger
from ae.utils.ui_messagetype import MessageType


async def drag_and_drop(
    source_selector: Annotated[str, "The selector string to identify the draggable element. Use Playwright's native selectors: xpath, attribute selectors, or text-based selectors (tagContainsSelector)."],
    target_selector: Annotated[str, "The selector string to identify the drop target element. Use Playwright's native selectors: xpath, attribute selectors, or text-based selectors (tagContainsSelector)."],
    wait_before_execution: Annotated[float, "Optional wait time in seconds before executing the drag-and-drop logic.", float] = 0.0,
) -> Annotated[str, "A message indicating success or failure of the drag-and-drop action."]:
    """
    Drags an element identified by the source selector and drops it onto the element
    identified by the target selector on the current page. Use Playwright's native selectors:
    xpath, attribute selectors, or text-based selectors (tagContainsSelector).

    Parameters:
    - source_selector: Selector of the element to drag. Use Playwright's native selectors: xpath, attribute selectors, or text-based selectors (tagContainsSelector).
    - target_selector: Selector of the element to drop onto. Use Playwright's native selectors: xpath, attribute selectors, or text-based selectors (tagContainsSelector).
    - wait_before_execution: Optional wait time in seconds before executing the operation.

    Returns:
    - A human-readable string describing the outcome, containing success or an error with guidance.
    """
    drag_and_drop_action = await DragAndDropAction.from_strings_with_generator(page, source_selector, target_selector)
    if drag_and_drop_action:
        add_playwright_action(drag_and_drop_action)
        logger.info(f"Added drag and drop action to history: {action_to_json(drag_and_drop_action)}")
    else:
        logger.warning(f"Could not create drag and drop action for selectors: {source_selector}, {target_selector}")
        
    logger.info(f"Executing drag_and_drop from '{source_selector}' to '{target_selector}'")

    browser_manager = PlaywrightManager(browser_type='chromium', headless=False)
    page = await browser_manager.get_current_page()
    if page is None:  # type: ignore
        raise ValueError('No active page found. OpenURL command opens a new page.')

    function_name = inspect.currentframe().f_code.co_name  # type: ignore

    await browser_manager.take_screenshots(f"{function_name}_start", page)
    await browser_manager.highlight_element(source_selector, True)
    await browser_manager.highlight_element(target_selector, True)

    dom_changes_detected: str | None = None

    def detect_dom_changes(changes: str):  # type: ignore
        nonlocal dom_changes_detected
        dom_changes_detected = changes  # type: ignore

    subscribe(detect_dom_changes)
    result = await do_drag_and_drop(page, source_selector, target_selector, wait_before_execution)
    await asyncio.sleep(0.1)
    unsubscribe(detect_dom_changes)
    await browser_manager.take_screenshots(f"{function_name}_end", page)
    await browser_manager.notify_user(result["summary_message"], message_type=MessageType.ACTION)

    if dom_changes_detected:
        return (
            f"Success: {result['summary_message']}.\n"
            f"As a consequence of this action, new elements have appeared in view: {dom_changes_detected}. "
            f"Get all_fields DOM to continue the interaction if needed."
        )
    return result["detailed_message"]


async def do_drag_and_drop(
    page: Page,
    source_selector: str,
    target_selector: str,
    wait_before_execution: float,
) -> dict[str, str]:
    """
    Perform the drag-and-drop using Playwright's native API with a JavaScript fallback.
    Supports Playwright's native selectors: xpath, attribute selectors, or text-based selectors (tagContainsSelector).

    Returns a dict with 'summary_message' and 'detailed_message'.
    """
    logger.info(
        f"Performing drag_and_drop from '{source_selector}' to '{target_selector}'. "
        f"Wait time before execution: {wait_before_execution} seconds."
    )

    if wait_before_execution > 0:
        await asyncio.sleep(wait_before_execution)

    try:
        # Ensure both elements exist and are attached
        source = await asyncio.wait_for(
            page.wait_for_selector(source_selector, state="attached", timeout=2000),
            timeout=2000,
        )
        target = await asyncio.wait_for(
            page.wait_for_selector(target_selector, state="attached", timeout=2000),
            timeout=2000,
        )
        if source is None or target is None:
            raise ValueError(
                f"Element not found: source={source_selector if source else 'None'}, target={target_selector if target else 'None'}"
            )

        # Scroll into view if needed (best-effort)
        try:
            await source.scroll_into_view_if_needed(timeout=200)
        except Exception:
            pass
        try:
            await target.scroll_into_view_if_needed(timeout=200)
        except Exception:
            pass

        # Gather outer HTML for detailed reporting
        try:
            source_tag = await source.evaluate("el => el.tagName.toLowerCase()")
            target_tag = await target.evaluate("el => el.tagName.toLowerCase()")
            source_outer_html = await get_element_outer_html(source, page, source_tag)
            target_outer_html = await get_element_outer_html(target, page, target_tag)
        except Exception:
            source_outer_html = "<unavailable>"
            target_outer_html = "<unavailable>"

        # First attempt: Playwright native drag_to via locators
        try:
            source_locator = page.locator(source_selector)
            target_locator = page.locator(target_selector)
            await source_locator.drag_to(target_locator, timeout=800)
            msg = (
                f"Dragged element '{source_selector}' and dropped onto '{target_selector}' using Playwright drag_to."
            )
            return {
                "summary_message": msg,
                "detailed_message": f"{msg} Source outer HTML: {source_outer_html}. Target outer HTML: {target_outer_html}.",
            }
        except Exception as drag_err:
            logger.warning(
                f"Playwright drag_to failed for source='{source_selector}' target='{target_selector}'. Error: {drag_err}"
            )

        # Fallback: JavaScript-based drag and drop
        js_code = """
            (sourceSelector, targetSelector) => {
                const createDt = () => {
                    const dt = new DataTransfer();
                    dt.setData('text/plain', 'drag');
                    return dt;
                };

                const source = document.querySelector(sourceSelector);
                const target = document.querySelector(targetSelector);
                if (!source) return `drag_and_drop: Source element ${sourceSelector} not found`;
                if (!target) return `drag_and_drop: Target element ${targetSelector} not found`;

                const dispatch = (el, type, dt) => {
                    const evt = new DragEvent(type, { bubbles: true, cancelable: true, dataTransfer: dt });
                    return el.dispatchEvent(evt);
                };

                const dt = createDt();
                dispatch(source, 'dragstart', dt);
                dispatch(target, 'dragenter', dt);
                dispatch(target, 'dragover', dt);
                dispatch(target, 'drop', dt);
                dispatch(source, 'dragend', dt);

                return 'Executed JavaScript drag-and-drop from ' + sourceSelector + ' to ' + targetSelector;
            }
        """
        logger.info(
            f"Attempting JavaScript fallback drag-and-drop from '{source_selector}' to '{target_selector}'"
        )
        js_result: str = await page.evaluate(js_code, source_selector, target_selector)
        return {
            "summary_message": js_result,
            "detailed_message": f"{js_result} Source outer HTML: {source_outer_html}. Target outer HTML: {target_outer_html}.",
        }
    except Exception as e:
        logger.error(
            f"Unable to drag_and_drop from '{source_selector}' to '{target_selector}'. Error: {e}"
        )
        traceback.print_exc()
        msg = (
            "Unable to complete drag-and-drop. Verify selectors using GET_DOM_WITH_CONTENT_TYPE(all_fields) "
            "and try again with correct selectors using Playwright's native selectors: xpath, attribute selectors, or text-based selectors (tagContainsSelector)."
        )
        return {
            "summary_message": msg,
            "detailed_message": f"{msg} Error: {e}",
        }


