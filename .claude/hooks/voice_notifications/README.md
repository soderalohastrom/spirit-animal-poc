# Voice Notification Hook System

This module provides immersive voice notification capabilities for Claude Code using Alfred's voice character, offering immediate audio feedback during development activities with context-aware sound mapping.

## Features

- **Context-aware sound selection** - 200+ mappings based on file extensions, commands, and operations
- **Voice character system** - 30+ specialized Alfred sounds with planned Jarvis support
- **Sound variations** - Random selection from multiple audio options for variety
- **Intelligent event mapping** - Uses Claude's canonical hook/tool events for precise feedback
- **Graceful fallback system** - Alfred → error sound → chime → terminal bell progression
- **Module-specific logging** - Independent debug logging with emojis and timestamps
- **Dual hook architecture** - Works alongside push notifications for comprehensive feedback
- **Real-time feedback** - Immediate audio confirmation of Claude's activities

## Quick Start

### 1. Install Dependencies

Ensure pygame is available for audio playback:

```bash
# Using uv (recommended)
uv add pygame

# Or using pip
pip install pygame
```

### 2. Voice Characters

- **Alfred** - Complete set with 30+ specialized sounds for different operations
- **Jarvis** - Placeholder directory for future implementation
- **Error fallback** - Dedicated error handling with "I'm afraid there's been an issue" sound

### 3. Configuration

Voice notifications are configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [
        {"command": "uv run .claude/hooks/voice_notifications/handler.py --voice=alfred"},
        {"command": "uv run .claude/hooks/push_notifications/handler.py --topic=claude-code-notifications"}
      ]
    }],
    "Notification": [{
      "hooks": [
        {"command": "uv run .claude/hooks/voice_notifications/handler.py --voice=alfred"},
        {"command": "uv run .claude/hooks/push_notifications/handler.py --topic=claude-code-notifications --priority=4 --tags=🔔"}
      ]
    }],
    "PreToolUse": [{
      "hooks": [{
        "command": "uv run .claude/hooks/voice_notifications/handler.py --voice=alfred"
      }]
    }],
    "PostToolUse": [{
      "hooks": [{
        "command": "uv run .claude/hooks/voice_notifications/handler.py --voice=alfred"
      }]
    }]
  }
}
```

### 4. Customization

#### Change Voice Character
Edit the `--voice` parameter in `.claude/settings.json`:
```bash
--voice=jarvis  # When Jarvis sounds are added
--voice=alfred  # Default voice character
```

#### Debug Mode
Enable verbose logging for troubleshooting:
```bash
--voice=alfred --debug
```

## Testing

### Manual Testing

Test individual hook events with different voice characters:

```bash
# Test Stop hook with Alfred
echo '{"hook_event_name": "Stop"}' | uv run .claude/hooks/voice_notifications/handler.py --voice=alfred

# Test permission request notification
echo '{"hook_event_name": "Notification", "message": "Permission required to use the Read tool"}' | uv run .claude/hooks/voice_notifications/handler.py --voice=alfred

# Test file operation with context awareness
echo '{"hook_event_name": "PostToolUse", "tool_name": "Read", "tool_input": {"file_path": "example.py"}}' | uv run .claude/hooks/voice_notifications/handler.py --voice=alfred

# Test bash command context
echo '{"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "git status"}}' | uv run .claude/hooks/voice_notifications/handler.py --voice=alfred
```

### Debug Testing

Enable comprehensive logging for development:

```bash
# Debug mode with detailed logging
echo '{"hook_event_name": "Stop"}' | uv run .claude/hooks/voice_notifications/handler.py --voice=alfred --debug

# Test SubagentStop event tracking
echo '{"hook_event_name": "SubagentStop", "stop_hook_active": false}' | uv run .claude/hooks/voice_notifications/handler.py --voice=alfred --debug
```

### Log Analysis

Monitor voice notification activity:

```bash
# View debug logs
cat .claude/hooks/voice_notifications/debug.log

# Follow live activity
tail -f .claude/hooks/voice_notifications/debug.log

# Search for specific events
grep "NOTIFICATION EVENT" .claude/hooks/voice_notifications/debug.log
```

## Architecture

### File Structure
```
.claude/hooks/voice_notifications/
├── handler.py                # Main voice notification handler (460+ lines)
├── sound_mapping.json        # Context-aware sound mappings (200+ patterns)
├── debug.log                # Module-specific logging with emojis
├── __init__.py              # Python module marker
├── README.md                # This documentation
└── sounds/                  # Audio file directories
    ├── alfred/              # Alfred voice character (30+ sounds)
    │   ├── task_complete.mp3
    │   ├── file_read.mp3
    │   ├── code_edit.mp3
    │   ├── permission_request.mp3
    │   ├── error.mp3
    │   └── ... (25+ more specialized sounds)
    ├── jarvis/              # Jarvis placeholder directory
    ├── chime.mp3           # Pleasant fallback sound
    └── ding.wav            # Terminal bell alternative
```

### Hook Events Supported

- **Stop**: Task completion with multiple sound variations
- **SubagentStop**: Subagent task completion with stop hook status tracking
- **Notification**: Permission requests, idle timeouts, general notifications with context detection
- **PreToolUse**: Context-aware tool operation start notifications
- **PostToolUse**: Operation completion notifications with specialized sounds
- **UserPromptSubmit**: User input acknowledgment

### Context-Aware Patterns

**File Operations:**
- Python files (.py): "starting_python_read", "beginning_python_changes"
- JavaScript/TypeScript (.js/.ts): "starting_javascript_edit", "beginning_typescript_access"
- Documentation (.md): "starting_docs_read", "beginning_readme_update"
- Configuration (.json/.yml/.toml): "starting_config_edit", "beginning_yaml_check"
- Special files: CLAUDE.md, package.json, README.md get dedicated sounds

**Bash Commands:**
- Git operations: "starting_git_status", "beginning_changes_save", "starting_git_push"
- Package management: "starting_npm_install", "beginning_python_deps"
- System commands: "starting_list", "beginning_directory_creation"

**Notification Context Detection:**
- Permission requests: Detects "permission" + "use" patterns → authorization_needed.mp3
- Idle timeouts: Detects "waiting for input" patterns → awaiting_response.mp3
- General notifications: Default attention sounds with variations

## Sound Variations

The system includes multiple audio options for variety and natural feel:

- **Stop events**: "task_complete", "work_finished", "request_fulfilled", "work_concluded", "assignment_finished"
- **File operations**: Extension-specific sounds with "starting" and "beginning" variations
- **Git operations**: Command-specific sounds for status, commit, push, pull, staging
- **Todo management**: "updating_todo_list", "managing_tasks", "tracking_progress"
- **Error handling**: Dedicated "error.mp3" sound for system issues

## Integration with Push Notifications

Voice notifications work seamlessly alongside push notifications in a dual hook architecture:

- **Voice notifications**: Immediate audio feedback during active development sessions
- **Push notifications**: Persistent mobile/desktop alerts for remote monitoring
- **Shared intelligence**: Both systems use similar context-aware patterns and message variations
- **Independent operation**: Each system has its own logging and graceful failure handling
- **Unified configuration**: Both hooks configured together in `.claude/settings.json`
- **Complementary coverage**: Voice for immediate feedback, push for persistent alerts

## Configuration Options

### Command Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--voice` | `alfred` | Voice character (alfred, jarvis) |
| `--debug` | `false` | Enable verbose debug logging |

### Hook Configuration Examples

**Alfred voice only:**
```json
"Stop": [{
  "hooks": [{
    "command": "uv run .claude/hooks/voice_notifications/handler.py --voice=alfred"
  }]
}]
```

**Debug mode enabled:**
```json
"Notification": [{
  "hooks": [{
    "command": "uv run .claude/hooks/voice_notifications/handler.py --voice=alfred --debug"
  }]
}]
```

**Multiple voice characters (when Jarvis is implemented):**
```json
"Stop": [{
  "hooks": [
    {"command": "uv run .claude/hooks/voice_notifications/handler.py --voice=alfred"},
    {"command": "uv run .claude/hooks/voice_notifications/handler.py --voice=jarvis"}
  ]
}]
```

## Dependencies

- **Python**: 3.13+ (with native type annotations)
- **pygame**: Audio playback library (installed via `uv add pygame`)
- **pathlib**: Modern file path handling (Python standard library)
- **json**: Hook data processing (Python standard library)
- **uv**: Python package manager and script runner
- **random**: Sound variation selection (Python standard library)

## Troubleshooting

### Common Issues

1. **No sound playback**
   - Check if pygame is installed: `uv add pygame`
   - Verify sound files exist in `sounds/alfred/` directory
   - Check system audio settings and volume
   - Monitor debug logs for audio loading errors

2. **Wrong sounds for operations**
   - Verify `sound_mapping.json` configuration
   - Check file extensions and command patterns in debug logs
   - Ensure Alfred sound files match mapping names

3. **Handler startup failures**
   - Confirm Python 3.13+ compatibility
   - Check file permissions on handler.py
   - Review module import errors in debug logs

### Debug Information

All operations are logged to `.claude/hooks/voice_notifications/debug.log` with comprehensive context:

- Hook event details with timestamps, emojis, and context information
- Sound mapping results showing pattern matches and fallback logic
- Audio file loading attempts with success/failure status and file paths
- pygame initialization and playback status with timing information
- Context-aware pattern matching details for file operations and bash commands
- Notification categorization (permission requests vs idle timeouts vs general)
- SubagentStop event tracking with stop hook status monitoring

### Log Analysis Commands

**View recent voice activity:**
```bash
tail -20 .claude/hooks/voice_notifications/debug.log
```

**Monitor live notifications:**
```bash
tail -f .claude/hooks/voice_notifications/debug.log | grep "🎵\|🔔\|🤖"
```

**Find audio playback errors:**
```bash
grep "❌\|ERROR" .claude/hooks/voice_notifications/debug.log
```

**Track context-aware mappings:**
```bash
grep "Context-aware mapping\|context pattern" .claude/hooks/voice_notifications/debug.log
```

**Analyze notification categorization:**
```bash
grep "Notification type\|NOTIFICATION EVENT" .claude/hooks/voice_notifications/debug.log
```

### Sound File Management

**Check Alfred sound collection:**
```bash
ls -la .claude/hooks/voice_notifications/sounds/alfred/
```

**Verify sound mapping matches:**
```bash
python -c "
import json
mapping = json.load(open('.claude/hooks/voice_notifications/sound_mapping.json'))
print('Total mappings:', len(mapping))
print('Hook events:', list(mapping['hook_events'].keys()))
print('Tools:', list(mapping['tools'].keys()))
"
```

**Test individual sound files:**
```bash
# Play specific sound manually (requires pygame)
python -c "
import pygame
pygame.mixer.init()
sound = pygame.mixer.Sound('.claude/hooks/voice_notifications/sounds/alfred/task_complete.mp3')
sound.play()
import time; time.sleep(2)
"
```