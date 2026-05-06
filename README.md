# Android MCP Server

MCP server providing ADB and scrcpy capabilities for Android device control. Built with FastMCP.

*Assisted by Minimax Model via Claude Code.*

## Features

- **Device Management**: List devices, get device info
- **App Management**: Install/uninstall apps, start/stop apps, list packages
- **File Operations**: Push/pull files between device and host
- **Shell Execution**: Run shell commands on device, exec-out for binary output
- **Input Control**: Tap, swipe, input text, press keys
- **System Info**: Screen size, battery status, system properties
- **Screen Control**: Screen mirroring and control via scrcpy, screenshot via exec-out
- **UI Element Finding**: Dump UI hierarchy, find elements by attributes

## Install

```bash
uv add android-mcp-server
```

Or install from source:

```bash
# Clone the repo, then install
git clone https://github.com/chldu2000/android-mcp-server.git
cd android-mcp-server
uv pip install -e .
uv run python -m android_mcp.main
```

## Add MCP Server

### Claude Code

```bash
claude mcp add android uv run -- python -m android_mcp.main --cwd /Path/to/workdir
```

### Other MCP Clients

The server can be run with:

```bash
uv run python -m android_mcp.main
```

## Tools

### Device Management

| Tool | Description |
|------|-------------|
| `adb_list_devices` | List all connected Android devices |
| `adb_device_info` | Get detailed device information |

### App Management

| Tool | Description |
|------|-------------|
| `adb_install_app` | Install an APK |
| `adb_uninstall_app` | Uninstall an application |
| `adb_list_packages` | List installed packages |
| `adb_start_app` | Start an application |
| `adb_stop_app` | Force stop an application |

### File Operations

| Tool | Description |
|------|-------------|
| `adb_pull_file` | Pull file from device |
| `adb_push_file` | Push file to device |

### Shell

| Tool | Description |
|------|-------------|
| `adb_shell` | Execute shell command |
| `adb_exec_out` | Execute command via exec-out (for binary output) |

### Input Control

| Tool | Description |
|------|-------------|
| `adb_tap` | Tap at coordinates |
| `adb_swipe` | Swipe gesture |
| `adb_input_text` | Input text |
| `adb_press_key` | Press key event |

### System Info

| Tool | Description |
|------|-------------|
| `adb_get_screen_size` | Get screen resolution |
| `adb_get_battery` | Get battery status |
| `adb_get_properties` | Get system properties |

### Screen Control (scrcpy)

| Tool | Description |
|------|-------------|
| `scrcpy_start` | Start screen mirroring |
| `scrcpy_stop` | Stop screen mirroring |
| `scrcpy_screenshot` | Take screenshot |
| `scrcpy_control` | Send control command |
| `adb_screencap` | Capture screenshot via exec-out |

### UI Elements

| Tool | Description |
|------|-------------|
| `adb_dump_ui_tree` | Dump UI hierarchy tree |
| `adb_find_element` | Find UI elements by attributes |

## Device Connection

### USB Devices

Connect via USB and ensure USB debugging is enabled on the device.

### Network Devices

For TCP/IP connection:

1. Enable TCP/IP mode on device:
   ```bash
   adb tcpip 5555
   ```

2. Find device IP:
   ```bash
   adb shell ip route
   ```

3. Connect:
   ```bash
   adb connect <device-ip>:5555
   ```

## Dependencies

- [fastmcp](https://github.com/jlowin/fastmcp) - MCP server framework
- [scrcpy](https://github.com/Genymobile/scrcpy) - Screen mirroring (must be installed separately)
- [uiautomator2](https://github.com/openatx/uiautomator2) - uiautomator2 Python wrapper
