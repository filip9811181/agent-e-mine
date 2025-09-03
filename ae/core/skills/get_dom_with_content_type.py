import os
import time
import json
import tempfile
from typing import Annotated
from typing import Any

from playwright.async_api import Page

from ae.config import SOURCE_LOG_FOLDER_PATH
from ae.core.playwright_manager import PlaywrightManager
from ae.utils.dom_helper import wait_for_non_loading_dom_state
from ae.utils.get_detailed_accessibility_tree import do_get_accessibility_info
from ae.utils.logger import logger
from ae.utils.ui_messagetype import MessageType


async def get_dom_with_content_type(
    content_type: Annotated[str, "The type of content to extract: 'text_only': Extracts the innerText of the highest element in the document and responds with text, or 'input_fields': Extracts the text input and button elements in the dom."],
    as_file_attachment: Annotated[bool, "Whether to return the result as a file attachment for OpenAI API"] = False
    ) -> Annotated[dict[str, Any] | str | None, "The output based on the specified content type or file attachment info."]:
    """
    Retrieves and processes the DOM of the active page in a browser instance based on the specified content type.

    Parameters
    ----------
    content_type : str
        The type of content to extract. Possible values are:
        - 'text_only': Extracts the innerText of the highest element in the document and responds with text.
        - 'input_fields': Extracts the text input and button elements in the DOM and responds with a JSON object.
        - 'all_fields': Extracts all the fields in the DOM and responds with a JSON object.
    as_file_attachment : boolget_dom_with_content_type
        Whether to save the content as a file and return file attachment information for OpenAI API.

    Returns
    -------
    dict[str, Any] | str | None
        The processed content based on the specified content type. When as_file_attachment is True,
        returns a dict with file information for OpenAI API attachments.

    Raises
    ------
    ValueError
        If an unsupported content_type is provided.
    """

    logger.info(f"Executing Get DOM Command based on content_type: {content_type}")
    start_time = time.time()
    # Create and use the PlaywrightManager
    browser_manager = PlaywrightManager(browser_type='chromium', headless=False)
    page = await browser_manager.get_current_page()
    if page is None: # type: ignore
        raise ValueError('No active page found. OpenURL command opens a new page.')

    extracted_data = None
    await wait_for_non_loading_dom_state(page, 2000) # wait for the DOM to be ready, non loading means external resources do not need to be loaded
    user_success_message = ""
    if content_type == 'all_fields':
        user_success_message = "Fetched all the fields in the DOM"
        extracted_data = await do_get_accessibility_info(page, only_input_fields=False)
    elif content_type == 'input_fields':
        logger.debug('Fetching DOM for input_fields')
        extracted_data = await do_get_accessibility_info(page, only_input_fields=True)
        if extracted_data is None:
            return "Could not fetch input fields. Please consider trying with content_type all_fields."
        user_success_message = "Fetched only input fields in the DOM"
    elif content_type == 'text_only':
        # Extract text from the body or the highest-level element
        logger.debug('Fetching DOM for text_only')
        text_content = await get_filtered_text_content(page)
        with open(os.path.join(SOURCE_LOG_FOLDER_PATH, 'text_only_dom.txt'), 'w',  encoding='utf-8') as f:
            f.write(text_content)
        extracted_data = text_content
        user_success_message = "Fetched the text content of the DOM"
    else:
        raise ValueError(f"Unsupported content_type: {content_type}")

    elapsed_time = time.time() - start_time
    logger.info(f"Get DOM Command executed in {elapsed_time} seconds")
    await browser_manager.notify_user(user_success_message, message_type=MessageType.ACTION)
    
    # If file attachment is requested, save content and return file info
    if as_file_attachment:
        return await save_content_as_file_attachment(extracted_data, content_type)
    
    return extracted_data # type: ignore


async def get_filtered_text_content(page: Page) -> str:
    text_content = await page.evaluate("""
        () => {
            // Array of query selectors to filter out
            const selectorsToFilter = ['#agente-overlay'];

            // Store the original visibility values to revert later
            const originalStyles = [];

            // Hide the elements matching the query selectors
            selectorsToFilter.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(element => {
                    originalStyles.push({ element: element, originalStyle: element.style.visibility });
                    element.style.visibility = 'hidden';
                });
            });

            // Get the text content of the page
            let textContent = document?.body?.innerText || document?.documentElement?.innerText || "";

            // Get all the alt text from images on the page
            let altTexts = Array.from(document.querySelectorAll('img')).map(img => img.alt);
            altTexts="Other Alt Texts in the page: " + altTexts.join(' ');

            // Revert the visibility changes
            originalStyles.forEach(entry => {
                entry.element.style.visibility = entry.originalStyle;
            });
            textContent=textContent+" "+altTexts;
            return textContent;
        }
    """)
    return text_content


async def upload_file_to_openai(file_path: str) -> dict[str, Any] | None:
    """
    Uploads a file to OpenAI API and returns the file information.
    
    Parameters
    ----------
    file_path : str
        Path to the file to upload
        
    Returns
    -------
    dict[str, Any] | None
        Dictionary containing OpenAI file information or None if upload fails
    """
    try:
        # Check if OpenAI API key is available
        import os
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables. Cannot upload to OpenAI.")
            return None
            
        # Import OpenAI library
        try:
            from openai import AsyncOpenAI
        except ImportError:
            logger.error("OpenAI library not installed. Cannot upload file to OpenAI.")
            return None
            
        # Initialize OpenAI client
        client = AsyncOpenAI(api_key=api_key)
        
        # Upload file to OpenAI
        with open(file_path, 'rb') as file:
            response = await client.files.create(
                file=file,
                purpose='assistants'
            )
            
        logger.info(f"Successfully uploaded file to OpenAI with ID: {response.id}")
        
        return {
            "file_id": response.id,
            "filename": response.filename,
            "bytes": response.bytes,
            "created_at": response.created_at,
            "purpose": response.purpose,
            "status": response.status
        }
        
    except Exception as e:
        logger.error(f"Error uploading file to OpenAI: {e}")
        return None


async def save_content_as_file_attachment(content: Any, content_type: str) -> dict[str, Any]:
    """
    Saves the content as a file and returns information for OpenAI file attachment.
    
    Parameters
    ----------
    content : Any
        The content to save (string, dict, etc.)
    content_type : str
        The type of content ('text_only', 'input_fields', 'all_fields')
        
    Returns
    -------
    dict[str, Any]
        Dictionary containing file information for OpenAI API attachments
    """
    try:
        # Determine file extension and format based on content type
        if content_type == 'text_only':
            file_extension = '.txt'
            file_content = str(content) if content else ""
        elif content_type in ['input_fields', 'all_fields']:
            file_extension = '.json'
            file_content = json.dumps(content, indent=2, ensure_ascii=False) if content else "{}"
        else:
            file_extension = '.txt'
            file_content = str(content) if content else ""
        
        # Create a temporary file with appropriate extension
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix=file_extension, 
            prefix=f'dom_{content_type}_',
            delete=False,
            encoding='utf-8'
        )
        
        with temp_file as f:
            f.write(file_content)
            temp_file_path = f.name
        
        logger.info(f"Saved DOM content to temporary file: {temp_file_path}")
        
        # Try to upload to OpenAI
        openai_file_info = await upload_file_to_openai(temp_file_path)
        
        # Return file attachment information in OpenAI format
        result = {
            "type": "file_attachment",
            "file_path": temp_file_path,
            "content_type": content_type,
            "file_size": len(file_content.encode('utf-8')),
            "message": f"DOM content ({content_type}) saved as file attachment"
        }
        
        if openai_file_info:
            # Include OpenAI file information
            result["openai_file"] = openai_file_info
            result["openai_format"] = {
                "content": [
                    {
                        "type": "text",
                        "text": f"DOM content ({content_type}) has been uploaded to OpenAI as file attachment."
                    },
                    {
                        "type": "file",
                        "file_id": openai_file_info["file_id"]
                    }
                ]
            }
            result["message"] += f" and uploaded to OpenAI with file ID: {openai_file_info['file_id']}"
        else:
            # Fallback to local file information
            result["openai_format"] = {
                "content": [
                    {
                        "type": "text",
                        "text": f"DOM content ({content_type}) has been saved as a local file attachment. File path: {temp_file_path}"
                    },
                    {
                        "type": "file",
                        "file_path": temp_file_path
                    }
                ]
            }
            result["message"] += " (OpenAI upload failed - using local file)"
        
        return result
        
    except Exception as e:
        logger.error(f"Error saving content as file attachment: {e}")
        return {
            "type": "error",
            "message": f"Failed to save content as file attachment: {str(e)}",
            "original_content": content
        }

