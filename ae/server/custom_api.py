import asyncio
import json
import logging
import os
import uuid
from queue import Empty
from queue import Queue
from typing import Any

import uvicorn

from playwright.sync_api import sync_playwright
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pydantic import Field

import ae.core.playwright_manager as browserManager
from ae.config import SOURCE_LOG_FOLDER_PATH
from ae.core.agents_llm_config import AgentsLLMConfig
from ae.core.autogen_wrapper import AutogenWrapper
from ae.utils.formatting_helper import is_terminating_message
from ae.utils.ui_messagetype import MessageType
from ae.core.skills.playwright_actions.playwright_action_history import get_playwright_action_history

browser_manager = browserManager.PlaywrightManager(headless=False)

APP_VERSION = "1.0.0"
APP_NAME = "Agent-E Web API"
API_PREFIX = "/api"
IS_DEBUG = False
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8080))
WORKERS = 1

container_id = os.getenv("CONTAINER_ID", "")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("uvicorn")


class CommandQueryModel(BaseModel):
    command: str = Field(..., description="The command related to web navigation to execute.")  # Required field with description
    page_url: str = Field(..., description="The page url related to web navigation to execute the command on.")  # Required field with description  
    llm_config: dict[str,Any] | None = Field(None, description="The LLM configuration string to use for the agents.")
    planner_max_chat_round: int = Field(50, description="The maximum number of chat rounds for the planner.")
    browser_nav_max_chat_round: int = Field(10, description="The maximum number of chat rounds for the browser navigation agent.")
    clientid: str | None = Field(None, description="Client identifier, optional")
    request_originator: str | None = Field(None, description="Optional id of the request originator")


def get_app() -> FastAPI:
    """Starts the Application"""
    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)

    fast_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    return fast_app


app = get_app()


@app.on_event("startup")  # type: ignore
async def startup_event():
    """
    Startup event handler to initialize browser manager asynchronously.
    """
    global container_id

    if container_id.strip() == "":
        container_id = str(uuid.uuid4())
        os.environ["CONTAINER_ID"] = container_id
    await browser_manager.async_initialize()

@app.post("/execute_task", description="Execute a given command related to web navigation and return the result.")
async def execute_task(request: Request, query_model: CommandQueryModel):
    notification_queue = Queue()  # type: ignore
    transaction_id = str(uuid.uuid4()) if query_model.clientid is None else query_model.clientid

    return JSONResponse(await run_task(request, transaction_id, query_model.command, query_model.page_url, notification_queue, query_model.request_originator,query_model.llm_config,
                                      planner_max_chat_round=query_model.planner_max_chat_round,
                                      browser_nav_max_chat_round=query_model.browser_nav_max_chat_round))


async def run_task(request: Request, transaction_id: str, command: str, page_url: str, notification_queue: Queue, request_originator: str|None = None, llm_config: dict[str,Any]|None = None,   # type: ignore
             planner_max_chat_round: int = 50, browser_nav_max_chat_round: int = 10):
    return await process_command(command, page_url, planner_max_chat_round, browser_nav_max_chat_round, llm_config)



async def process_command(command: str, page_url: str, planner_max_chat_round: int, browser_nav_max_chat_round: int, llm_config:dict[str,Any]|None = None):
    # Load the configuration using AgentsLLMConfig

    await browser_manager.goto(page_url)
    
    normalized_llm_config = None
    if llm_config is None:
        normalized_llm_config = AgentsLLMConfig()
    else:
        normalized_llm_config = AgentsLLMConfig(llm_config=llm_config)
        logger.info("Applied LLM config received via API.")

    # Retrieve planner agent and browser nav agent configurations
    planner_agent_config = normalized_llm_config.get_planner_agent_config()
    browser_nav_agent_config = normalized_llm_config.get_browser_nav_agent_config()

    ag = await AutogenWrapper.create(planner_agent_config, browser_nav_agent_config, planner_max_chat_round=planner_max_chat_round,
                                     browser_nav_max_chat_round=browser_nav_max_chat_round)
    result = await ag.process_command(command, page_url)  # type: ignore

    print(f"Result of command execution: {result}")
    get_playwright_action_history().get_recent_actions(15)

    return result.chat_history

if __name__ == "__main__":
    logger.info("**********Application Started**********")
    uvicorn.run("main:app", host=HOST, port=PORT, workers=WORKERS, reload=IS_DEBUG, log_level="info")
 