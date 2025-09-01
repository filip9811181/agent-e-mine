"""
Playwright Action History Utilities

Utility functions for retrieving and analyzing Playwright action history data.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from ae.core.skills.playwright_action_history import get_playwright_action_history, PlaywrightActionRecord


def print_playwright_action_summary(limit: int = 20):
    """Print a summary of recent Playwright actions."""
    history = get_playwright_action_history()
    recent_actions = history.get_recent_actions(limit)
    
    if not recent_actions:
        print("No Playwright actions found in history.")
        return
    
    print(f"\n=== Playwright Action Summary (Last {len(recent_actions)} actions) ===")
    print(f"{'Timestamp':<25} {'Type':<15} {'URL':<40} {'Status':<10} {'Time(ms)':<10}")
    print("-" * 110)
    
    for action in recent_actions:
        timestamp = action.timestamp[:19]  # Truncate to seconds
        action_type = action.action_type[:14] + "..." if len(action.action_type) > 15 else action.action_type
        url = action.url[:37] + "..." if len(action.url) > 40 else action.url
        status = "✅" if action.success else "❌"
        execution_time = f"{action.execution_time_ms}ms" if action.execution_time_ms else "N/A"
        
        print(f"{timestamp:<25} {action_type:<15} {url:<40} {status:<10} {execution_time:<10}")
    
    # Print statistics
    stats = history.get_action_statistics()
    print(f"\nTotal Actions: {stats['total_actions']}")
    print(f"Success Rate: {stats['success_rate']:.1f}%")
    print(f"Average Execution Time: {stats['average_execution_time_ms']:.0f}ms")
    
    # Print action type breakdown
    print(f"\nAction Type Breakdown:")
    for action_type, count in stats['action_types'].items():
        print(f"  {action_type}: {count}")


def print_navigation_summary(limit: int = 20):
    """Print a summary of recent navigation actions."""
    history = get_playwright_action_history()
    navigation_actions = history.get_navigation_actions(limit)
    
    if not navigation_actions:
        print("No navigation actions found in history.")
        return
    
    print(f"\n=== Navigation Action Summary (Last {len(navigation_actions)} actions) ===")
    print(f"{'Timestamp':<25} {'URL':<50} {'Title':<30} {'Status':<10} {'Time(ms)':<10}")
    print("-" * 130)
    
    for action in navigation_actions:
        timestamp = action.timestamp[:19]  # Truncate to seconds
        url = action.url[:47] + "..." if len(action.url) > 50 else action.url
        title = action.title[:27] + "..." if len(action.title) > 30 else action.title
        status = "✅" if action.success else "❌"
        execution_time = f"{action.execution_time_ms}ms" if action.execution_time_ms else "N/A"
        
        print(f"{timestamp:<25} {url:<50} {title:<30} {status:<10} {execution_time:<10}")
    
    # Print navigation statistics
    nav_stats = {
        "total": len(navigation_actions),
        "successful": len([a for a in navigation_actions if a.success]),
        "failed": len([a for a in navigation_actions if not a.success])
    }
    
    if nav_stats["total"] > 0:
        success_rate = (nav_stats["successful"] / nav_stats["total"]) * 100
        print(f"\nNavigation Statistics:")
        print(f"  Total: {nav_stats['total']}")
        print(f"  Successful: {nav_stats['successful']}")
        print(f"  Failed: {nav_stats['failed']}")
        print(f"  Success Rate: {success_rate:.1f}%")


def print_click_action_summary(limit: int = 20):
    """Print a summary of recent click actions."""
    history = get_playwright_action_history()
    click_actions = history.get_click_actions(limit)
    
    if not click_actions:
        print("No click actions found in history.")
        return
    
    print(f"\n=== Click Action Summary (Last {len(click_actions)} actions) ===")
    print(f"{'Timestamp':<25} {'URL':<40} {'Selector':<30} {'Status':<10} {'Time(ms)':<10}")
    print("-" * 120)
    
    for action in click_actions:
        timestamp = action.timestamp[:19]
        url = action.url[:37] + "..." if len(action.url) > 40 else action.url
        
        # Extract selector information
        selector = "N/A"
        if "selector" in action.action_data:
            selector_data = action.action_data["selector"]
            if isinstance(selector_data, dict):
                selector = f"{selector_data.get('type', 'unknown')}: {selector_data.get('value', 'N/A')}"
            else:
                selector = str(selector_data)[:27] + "..." if len(str(selector_data)) > 30 else str(selector_data)
        
        status = "✅" if action.success else "❌"
        execution_time = f"{action.execution_time_ms}ms" if action.execution_time_ms else "N/A"
        
        print(f"{timestamp:<25} {url:<40} {selector:<30} {status:<10} {execution_time:<10}")
    
    # Print click statistics
    click_stats = {
        "total": len(click_actions),
        "successful": len([a for a in click_actions if a.success]),
        "failed": len([a for a in click_actions if not a.success])
    }
    
    if click_stats["total"] > 0:
        success_rate = (click_stats["successful"] / click_stats["total"]) * 100
        print(f"\nClick Action Statistics:")
        print(f"  Total: {click_stats['total']}")
        print(f"  Successful: {click_stats['successful']}")
        print(f"  Failed: {click_stats['failed']}")
        print(f"  Success Rate: {success_rate:.1f}%")


def print_form_action_summary(limit: int = 20):
    """Print a summary of recent form actions."""
    history = get_playwright_action_history()
    form_actions = history.get_form_actions(limit)
    
    if not form_actions:
        print("No form actions found in history.")
        return
    
    print(f"\n=== Form Action Summary (Last {len(form_actions)} actions) ===")
    print(f"{'Timestamp':<25} {'URL':<40} {'Action':<20} {'Status':<10} {'Time(ms)':<10}")
    print("-" * 120)
    
    for action in form_actions:
        timestamp = action.timestamp[:19]
        url = action.url[:37] + "..." if len(action.url) > 40 else action.url
        
        # Extract form action information
        form_action = "N/A"
        if "action" in action.action_data:
            form_action = action.action_data["action"]
        elif "text_to_enter" in action.action_data:
            form_action = "type_text"
        elif "value" in action.action_data:
            form_action = "select_option"
        
        status = "✅" if action.success else "❌"
        execution_time = f"{action.execution_time_ms}ms" if action.execution_time_ms else "N/A"
        
        print(f"{timestamp:<25} {url:<40} {form_action:<20} {status:<10} {execution_time:<10}")
    
    # Print form action statistics
    form_stats = {
        "total": len(form_actions),
        "successful": len([a for a in form_actions if a.success]),
        "failed": len([a for a in form_actions if not a.success])
    }
    
    if form_stats["total"] > 0:
        success_rate = (form_stats["successful"] / form_stats["total"]) * 100
        print(f"\nForm Action Statistics:")
        print(f"  Total: {form_stats['total']}")
        print(f"  Successful: {form_stats['successful']}")
        print(f"  Failed: {form_stats['failed']}")
        print(f"  Success Rate: {success_rate:.1f}%")


def get_recent_playwright_errors(limit: int = 10):
    """Get recent Playwright action errors for debugging."""
    history = get_playwright_action_history()
    failed_actions = history.get_failed_actions(limit)
    
    if not failed_actions:
        print("No Playwright action errors found in recent history.")
        return
    
    print(f"\n=== Recent Playwright Action Errors (Last {len(failed_actions)} errors) ===")
    for action in failed_actions:
        print(f"\nTimestamp: {action.timestamp}")
        print(f"Action Type: {action.action_type}")
        print(f"URL: {action.url}")
        print(f"Title: {action.title}")
        print(f"Error: {action.error_message}")
        print(f"Action Data: {json.dumps(action.action_data, indent=2)}")
        if action.execution_time_ms:
            print(f"Execution Time: {action.execution_time_ms}ms")
        print("-" * 50)


def get_slow_actions_summary(threshold_ms: int = 5000, limit: int = 10):
    """Get summary of slow actions for performance analysis."""
    history = get_playwright_action_history()
    slow_actions = history.get_slow_actions(threshold_ms, limit)
    
    if not slow_actions:
        print(f"No actions found slower than {threshold_ms}ms threshold.")
        return
    
    print(f"\n=== Slow Actions Summary (>{threshold_ms}ms threshold) ===")
    print(f"{'Timestamp':<25} {'Type':<15} {'URL':<40} {'Time(ms)':<10}")
    print("-" * 100)
    
    for action in slow_actions:
        timestamp = action.timestamp[:19]
        action_type = action.action_type[:14] + "..." if len(action.action_type) > 15 else action.action_type
        url = action.url[:37] + "..." if len(action.url) > 40 else action.url
        execution_time = f"{action.execution_time_ms}ms" if action.execution_time_ms else "N/A"
        
        print(f"{timestamp:<25} {action_type:<15} {url:<40} {execution_time:<10}")
    
    # Calculate average execution time for slow actions
    execution_times = [action.execution_time_ms for action in slow_actions if action.execution_time_ms]
    if execution_times:
        avg_time = sum(execution_times) / len(execution_times)
        print(f"\nAverage execution time for slow actions: {avg_time:.0f}ms")


def search_playwright_actions(query: str, limit: int = 20):
    """Search Playwright actions by query string."""
    history = get_playwright_action_history()
    results = history.search_actions(query)
    
    if not results:
        print(f"No Playwright actions found matching query: '{query}'")
        return
    
    print(f"\n=== Playwright Action Search Results for '{query}' (Found {len(results)} actions) ===")
    for action in results[:limit]:
        print(f"\nTimestamp: {action.timestamp}")
        print(f"Action Type: {action.action_type}")
        print(f"URL: {action.url}")
        print(f"Title: {action.title}")
        print(f"Success: {'✅' if action.success else '❌'}")
        if action.error_message:
            print(f"Error: {action.error_message}")
        if action.execution_time_ms:
            print(f"Execution Time: {action.execution_time_ms}ms")
        print(f"Action Data: {json.dumps(action.action_data, indent=2)}")
        print("-" * 50)


def get_session_summary(session_id: Optional[str] = None):
    """Get summary of actions for a specific session."""
    history = get_playwright_action_history()
    session_actions = history.get_session_actions(session_id)
    
    if not session_actions:
        print(f"No actions found for session: {session_id or 'current'}")
        return
    
    print(f"\n=== Session Summary ===")
    print(f"Session ID: {session_id or 'current'}")
    print(f"Total Actions: {len(session_actions)}")
    
    # Group by action type
    action_type_counts = {}
    for action in session_actions:
        action_type_counts[action.action_type] = action_type_counts.get(action.action_type, 0) + 1
    
    print(f"\nAction Type Breakdown:")
    for action_type, count in action_type_counts.items():
        print(f"  {action_type}: {count}")
    
    # Group by success/failure
    successful = [action for action in session_actions if action.success]
    failed = [action for action in session_actions if not action.success]
    
    print(f"\nSuccess/Failure Breakdown:")
    print(f"  Successful: {len(successful)}")
    print(f"  Failed: {len(failed)}")
    
    if successful:
        print(f"\nSuccessful Actions:")
        for action in successful[-5:]:  # Last 5 successful
            print(f"  ✅ {action.action_type} at {action.url}")
    
    if failed:
        print(f"\nFailed Actions:")
        for action in failed[-5:]:  # Last 5 failed
            print(f"  ❌ {action.action_type} at {action.url} - {action.error_message}")


def get_performance_analysis():
    """Get performance analysis of Playwright actions."""
    history = get_playwright_action_history()
    all_actions = history.get_recent_actions(1000)  # Get last 1000 actions
    
    if not all_actions:
        print("No actions found for performance analysis.")
        return
    
    # Filter actions with execution time data
    timed_actions = [action for action in all_actions if action.execution_time_ms]
    
    if not timed_actions:
        print("No actions with execution time data found.")
        return
    
    print(f"\n=== Performance Analysis ===")
    print(f"Total Actions Analyzed: {len(timed_actions)}")
    
    # Calculate statistics
    execution_times = [action.execution_time_ms for action in timed_actions]
    avg_time = sum(execution_times) / len(execution_times)
    min_time = min(execution_times)
    max_time = max(execution_times)
    
    print(f"Execution Time Statistics:")
    print(f"  Average: {avg_time:.0f}ms")
    print(f"  Minimum: {min_time}ms")
    print(f"  Maximum: {max_time}ms")
    
    # Performance by action type
    action_type_times = {}
    for action in timed_actions:
        if action.action_type not in action_type_times:
            action_type_times[action.action_type] = []
        action_type_times[action.action_type].append(action.execution_time_ms)
    
    print(f"\nPerformance by Action Type:")
    for action_type, times in action_type_times.items():
        avg_type_time = sum(times) / len(times)
        print(f"  {action_type}: {avg_type_time:.0f}ms (count: {len(times)})")
    
    # Identify bottlenecks
    slow_threshold = avg_time * 2  # Actions slower than 2x average
    slow_actions = [action for action in timed_actions if action.execution_time_ms > slow_threshold]
    
    if slow_actions:
        print(f"\nPotential Bottlenecks (>{slow_threshold:.0f}ms):")
        for action in slow_actions[:5]:  # Top 5 slowest
            print(f"  {action.action_type} at {action.url}: {action.execution_time_ms}ms")


def export_playwright_action_history(export_path: str, format_type: str = "json", 
                                   action_types: Optional[List[str]] = None, limit: int = None):
    """Export Playwright action history to a file."""
    history = get_playwright_action_history()
    
    if action_types:
        export_data = [record for record in history.history if record.action_type in action_types]
    else:
        export_data = history.history
    
    if limit:
        export_data = export_data[-limit:]
    
    if not export_data:
        print("No Playwright actions to export.")
        return
    
    try:
        if format_type.lower() == "json":
            with open(export_path, 'w', encoding='utf-8') as f:
                history_data = [action.__dict__ for action in export_data]
                json.dump(history_data, f, indent=2, ensure_ascii=False)
        
        elif format_type.lower() == "csv":
            import csv
            with open(export_path, 'w', newline='', encoding='utf-8') as f:
                if export_data:
                    writer = csv.DictWriter(f, fieldnames=export_data[0].__dict__.keys())
                    writer.writeheader()
                    for action in export_data:
                        writer.writerow(action.__dict__)
        
        print(f"Playwright action history exported to {export_path}")
        print(f"Exported {len(export_data)} actions")
        
    except Exception as e:
        print(f"Error exporting Playwright action history: {e}")


def main():
    """Main function to demonstrate Playwright action history utilities."""
    print("=== Playwright Action History Utilities ===")
    print("Available functions:")
    print("1. print_playwright_action_summary() - Show recent Playwright actions")
    print("2. print_navigation_summary() - Show recent navigation actions")
    print("3. print_click_action_summary() - Show recent click actions")
    print("4. print_form_action_summary() - Show recent form actions")
    print("5. get_recent_playwright_errors() - Show recent action errors")
    print("6. get_slow_actions_summary() - Show slow actions for performance analysis")
    print("7. search_playwright_actions(query) - Search action history")
    print("8. get_session_summary() - Show session action summary")
    print("9. get_performance_analysis() - Analyze action performance")
    print("10. export_playwright_action_history(path, format) - Export action history")
    
    # Show basic summary
    print_playwright_action_summary()
    
    # Show navigation summary
    print_navigation_summary()
    
    # Show recent errors if any
    get_recent_playwright_errors()


if __name__ == "__main__":
    main()

