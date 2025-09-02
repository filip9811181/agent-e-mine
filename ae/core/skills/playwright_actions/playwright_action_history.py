"""
Playwright Action History Module

This module provides functionality to save and retrieve action history for Playwright automation.
It tracks all types of browser actions including navigation, clicks, form submissions, etc.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path

from ae.core.skills.playwright_actions.action_classes import Action
from ae.utils.logger import logger




class PlaywrightActionHistory:
    """Manages Playwright action history storage and retrieval."""
    
    def __init__(self, history_file_path: Optional[str] = None, max_history_size: int = 2000):
        """
        Initialize the PlaywrightActionHistory.
        
        Args:
            history_file_path: Path to the history file. If None, uses default location.
            max_history_size: Maximum number of actions to keep in history.
        """
        if history_file_path is None:
            # Default to logs directory
            from ae.config import LOG_FILES_PATH
            history_file_path = os.path.join(LOG_FILES_PATH, "playwright_action_history.json")
        
        self.history_file_path = Path(history_file_path)
        self.max_history_size = max_history_size
        self.history: List[Action] = []
        self.session_id = self._generate_session_id()
        
        # Ensure directory exists
        self.history_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing history
        self._load_history()
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return f"playwright_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _load_history(self):
        """Load existing history from file."""
        try:
            if self.history_file_path.exists():
                with open(self.history_file_path, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                    # Convert dictionary data back to Action objects using ActionFactory
                    from ae.core.skills.playwright_actions.action_classes import ActionFactory
                    self.history = []
                    for record in history_data:
                        try:
                            action = ActionFactory.from_dict(record)
                            if action:
                                self.history.append(action)
                        except Exception as e:
                            logger.warning(f"Failed to load action from history: {e}")
                    logger.info(f"Loaded {len(self.history)} Playwright actions from {self.history_file_path}")
            else:
                logger.info(f"No existing Playwright action history found. Creating new history file at {self.history_file_path}")
        except Exception as e:
            logger.error(f"Error loading Playwright action history: {e}")
            self.history = []
    
    def _save_history(self):
        """Save current history to file."""
        try:
            # Convert Action objects to dictionaries
            history_data = [action.to_dict() for action in self.history]
            
            with open(self.history_file_path, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved {len(self.history)} Playwright actions to {self.history_file_path}")
        except Exception as e:
            logger.error(f"Error saving Playwright action history: {e}")
    
    def add_action(self, action: Action) -> Action:
        """
        Add a new Playwright action to the history.
        
        Args:
            action: The Action object to add to history
            
        Returns:
            The added Action object
        """
        self.history.append(action)
        
        # Trim history if it exceeds max size
        if len(self.history) > self.max_history_size:
            self.history = self.history[-self.max_history_size:]
            logger.info(f"Trimmed Playwright action history to {self.max_history_size} records")
        
        # Save to file
        self._save_history()
        
        action_type = action.type.value if hasattr(action.type, 'value') else str(action.type)
        logger.debug(f"Added Playwright action: {action_type}")
        return action
    
    def clear_history(self):
        """Clear all action history."""
        self.history = []
        self._save_history()
        logger.info("Playwright action history cleared")
    



# Global Playwright action history instance
_playwright_action_history: Optional[PlaywrightActionHistory] = None


def get_playwright_action_history() -> PlaywrightActionHistory:
    """Get the global Playwright action history instance."""
    global _playwright_action_history
    if _playwright_action_history is None:
        _playwright_action_history = PlaywrightActionHistory()
    return _playwright_action_history


def add_playwright_action(action: Action) -> Action:
    """
    Convenience function to add a Playwright action to history.
    
    Args:
        action: The Action object to add to history
        
    Returns:
        The added Action object
    """
    history = get_playwright_action_history()
    return history.add_action(action)