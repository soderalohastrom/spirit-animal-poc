#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pygame",
# ]
# ///
"""
Voice Notification Hook for Claude Code
=====================================

Plays voice notifications based on voice character and Claude's canonical hook/tool events.
Uses sound_mapping.json to map Claude's events to sound files.

Author: Chong-U (chong-u@aioriented.dev)
Created: 2025
Purpose: Advanced voice notification system for Claude Code with context-aware sound mapping

Features:
- Context-aware sound selection based on file extensions and command patterns
- 30+ Alfred voice notifications for different operations
- Modular hook architecture with graceful fallbacks
- Intelligent mapping of Claude's canonical events to appropriate audio feedback

Usage: 
  python voice_notification.py --voice=alfred
  python voice_notification.py --voice=jarvis

Arguments:
  --voice: Voice character (alfred, jarvis)
"""

import json
import sys
import argparse
import logging
import random
from pathlib import Path

# Add parent directory to path for importing common module
sys.path.insert(0, str(Path(__file__).parent.parent))

from common import (
    HookEvent,
    ToolName,
    InputKey,
    FileExtension,
    GitCommand,
    CommandType,
    NotificationType,
    get_hook_event,
    get_tool_name,
    get_file_extension,
    get_git_command,
    get_command_type,
    categorize_notification_message,
    extract_tool_input_value,
    is_file_operation_tool,
    debug_hook_data,
    enum_to_json_value,
)

# Type aliases for complex recurring types
type SoundMapping = dict[str, dict[str, str] | str | list[str]]
type ToolInput = dict[str, str]
type HookData = dict[str, str | dict | None]
type SoundVariations = str | list[str]

def setup_module_logger(module_name: str, log_file: Path | None = None) -> logging.Logger:
    """Set up a module-specific logger with file handler.
    
    Args:
        module_name: Name of the module (e.g., 'hooks.voice_notifications')
        log_file: Path to log file (defaults to module_debug.log in same directory)
        
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(module_name)
    
    if logger.handlers:
        return logger  # Already configured
    
    if log_file is None:
        log_file = Path(__file__).parent / "debug.log"
    
    # Create file handler
    handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    return logger

# Initialize module logger
logger = setup_module_logger('hooks.voice_notifications')

def load_sound_mapping() -> SoundMapping:
    """Load sound mapping configuration from JSON file."""
    script_dir = Path(__file__).parent
    mapping_file = script_dir / "sound_mapping.json"
    
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
            logger.debug(f"Loaded sound mapping from {mapping_file}")
            return mapping
    except Exception as e:
        # Fallback mapping if file doesn't exist
        logger.error(f"Could not load sound_mapping.json: {e}, using fallback")
        return {
            "hook_events": {"Stop": "task_complete", "PostToolUse": "task_complete"},
            "tools": {"Read": "file_read", "Edit": "code_edit", "Grep": "search"},
            "default": "task_complete"
        }

def get_context_aware_sound_name(hook_event_name: HookEvent, tool_name: ToolName | None = None, tool_input: ToolInput | None = None, input_data: HookData | None = None) -> str:
    """Map Claude's hook/tool names to context-aware sound file names with variation support."""
    mapping = load_sound_mapping()
    
    # Special handling for Notification events with message context
    if hook_event_name == HookEvent.NOTIFICATION and input_data:
        notification_sound = _get_notification_sound(mapping, input_data)
        if notification_sound:
            logger.debug(f"Notification message mapping: '{notification_sound}'")
            return notification_sound
    
    # Try context-aware patterns for file operations and bash commands
    if hook_event_name in [HookEvent.PRE_TOOL_USE, HookEvent.POST_TOOL_USE] and tool_name and tool_input:
        context_sound = _get_context_sound(mapping, tool_name, tool_input)
        if context_sound:
            logger.debug(f"Context-aware mapping: {hook_event_name} + {tool_name} -> '{context_sound}'")
            return context_sound
        else:
            logger.warning(f"No context pattern found for {tool_name} with {hook_event_name}, falling back to tool mapping")
    
    # Fallback to original tool-based mapping
    if hook_event_name in [HookEvent.PRE_TOOL_USE, HookEvent.POST_TOOL_USE] and tool_name:
        if tool_name.value in mapping["tools"]:
            sound_name = _select_variation(mapping["tools"][tool_name.value])
            logger.debug(f"Tool mapping: '{tool_name}' -> '{sound_name}' for {hook_event_name}")
            return sound_name
        else:
            logger.warning(f"No tool mapping found for '{tool_name}', falling back to hook event mapping")
    
    # Then try hook events (Stop, Notification, etc.)
    if hook_event_name.value in mapping["hook_events"]:
        hook_config = mapping["hook_events"][hook_event_name.value]
        
        # Check if hook event has tool-specific mappings (dict format)
        if isinstance(hook_config, dict):
            # Try tool-specific mapping first
            if tool_name and tool_name.value in hook_config:
                sound_name = _select_variation(hook_config[tool_name.value])
                logger.debug(f"Tool-specific hook mapping: '{hook_event_name}' + '{tool_name}' -> '{sound_name}'")
                return sound_name
            # Fall back to default for this hook event
            elif "default" in hook_config:
                sound_name = _select_variation(hook_config["default"])
                logger.debug(f"Hook event default mapping: '{hook_event_name}' -> '{sound_name}'")
                return sound_name
        else:
            # Simple string/array mapping (legacy format)
            sound_name = _select_variation(hook_config)
            logger.debug(f"Hook event mapping: '{hook_event_name}' -> '{sound_name}'")
            return sound_name
    else:
        logger.warning(f"No hook event mapping found for '{hook_event_name}', using default sound")
    
    # Final fallback to default
    sound_name = mapping["default"]
    logger.warning(f"Default fallback: '{sound_name}' for hook='{hook_event_name}', tool='{tool_name}'")
    return sound_name

def _get_context_sound(mapping: SoundMapping, tool_name: ToolName, tool_input: ToolInput) -> str | None:
    """Get context-specific sound based on file extensions, filenames, or command patterns."""
    context_patterns = mapping.get("context_patterns", {})
    
    # Handle file operations (Read, Edit, Write)
    if is_file_operation_tool(tool_name):
        return _get_file_operation_sound(context_patterns, tool_name, tool_input)
    
    # Handle bash commands
    if tool_name == ToolName.BASH:
        return _get_bash_command_sound(context_patterns, tool_input)
    
    return None

def _get_file_operation_sound(context_patterns: dict[str, dict], tool_name: ToolName, tool_input: ToolInput) -> str | None:
    """Get sound for file operations based on file extension or filename."""
    file_ops = context_patterns.get("file_operations", {})
    
    # Map tool variants to base tool names
    base_tool_name = tool_name.value
    if tool_name in [ToolName.MULTI_EDIT, ToolName.NOTEBOOK_EDIT]:
        base_tool_name = ToolName.EDIT.value
    elif tool_name == ToolName.NOTEBOOK_READ:
        base_tool_name = ToolName.READ.value
    
    tool_patterns = file_ops.get(base_tool_name, {})
    file_path = tool_input.get(InputKey.FILE_PATH.value, "")
    
    if not file_path:
        return None
    
    # Use enum-based file extension detection
    file_extension = get_file_extension(file_path)
    path_obj = Path(file_path)
    filename = path_obj.name
    
    # Try filename-specific patterns first
    by_filename = tool_patterns.get("by_filename", {})
    if filename in by_filename:
        return _select_variation(by_filename[filename])
    
    # Try extension-specific patterns using enum
    by_extension = tool_patterns.get("by_extension", {})
    if file_extension and file_extension.value in by_extension:
        return _select_variation(by_extension[file_extension.value])
    
    # Fallback to tool default
    default_sounds = tool_patterns.get("default", [])
    if default_sounds:
        return _select_variation(default_sounds)
    
    return None

def _get_bash_command_sound(context_patterns: dict[str, dict], tool_input: ToolInput) -> str | None:
    """Get sound for bash commands based on command patterns."""
    bash_commands = context_patterns.get("bash_commands", {})
    command = tool_input.get(InputKey.COMMAND.value, "")
    
    if not command:
        return None
    
    # Try git command detection first using enum
    git_command = get_git_command(command)
    if git_command:
        git_patterns = bash_commands.get("git", {})
        if isinstance(git_patterns, dict) and git_command.value in git_patterns:
            return _select_variation(git_patterns[git_command.value])
    
    # Try other command types using enum
    command_type = get_command_type(command)
    if command_type:
        cmd_patterns = bash_commands.get(command_type.value, {})
        if isinstance(cmd_patterns, dict):
            # Try exact pattern matches
            for pattern, sounds in cmd_patterns.items():
                if command.strip().startswith(pattern):
                    return _select_variation(sounds)
        elif isinstance(cmd_patterns, list):
            # Direct list of sounds for this command type
            return _select_variation(cmd_patterns)
    
    # Fallback to bash default
    default_sounds = bash_commands.get("default", [])
    if default_sounds:
        return _select_variation(default_sounds)
    
    return None

def _get_notification_sound(mapping: SoundMapping, input_data: HookData) -> str | None:
    """Get context-specific sound for Notification events based on message content."""
    notification_config = mapping["hook_events"].get(HookEvent.NOTIFICATION.value, {})
    
    # If not a dict, use legacy behavior
    if not isinstance(notification_config, dict):
        return _select_variation(notification_config)
    
    message = input_data.get(InputKey.MESSAGE.value, "")
    if not message:
        return None
    
    # Use enum-based notification categorization
    notification_type = categorize_notification_message(message)
    
    # Map notification types to config keys
    config_key = notification_type.value
    if config_key in notification_config:
        logger.debug(f"{notification_type.name} detected: {message}")
        return _select_variation(notification_config[config_key])
    
    # Fallback to default notification sounds
    if "default" in notification_config:
        logger.debug(f"Using default notification sound for: {message}")
        return _select_variation(notification_config["default"])
    
    return None

def _select_variation(sounds: SoundVariations) -> str:
    """Select a random variation from available sound options."""
    if isinstance(sounds, str):
        return sounds
    elif isinstance(sounds, list) and sounds:
        return random.choice(sounds)
    return "task_complete"

# Legacy wrapper for backward compatibility
def get_sound_name(hook_event_name: str, tool_name: str | None = None, tool_input: ToolInput | None = None, input_data: HookData | None = None) -> str:
    """Legacy wrapper for get_context_aware_sound_name."""
    # Convert string parameters to enums safely
    hook_event_enum = get_hook_event({InputKey.HOOK_EVENT_NAME.value: hook_event_name})
    tool_name_enum = get_tool_name({InputKey.TOOL_NAME.value: tool_name}) if tool_name else None
    
    # Use fallback if conversion failed
    if not hook_event_enum:
        logger.warning(f"Unknown hook event: {hook_event_name}, using Stop as fallback")
        hook_event_enum = HookEvent.STOP
    
    return get_context_aware_sound_name(hook_event_enum, tool_name_enum, tool_input, input_data)

def play_voice_sound(voice: str = "ding", sound_name: str = "task_complete") -> None:
    """
    Play a voice sound using pygame library with graceful fallbacks.
    
    Args:
        voice: Voice character (alfred, jarvis, ding)
        sound_name: Sound file name from mapping (task_complete, file_read, etc.)
    """
    logger.info(f"🎵 Attempting to play: {voice}/{sound_name}")
    
    try:
        import pygame
        import os
        
        # Get script directory and build sound path
        script_dir = Path(__file__).parent
        
        # Try specific voice/sound combination first (mp3 then wav)
        mp3_path = script_dir / "sounds" / voice / f"{sound_name}.mp3"
        wav_path = script_dir / "sounds" / voice / f"{sound_name}.wav"
        
        if mp3_path.exists():
            sound_path = mp3_path
            logger.debug(f"Found primary sound file: {sound_path}")
        elif wav_path.exists():
            sound_path = wav_path
            logger.debug(f"Found primary sound file (wav): {sound_path}")
        else:
            logger.warning(f"Primary sound files not found: {mp3_path} OR {wav_path}")
            
            # Direct fallback to chime.mp3 (more pleasant than ding)
            chime_path = script_dir / "sounds" / "chime.mp3"
            if chime_path.exists():
                sound_path = chime_path
                logger.warning(f"Using chime fallback: {sound_path}")
            else:
                logger.error(f"All fallbacks failed - tried: {mp3_path}, {wav_path}, {chime_path}")
                print("\a", end="", flush=True)  # Terminal bell fallback
                return
        
        # Set environment variable to suppress pygame messages
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
        
        # Initialize pygame mixer
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
        pygame.mixer.init()
        
        # Load and play the sound
        sound = pygame.mixer.Sound(str(sound_path))
        sound.play()
        
        # Wait for sound to play completely
        import time
        time.sleep(0.1)  # Let it start
        
        # Wait for completion with longer timeout for voice clips
        timeout = 3.0  # 3 seconds max wait
        start_time = time.time()
        
        while pygame.mixer.get_busy() and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        logger.info(f"✅ Successfully played: {voice}/{sound_name} -> {sound_path.name} (from {sound_path})")
        pygame.mixer.quit()
        
    except ImportError as e:
        logger.error(f"❌ pygame not available ({voice}/{sound_name}): {e} - falling back to terminal bell")
        print("\a", end="", flush=True)
        
    except Exception as e:
        logger.error(f"❌ Voice playback failed ({voice}/{sound_name}): {e} - attempted file: {sound_path if 'sound_path' in locals() else 'unknown'}")
        print("\a", end="", flush=True)

def main() -> None:
    """
    Main function - reads Claude's JSON hook data and plays appropriate sound.
    """
    parser = argparse.ArgumentParser(description='Play voice notifications for Claude Code')
    parser.add_argument('--voice', default='alfred', help='Voice character (alfred, jarvis, ding)')
    parser.add_argument('--debug', action='store_true', help='Enable verbose debug logging')
    
    # Parse command line arguments
    args = parser.parse_args()
    voice = args.voice
    debug_mode = args.debug
    
    if debug_mode:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled - verbose logging active")
    
    logger.info(f"Voice notification hook started with voice: {voice}, debug: {debug_mode}")
    
    # Read hook data from stdin (Claude provides this)
    try:
        input_data = json.load(sys.stdin)
        
        # Comprehensive logging of all incoming data
        if debug_mode:
            logger.debug("=" * 60)
            logger.debug("COMPREHENSIVE HOOK DATA DUMP:")
            logger.debug(json.dumps(input_data, indent=2, default=str))
            logger.debug("Available keys: " + ", ".join(input_data.keys()))
            logger.debug("=" * 60)
        
        # Extract Claude's canonical event information using enums
        hook_event_name = get_hook_event(input_data)
        tool_name = get_tool_name(input_data)
        tool_input = input_data.get(InputKey.TOOL_INPUT.value, {})
        
        # Special logging for Notification events
        if hook_event_name == HookEvent.NOTIFICATION:
            notification_message = input_data.get(InputKey.MESSAGE.value, "No message provided")
            logger.info(f"🔔 NOTIFICATION EVENT DETECTED: {notification_message}")
            
            # Use enum-based categorization
            notification_type = categorize_notification_message(notification_message)
            logger.info(f"📋 Notification type: {notification_type.name}")
            
            logger.debug(f"Notification context: {json.dumps(input_data, indent=2, default=str)}")
        
        # Special logging for SubagentStop events
        if hook_event_name == HookEvent.SUBAGENT_STOP:
            stop_hook_active = input_data.get(InputKey.STOP_HOOK_ACTIVE.value, False)
            logger.info(f"🤖 SUBAGENT STOP EVENT DETECTED")
            logger.info(f"📊 Stop hook active: {stop_hook_active}")
            
            if stop_hook_active:
                logger.info("🔄 Main Claude Code continuing from previous stop hook")
            else:
                logger.info("✅ Subagent completed task independently")
            
            logger.debug(f"SubagentStop context: {json.dumps(input_data, indent=2, default=str)}")
        
        # Enhanced logging with context
        context_info = ""
        if tool_input:
            if InputKey.FILE_PATH.value in tool_input:
                context_info = f" -> {tool_input[InputKey.FILE_PATH.value]}"
            elif InputKey.COMMAND.value in tool_input:
                context_info = f" -> {tool_input[InputKey.COMMAND.value]}"
            elif InputKey.PATTERN.value in tool_input:
                context_info = f" -> searching '{tool_input[InputKey.PATTERN.value]}'"
        
        logger.info(f"🔄 Processing: {hook_event_name} + {tool_name or 'None'}{context_info}")
        if not debug_mode:  # Avoid duplicate logging in debug mode
            logger.debug(f"Full hook data: {input_data}")
        
        # Map to sound name using our enhanced context-aware configuration
        if hook_event_name:
            sound_name = get_context_aware_sound_name(hook_event_name, tool_name, tool_input, input_data)
        else:
            # Fallback for unknown events
            logger.warning(f"Unknown hook event, using fallback sound")
            sound_name = "task_complete"
        
        if debug_mode:
            logger.debug(f"🎵 Sound selection result: '{sound_name}'")
        
    except json.JSONDecodeError as e:
        # No JSON input, use default
        sound_name = "task_complete"
        logger.warning(f"No JSON input - using default sound: {sound_name}, voice: {voice}, error: {e}")
        
    except Exception as e:
        sound_name = "task_complete"
        logger.error(f"Hook parsing error - using default: sound={sound_name}, voice={voice}, error={e}")
    
    # Play the sound
    play_voice_sound(voice, sound_name)
    sys.exit(0)

if __name__ == "__main__":
    main()