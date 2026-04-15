"""Main entry point for the Android MCP Server."""

from fastmcp import FastMCP

from android_mcp.tools.device import (
    adb_list_devices as _adb_list_devices,
    adb_device_info as _adb_device_info,
)
from android_mcp.tools.app import (
    adb_install_app as _adb_install_app,
    adb_uninstall_app as _adb_uninstall_app,
    adb_list_packages as _adb_list_packages,
    adb_start_app as _adb_start_app,
    adb_stop_app as _adb_stop_app,
)
from android_mcp.tools.file import (
    adb_pull_file as _adb_pull_file,
    adb_push_file as _adb_push_file,
)
from android_mcp.tools.shell import adb_shell as _adb_shell
from android_mcp.tools.input import (
    adb_tap as _adb_tap,
    adb_swipe as _adb_swipe,
    adb_input_text as _adb_input_text,
    adb_press_key as _adb_press_key,
)
from android_mcp.tools.system import (
    adb_get_screen_size as _adb_get_screen_size,
    adb_get_battery as _adb_get_battery,
    adb_get_properties as _adb_get_properties,
)
from android_mcp.tools.screen import (
    scrcpy_start as _scrcpy_start,
    scrcpy_stop as _scrcpy_stop,
    scrcpy_screenshot as _scrcpy_screenshot,
    scrcpy_control as _scrcpy_control,
)


mcp = FastMCP("android-mcp-server")


# Device management tools
@mcp.tool()
async def adb_list_devices():
    """List all connected Android devices."""
    return await _adb_list_devices()


@mcp.tool()
async def adb_device_info(serial: str):
    """Get detailed information about a specific device."""
    return await _adb_device_info(serial)


# App management tools
@mcp.tool()
async def adb_install_app(serial: str, apk_path: str):
    """Install an APK on the device."""
    return await _adb_install_app(serial, apk_path)


@mcp.tool()
async def adb_uninstall_app(serial: str, package_name: str):
    """Uninstall an application from the device."""
    return await _adb_uninstall_app(serial, package_name)


@mcp.tool()
async def adb_list_packages(serial: str):
    """List all installed packages on the device."""
    return await _adb_list_packages(serial)


@mcp.tool()
async def adb_start_app(serial: str, package_name: str, activity: str = None):
    """Start an application on the device."""
    return await _adb_start_app(serial, package_name, activity)


@mcp.tool()
async def adb_stop_app(serial: str, package_name: str):
    """Force stop an application on the device."""
    return await _adb_stop_app(serial, package_name)


# File operation tools
@mcp.tool()
async def adb_pull_file(serial: str, device_path: str, local_path: str):
    """Pull a file from the device to local filesystem."""
    return await _adb_pull_file(serial, device_path, local_path)


@mcp.tool()
async def adb_push_file(serial: str, local_path: str, device_path: str):
    """Push a file from local filesystem to the device."""
    return await _adb_push_file(serial, local_path, device_path)


# Shell tools
@mcp.tool()
async def adb_shell(serial: str, command: str):
    """Execute a shell command on the device."""
    return await _adb_shell(serial, command)


# Input control tools
@mcp.tool()
async def adb_tap(serial: str, x: int, y: int):
    """Simulate a tap at the specified coordinates."""
    return await _adb_tap(serial, x, y)


@mcp.tool()
async def adb_swipe(serial: str, x1: int, y1: int, x2: int, y2: int, duration: int = 300):
    """Simulate a swipe gesture."""
    return await _adb_swipe(serial, x1, y1, x2, y2, duration)


@mcp.tool()
async def adb_input_text(serial: str, text: str):
    """Input text on the device."""
    return await _adb_input_text(serial, text)


@mcp.tool()
async def adb_press_key(serial: str, keycode: int):
    """Press a key event."""
    return await _adb_press_key(serial, keycode)


# System info tools
@mcp.tool()
async def adb_get_screen_size(serial: str):
    """Get the screen resolution of the device."""
    return await _adb_get_screen_size(serial)


@mcp.tool()
async def adb_get_battery(serial: str):
    """Get battery status of the device."""
    return await _adb_get_battery(serial)


@mcp.tool()
async def adb_get_properties(serial: str, keys: list[str] = None):
    """Get system properties from the device."""
    return await _adb_get_properties(serial, keys)


# Screen control tools
@mcp.tool()
async def scrcpy_start(serial: str, bit_rate: int = 8000000):
    """Start screen mirroring via scrcpy."""
    return await _scrcpy_start(serial, bit_rate)


@mcp.tool()
async def scrcpy_stop():
    """Stop screen mirroring."""
    return await _scrcpy_stop()


@mcp.tool()
async def scrcpy_screenshot(serial: str, output_path: str = "/sdcard/screenshot.png"):
    """Take a screenshot from the device."""
    return await _scrcpy_screenshot(serial, output_path)


@mcp.tool()
async def scrcpy_control(serial: str, action: str, params: dict):
    """Send control command to scrcpy."""
    return await _scrcpy_control(serial, action, params)


if __name__ == "__main__":
    mcp.run()