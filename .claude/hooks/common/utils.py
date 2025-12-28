#!/usr/bin/env python3
"""
Common Utilities for Claude Code Hook System
=============================================

Utility functions for converting between string literals and enums,
providing safe conversion with fallback handling for the Claude Code hook system.

Author: Chong-U (chong-u@aioriented.dev)
Created: 2025
Purpose: Safe enum conversion utilities for Claude Code hook system
"""

import logging
from typing import Optional, Dict, Any, Type, TypeVar
from pathlib import Path

from .enums import (
    HookEvent,
    ToolName,
    InputKey,
    FileExtension,
    GitCommand,
    CommandType,
    NotificationType,
)

# Type variable for enum types
EnumType = TypeVar('EnumType')

# Logger for this module
logger = logging.getLogger('hooks.common.utils')


def safe_enum_from_string(enum_class: Type[EnumType], value: str, fallback: Optional[EnumType] = None) -> Optional[EnumType]:
    """Safely convert a string value to an enum, with optional fallback.
    
    Args:
        enum_class: The enum class to convert to
        value: String value to convert
        fallback: Optional fallback enum value if conversion fails
        
    Returns:
        Enum value if conversion succeeds, fallback if provided, None otherwise
        
    Examples:
        >>> safe_enum_from_string(HookEvent, "Stop", HookEvent.STOP)
        <HookEvent.STOP: 'Stop'>
        
        >>> safe_enum_from_string(ToolName, "InvalidTool", ToolName.READ)
        <ToolName.READ: 'Read'>
        
        >>> safe_enum_from_string(ToolName, "InvalidTool")
        None
    """
    if not value:
        return fallback
    
    try:
        # Try direct conversion first
        return enum_class(value)
    except ValueError:
        # Try case-insensitive search for string enums
        if hasattr(enum_class, '__members__'):
            for enum_member in enum_class:
                if hasattr(enum_member, 'value') and str(enum_member.value).lower() == value.lower():
                    logger.debug(f"Case-insensitive match found: '{value}' -> {enum_member}")
                    return enum_member
        
        # Log the failed conversion
        logger.warning(f"Could not convert '{value}' to {enum_class.__name__}, using fallback: {fallback}")
        return fallback


def get_hook_event(hook_data: Dict[str, Any]) -> Optional[HookEvent]:
    """Extract and convert hook event name from hook data.
    
    Args:
        hook_data: Dictionary containing hook event data from Claude Code
        
    Returns:
        HookEvent enum value or None if not found/invalid
    """
    event_name = hook_data.get(InputKey.HOOK_EVENT_NAME.value)
    return safe_enum_from_string(HookEvent, event_name)


def get_tool_name(hook_data: Dict[str, Any]) -> Optional[ToolName]:
    """Extract and convert tool name from hook data.
    
    Args:
        hook_data: Dictionary containing hook event data from Claude Code
        
    Returns:
        ToolName enum value or None if not found/invalid
    """
    tool_name = hook_data.get(InputKey.TOOL_NAME.value)
    return safe_enum_from_string(ToolName, tool_name)


def get_file_extension(file_path: str) -> Optional[FileExtension]:
    """Extract and convert file extension from file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        FileExtension enum value or None if not recognized
        
    Examples:
        >>> get_file_extension("example.py")
        <FileExtension.PYTHON: '.py'>
        
        >>> get_file_extension("README.md")
        <FileExtension.README: 'README.md'>
    """
    if not file_path:
        return None
    
    path_obj = Path(file_path)
    filename = path_obj.name
    extension = path_obj.suffix.lower()
    
    # Check for special filenames first (README.md, Dockerfile, etc.)
    special_files = {
        "README.md": FileExtension.README,
        ".gitignore": FileExtension.GITIGNORE,
        "Dockerfile": FileExtension.DOCKERFILE,
        "Makefile": FileExtension.MAKEFILE,
    }
    
    if filename in special_files:
        return special_files[filename]
    
    # Then check for extensions
    return safe_enum_from_string(FileExtension, extension)


def get_git_command(command: str) -> Optional[GitCommand]:
    """Extract and convert git command from bash command string.
    
    Args:
        command: Full bash command string
        
    Returns:
        GitCommand enum value or None if not a recognized git command
        
    Examples:
        >>> get_git_command("git status --porcelain")
        <GitCommand.STATUS: 'git status'>
        
        >>> get_git_command("git commit -m 'message'")
        <GitCommand.COMMIT: 'git commit'>
    """
    if not command or not command.strip().startswith("git "):
        return None
    
    # Try to match against known git command patterns
    for git_cmd in GitCommand:
        if command.strip().startswith(git_cmd.value):
            return git_cmd
    
    return None


def get_command_type(command: str) -> Optional[CommandType]:
    """Extract and convert command type from bash command string.
    
    Args:
        command: Full bash command string
        
    Returns:
        CommandType enum value or None if not recognized
        
    Examples:
        >>> get_command_type("npm install express")
        <CommandType.NPM: 'npm'>
        
        >>> get_command_type("python script.py")
        <CommandType.PYTHON: 'python'>
    """
    if not command:
        return None
    
    command = command.strip()
    
    # Try to match against known command types
    for cmd_type in CommandType:
        if command.startswith(cmd_type.value + " ") or command == cmd_type.value:
            return cmd_type
    
    return None


def categorize_notification_message(message: str) -> NotificationType:
    """Categorize a notification message into a type.
    
    Args:
        message: Notification message text
        
    Returns:
        NotificationType enum value
        
    Examples:
        >>> categorize_notification_message("Permission required to use the Read tool")
        <NotificationType.PERMISSION_REQUEST: 'permission_request'>
        
        >>> categorize_notification_message("Waiting for your input...")
        <NotificationType.IDLE_TIMEOUT: 'idle_timeout'>
    """
    if not message:
        return NotificationType.GENERAL
    
    message_lower = message.lower()
    
    # Check for permission requests
    if "permission" in message_lower and "use" in message_lower:
        return NotificationType.PERMISSION_REQUEST
    
    # Check for idle timeouts
    if "waiting for your input" in message_lower or "waiting for input" in message_lower:
        return NotificationType.IDLE_TIMEOUT
    
    # Check for errors
    if any(keyword in message_lower for keyword in ["error", "failed", "exception", "critical"]):
        return NotificationType.ERROR
    
    # Check for warnings
    if any(keyword in message_lower for keyword in ["warning", "warn", "caution"]):
        return NotificationType.WARNING
    
    # Default to general
    return NotificationType.GENERAL


def extract_tool_input_value(hook_data: Dict[str, Any], key: InputKey) -> Optional[str]:
    """Extract a value from tool_input section of hook data.
    
    Args:
        hook_data: Dictionary containing hook event data from Claude Code
        key: InputKey enum for the desired value
        
    Returns:
        String value or None if not found
        
    Examples:
        >>> extract_tool_input_value(hook_data, InputKey.FILE_PATH)
        "/path/to/file.py"
        
        >>> extract_tool_input_value(hook_data, InputKey.COMMAND)
        "git status"
    """
    tool_input = hook_data.get(InputKey.TOOL_INPUT.value, {})
    if not isinstance(tool_input, dict):
        return None
    
    return tool_input.get(key.value)


def is_file_operation_tool(tool_name: Optional[ToolName]) -> bool:
    """Check if a tool is a file operation tool.
    
    Args:
        tool_name: ToolName enum value or None
        
    Returns:
        True if the tool operates on files, False otherwise
    """
    if not tool_name:
        return False
    
    from .enums import FILE_OPERATION_TOOLS
    return tool_name in FILE_OPERATION_TOOLS


def is_system_tool(tool_name: Optional[ToolName]) -> bool:
    """Check if a tool is a system operation tool.
    
    Args:
        tool_name: ToolName enum value or None
        
    Returns:
        True if the tool is a system operation, False otherwise
    """
    if not tool_name:
        return False
        
    from .enums import SYSTEM_TOOLS
    return tool_name in SYSTEM_TOOLS


def is_search_tool(tool_name: Optional[ToolName]) -> bool:
    """Check if a tool is a search operation tool.
    
    Args:
        tool_name: ToolName enum value or None
        
    Returns:
        True if the tool is a search operation, False otherwise
    """
    if not tool_name:
        return False
        
    from .enums import SEARCH_TOOLS
    return tool_name in SEARCH_TOOLS


def enum_to_json_value(enum_value: Optional[EnumType]) -> Optional[str]:
    """Convert an enum value to its JSON string representation.
    
    Args:
        enum_value: Any enum value or None
        
    Returns:
        String value for JSON serialization or None
    """
    if enum_value is None:
        return None
    
    if hasattr(enum_value, 'value'):
        return str(enum_value.value)
    
    return str(enum_value)


def debug_hook_data(hook_data: Dict[str, Any], logger: logging.Logger) -> None:
    """Debug utility to log parsed hook data with enum conversions.
    
    Args:
        hook_data: Raw hook data from Claude Code
        logger: Logger instance to use for output
    """
    if not logger.isEnabledFor(logging.DEBUG):
        return
    
    logger.debug("=== HOOK DATA ANALYSIS ===")
    
    # Extract and convert basic fields
    hook_event = get_hook_event(hook_data)
    tool_name = get_tool_name(hook_data)
    
    logger.debug(f"Hook Event: {hook_event} (raw: {hook_data.get('hook_event_name')})")
    logger.debug(f"Tool Name: {tool_name} (raw: {hook_data.get('tool_name')})")
    
    # Analyze tool input if present
    file_path = extract_tool_input_value(hook_data, InputKey.FILE_PATH)
    if file_path:
        file_ext = get_file_extension(file_path)
        logger.debug(f"File Path: {file_path} -> Extension: {file_ext}")
    
    command = extract_tool_input_value(hook_data, InputKey.COMMAND)
    if command:
        git_cmd = get_git_command(command)
        cmd_type = get_command_type(command)
        logger.debug(f"Command: {command}")
        logger.debug(f"  -> Git Command: {git_cmd}")
        logger.debug(f"  -> Command Type: {cmd_type}")
    
    # Analyze notification if present
    message = hook_data.get(InputKey.MESSAGE.value)
    if message:
        msg_type = categorize_notification_message(message)
        logger.debug(f"Notification: {message} -> Type: {msg_type}")
    
    # Tool categorization
    if tool_name:
        logger.debug(f"Tool Categories:")
        logger.debug(f"  -> File Operation: {is_file_operation_tool(tool_name)}")
        logger.debug(f"  -> System Tool: {is_system_tool(tool_name)}")
        logger.debug(f"  -> Search Tool: {is_search_tool(tool_name)}")
    
    logger.debug("=== END HOOK DATA ANALYSIS ===")