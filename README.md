# android-mcp-server

MCP Server for Android device control via ADB and scrcpy. Allows external LLMs to interact with Android devices through a well-defined tool interface.

Assisted by Minimax Model via Claude Code.

## Setup

```bash
uv sync
```

## Add to Agent Tools

### Claude Code

```bash
claude mcp add android -- uv run --directory /path/to/android-mcp-server android-mcp
```

Or edit `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "android": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/android-mcp-server", "android-mcp"]
    }
  }
}
```

### OpenCode

Edit OpenCode's config file (usually `~/.opencode/config.json` or project config):

```json
{
  "mcpServers": {
    "android": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/android-mcp-server", "android-mcp"]
    }
  }
}
```

### Other MCP Clients

For any MCP-compatible agent, add to their MCP settings:

```json
{
  "mcpServers": {
    "android": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/android-mcp-server", "android-mcp"]
    }
  }
}
```

Or if using a virtualenv directly:

```json
{
  "mcpServers": {
    "android": {
      "command": "python",
      "args": ["-m", "android_mcp_server"],
      "cwd": "/path/to/android-mcp-server"
    }
  }
}
```

## Available Tools

### Device Management

- `adb_devices` - List connected devices
- `adb_connect` - Connect via TCP/IP
- `adb_disconnect` - Disconnect TCP/IP device
- `adb_set_device` - Set active device
- `adb_device_info` - Get device details

### Input Simulation

- `adb_input_tap` - Tap at coordinates
- `adb_input_swipe` - Swipe gesture
- `adb_input_text` - Input text
- `adb_input_keyevent` - Send key event
- `adb_input_scroll` - Scroll gesture

### App Management

- `adb_install` - Install APK
- `adb_uninstall` - Uninstall app
- `adb_list_packages` - List installed packages
- `adb_start_app` - Launch app
- `adb_stop_app` - Force stop app
- `adb_clear_app` - Clear app data

### File Operations

- `adb_push` - Push file to device
- `adb_pull` - Pull file from device

### System Info

- `adb_getprop` - Get system properties
- `adb_dumpsys` - Get system service info
- `adb_wm_size` - Get screen size
- `adb_ps` - Process list
- `adb_netstat` - Network statistics
- `adb_dump_ui_tree` - Dump UI hierarchy tree

### Screen Capture

- `adb_screencap` - Screenshot (base64 PNG)
- `adb_screenrecord` - Record screen
- `scrcpy_start` - Start scrcpy session
- `scrcpy_stop` - Stop scrcpy session

## Resources

- `device://list` - List all devices
- `device://{serial}` - Device info
- `screen://{serial}` - Current screen screenshot
