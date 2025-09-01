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

from ae.utils.logger import logger


@dataclass
class PlaywrightActionRecord:
    """Represents a single Playwright action record in the history."""
    timestamp: str
    action_type: str
    action_data: Dict[str, Any]
    url: str
    title: str
    success: bool
    error_message: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    execution_time_ms: Optional[int] = None
    screenshot_path: Optional[str] = None
    page_state: Optional[str] = None


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
        self.history: List[PlaywrightActionRecord] = []
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
                    self.history = [PlaywrightActionRecord(**record) for record in history_data]
                    logger.info(f"Loaded {len(self.history)} Playwright action records from {self.history_file_path}")
            else:
                logger.info(f"No existing Playwright action history found. Creating new history file at {self.history_file_path}")
        except Exception as e:
            logger.error(f"Error loading Playwright action history: {e}")
            self.history = []
    
    def _save_history(self):
        """Save current history to file."""
        try:
            # Convert PlaywrightActionRecord objects to dictionaries
            history_data = [asdict(record) for record in self.history]
            
            with open(self.history_file_path, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved {len(self.history)} Playwright action records to {self.history_file_path}")
        except Exception as e:
            logger.error(f"Error saving Playwright action history: {e}")
    
    def add_action(self, action_type: str, action_data: Dict[str, Any], url: str, 
                   title: str, success: bool, error_message: Optional[str] = None,
                   user_id: Optional[str] = None, execution_time_ms: Optional[int] = None,
                   screenshot_path: Optional[str] = None, page_state: Optional[str] = None) -> PlaywrightActionRecord:
        """
        Add a new Playwright action to the history.
        
        Args:
            action_type: Type of action (e.g., 'navigate', 'click', 'submit', 'type', 'hover')
            action_data: Data associated with the action
            url: Current page URL
            title: Current page title
            success: Whether the action was successful
            error_message: Error message if action failed
            user_id: Optional user identifier
            execution_time_ms: Optional execution time in milliseconds
            screenshot_path: Optional path to screenshot taken during action
            page_state: Optional description of page state after action
            
        Returns:
            The created PlaywrightActionRecord
        """
        record = PlaywrightActionRecord(
            timestamp=datetime.now().isoformat(),
            action_type=action_type,
            action_data=action_data,
            url=url,
            title=title,
            success=success,
            error_message=error_message,
            session_id=self.session_id,
            user_id=user_id,
            execution_time_ms=execution_time_ms,
            screenshot_path=screenshot_path,
            page_state=page_state
        )
        
        self.history.append(record)
        
        # Trim history if it exceeds max size
        if len(self.history) > self.max_history_size:
            self.history = self.history[-self.max_history_size:]
            logger.info(f"Trimmed Playwright action history to {self.max_history_size} records")
        
        # Save to file
        self._save_history()
        
        logger.debug(f"Added Playwright action record: {action_type} at {url}")
        return record
    
    def add_navigation_action(self, url: str, title: str, action_data: Dict[str, Any], 
                             success: bool = True, error_message: Optional[str] = None,
                             execution_time_ms: Optional[int] = None, screenshot_path: Optional[str] = None,
                             user_id: Optional[str] = None) -> PlaywrightActionRecord:
        """Convenience method for adding navigation actions."""
        return self.add_action(
            action_type="navigate",
            action_data=action_data,
            url=url,
            title=title,
            success=success,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
            screenshot_path=screenshot_path,
            user_id=user_id
        )
    
    def add_click_action(self, url: str, title: str, action_data: Dict[str, Any],
                        success: bool = True, error_message: Optional[str] = None,
                        execution_time_ms: Optional[int] = None, screenshot_path: Optional[str] = None,
                        user_id: Optional[str] = None) -> PlaywrightActionRecord:
        """Convenience method for adding click actions."""
        return self.add_action(
            action_type="click",
            action_data=action_data,
            url=url,
            title=title,
            success=success,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
            screenshot_path=screenshot_path,
            user_id=user_id
        )
    
    def add_form_action(self, url: str, title: str, action_data: Dict[str, Any],
                       success: bool = True, error_message: Optional[str] = None,
                       execution_time_ms: Optional[int] = None, screenshot_path: Optional[str] = None,
                       user_id: Optional[str] = None) -> PlaywrightActionRecord:
        """Convenience method for adding form-related actions (submit, type, select)."""
        return self.add_action(
            action_type="form_action",
            action_data=action_data,
            url=url,
            title=title,
            success=success,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
            screenshot_path=screenshot_path,
            user_id=user_id
        )
    
    def get_recent_actions(self, limit: int = 10) -> List[PlaywrightActionRecord]:
        """Get the most recent actions."""
        return self.history[-limit:] if self.history else []
    
    def get_actions_by_type(self, action_type: str) -> List[PlaywrightActionRecord]:
        """Get all actions of a specific type."""
        return [record for record in self.history if record.action_type == action_type]
    
    def get_actions_by_url(self, url: str) -> List[PlaywrightActionRecord]:
        """Get all actions performed on a specific URL."""
        return [record for record in self.history if record.url == url]
    
    def get_session_actions(self, session_id: Optional[str] = None) -> List[PlaywrightActionRecord]:
        """Get all actions from a specific session."""
        target_session = session_id or self.session_id
        return [record for record in self.history if record.session_id == target_session]
    
    def get_user_actions(self, user_id: str) -> List[PlaywrightActionRecord]:
        """Get all actions performed by a specific user."""
        return [record for record in self.history if record.user_id == user_id]
    
    def get_navigation_actions(self, limit: int = 50) -> List[PlaywrightActionRecord]:
        """Get navigation action history."""
        navigation_actions = self.get_actions_by_type('navigate')
        return navigation_actions[-limit:] if navigation_actions else []
    
    def get_click_actions(self, limit: int = 50) -> List[PlaywrightActionRecord]:
        """Get click action history."""
        click_actions = self.get_actions_by_type('click')
        return click_actions[-limit:] if click_actions else []
    
    def get_form_actions(self, limit: int = 50) -> List[PlaywrightActionRecord]:
        """Get form action history."""
        form_actions = self.get_actions_by_type('form_action')
        return form_actions[-limit:] if form_actions else []
    
    def get_failed_actions(self, limit: int = 50) -> List[PlaywrightActionRecord]:
        """Get failed actions for debugging."""
        failed_actions = [record for record in self.history if not record.success]
        return failed_actions[-limit:] if failed_actions else []
    
    def get_slow_actions(self, threshold_ms: int = 5000, limit: int = 50) -> List[PlaywrightActionRecord]:
        """Get actions that took longer than threshold for performance analysis."""
        slow_actions = [record for record in self.history 
                       if record.execution_time_ms and record.execution_time_ms > threshold_ms]
        return sorted(slow_actions, key=lambda x: x.execution_time_ms or 0, reverse=True)[:limit]
    
    def search_actions(self, query: str) -> List[PlaywrightActionRecord]:
        """Search actions by query string in action data or error messages."""
        query_lower = query.lower()
        results = []
        
        for record in self.history:
            # Search in action data
            if any(query_lower in str(value).lower() for value in record.action_data.values()):
                results.append(record)
                continue
            
            # Search in error message
            if record.error_message and query_lower in record.error_message.lower():
                results.append(record)
                continue
            
            # Search in URL or title
            if query_lower in record.url.lower() or query_lower in record.title.lower():
                results.append(record)
        
        return results
    
    def get_action_statistics(self) -> Dict[str, Any]:
        """Get statistics about the action history."""
        if not self.history:
            return {
                "total_actions": 0,
                "successful_actions": 0,
                "failed_actions": 0,
                "action_types": {},
                "sessions": 0,
                "average_execution_time_ms": 0
            }
        
        total_actions = len(self.history)
        successful_actions = sum(1 for record in self.history if record.success)
        failed_actions = total_actions - successful_actions
        
        # Count action types
        action_types = {}
        for record in self.history:
            action_types[record.action_type] = action_types.get(record.action_type, 0) + 1
        
        # Count unique sessions
        unique_sessions = len(set(record.session_id for record in self.history))
        
        # Calculate average execution time
        execution_times = [record.execution_time_ms for record in self.history if record.execution_time_ms]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        return {
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "failed_actions": failed_actions,
            "success_rate": (successful_actions / total_actions) * 100 if total_actions > 0 else 0,
            "action_types": action_types,
            "sessions": unique_sessions,
            "average_execution_time_ms": avg_execution_time,
            "oldest_action": self.history[0].timestamp if self.history else None,
            "newest_action": self.history[-1].timestamp if self.history else None
        }
    
    def clear_history(self):
        """Clear all action history."""
        self.history = []
        self._save_history()
        logger.info("Playwright action history cleared")
    
    def export_history(self, export_path: str, format_type: str = "json", action_types: Optional[List[str]] = None):
        """Export action history to a file."""
        try:
            # Filter by action types if specified
            if action_types:
                export_data = [record for record in self.history if record.action_type in action_types]
            else:
                export_data = self.history
            
            if format_type.lower() == "json":
                with open(export_path, 'w', encoding='utf-8') as f:
                    history_data = [asdict(record) for record in export_data]
                    json.dump(history_data, f, indent=2, ensure_ascii=False)
            
            elif format_type.lower() == "csv":
                import csv
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    if export_data:
                        writer = csv.DictWriter(f, fieldnames=asdict(export_data[0]).keys())
                        writer.writeheader()
                        for record in export_data:
                            writer.writerow(asdict(record))
            
            logger.info(f"Playwright action history exported to {export_path}")
            logger.info(f"Exported {len(export_data)} actions")
            
        except Exception as e:
            logger.error(f"Error exporting Playwright action history: {e}")


# Global Playwright action history instance
_playwright_action_history: Optional[PlaywrightActionHistory] = None


def get_playwright_action_history() -> PlaywrightActionHistory:
    """Get the global Playwright action history instance."""
    global _playwright_action_history
    if _playwright_action_history is None:
        _playwright_action_history = PlaywrightActionHistory()
    return _playwright_action_history


def add_playwright_action(action_type: str, action_data: Dict[str, Any], url: str, 
                         title: str, success: bool, error_message: Optional[str] = None,
                         user_id: Optional[str] = None, execution_time_ms: Optional[int] = None,
                         screenshot_path: Optional[str] = None, page_state: Optional[str] = None) -> PlaywrightActionRecord:
    """
    Convenience function to add a Playwright action to history.
    
    Args:
        action_type: Type of action (e.g., 'navigate', 'click', 'submit')
        action_data: Data associated with the action
        url: Current page URL
        title: Current page title
        success: Whether the action was successful
        error_message: Error message if action failed
        user_id: Optional user identifier
        execution_time_ms: Optional execution time in milliseconds
        screenshot_path: Optional path to screenshot taken during action
        page_state: Optional description of page state after action
        
    Returns:
        The created PlaywrightActionRecord
    """
    history = get_playwright_action_history()
    return history.add_action(
        action_type=action_type,
        action_data=action_data,
        url=url,
        title=title,
        success=success,
        error_message=error_message,
        user_id=user_id,
        execution_time_ms=execution_time_ms,
        screenshot_path=screenshot_path,
        page_state=page_state
    )


def add_navigation_action(url: str, title: str, action_data: Dict[str, Any], 
                         success: bool = True, error_message: Optional[str] = None,
                         execution_time_ms: Optional[int] = None, screenshot_path: Optional[str] = None,
                         user_id: Optional[str] = None) -> PlaywrightActionRecord:
    """Convenience function for navigation actions."""
    return add_playwright_action(
        action_type="navigate",
        action_data=action_data,
        url=url,
        title=title,
        success=success,
        error_message=error_message,
        execution_time_ms=execution_time_ms,
        screenshot_path=screenshot_path,
        user_id=user_id
    )


def add_click_action(url: str, title: str, action_data: Dict[str, Any],
                    success: bool = True, error_message: Optional[str] = None,
                    execution_time_ms: Optional[int] = None, screenshot_path: Optional[str] = None,
                    user_id: Optional[str] = None) -> PlaywrightActionRecord:
    """Convenience function for click actions."""
    return add_playwright_action(
        action_type="click",
        action_data=action_data,
        url=url,
        title=title,
        success=success,
        error_message=error_message,
        execution_time_ms=execution_time_ms,
        screenshot_path=screenshot_path,
        user_id=user_id
    )


def add_form_action(url: str, title: str, action_data: Dict[str, Any],
                   success: bool = True, error_message: Optional[str] = None,
                   execution_time_ms: Optional[int] = None, screenshot_path: Optional[str] = None,
                   user_id: Optional[str] = None) -> PlaywrightActionRecord:
    """Convenience function for form actions."""
    return add_playwright_action(
        action_type="form_action",
        action_data=action_data,
        url=url,
        title=title,
        success=success,
        error_message=error_message,
        execution_time_ms=execution_time_ms,
        screenshot_path=screenshot_path,
        user_id=user_id
    )


# Example usage
if __name__ == "__main__":
    # Create Playwright action history
    history = PlaywrightActionHistory()
    
    # Add some sample actions
    history.add_navigation_action(
        url="https://example.com",
        title="Example Domain",
        action_data={"url": "https://example.com", "timeout": 5, "method": "direct"},
        success=True,
        execution_time_ms=1200
    )
    
    history.add_click_action(
        url="https://example.com",
        title="Example Domain",
        action_data={"selector": "#submit-button", "x": 100, "y": 200},
        success=True,
        execution_time_ms=150
    )
    
    history.add_form_action(
        url="https://example.com/login",
        title="Login Page",
        action_data={"action": "submit", "form_id": "login-form"},
        success=True,
        execution_time_ms=800
    )
    
    # Get statistics
    stats = history.get_action_statistics()
    print("Playwright Action History Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Get recent actions
    recent = history.get_recent_actions(5)
    print(f"\nRecent Actions: {len(recent)}")
    for action in recent:
        print(f"- {action.action_type} at {action.url} ({action.timestamp})")
        if action.execution_time_ms:
            print(f"  Execution time: {action.execution_time_ms}ms")

