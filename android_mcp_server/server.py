"""MCP Server implementation using fastmcp."""

from typing import Optional
from fastmcp import FastMCP

from .adb.device import device_manager
from .tools import device as device_tools
from .tools import input as input_tools
from .tools import app as app_tools
from .tools import file as file_tools
from .tools import system as system_tools
from .tools import screen as screen_tools


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server.

    Returns:
        Configured FastMCP instance
    """
    mcp = FastMCP(
        name="android-mcp-server",
    )

    # Register device management tools
    @mcp.tool()
    async def adb_devices():
        """List all connected Android devices."""
        return await device_tools.list_devices()

    @mcp.tool()
    async def adb_connect(host: str, port: int = 5555):
        """Connect to a device over TCP/IP."""
        return await device_tools.connect_device(host, port)

    @mcp.tool()
    async def adb_disconnect(host: str, port: int = 5555):
        """Disconnect from a TCP/IP device."""
        return await device_tools.disconnect_device(host, port)

    @mcp.tool()
    async def adb_set_device(serial: str):
        """Set the active device for single-device operations."""
        return await device_tools.set_active_device(serial)

    @mcp.tool()
    async def adb_device_info(serial: Optional[str] = None):
        """Get detailed information about a device."""
        return await device_tools.get_device_info(serial)

    # Register input tools
    @mcp.tool()
    async def adb_input_tap(x: int, y: int, serial: Optional[str] = None):
        """Simulate a tap at the given coordinates."""
        return await input_tools.input_tap(x, y, serial)

    @mcp.tool()
    async def adb_input_swipe(
        x1: int, y1: int, x2: int, y2: int, duration: int = 300, serial: Optional[str] = None
    ):
        """Simulate a swipe gesture."""
        return await input_tools.input_swipe(x1, y1, x2, y2, duration, serial)

    @mcp.tool()
    async def adb_input_text(text: str, serial: Optional[str] = None):
        """Simulate text input."""
        return await input_tools.input_text(text, serial)

    @mcp.tool()
    async def adb_input_keyevent(keycode: int, serial: Optional[str] = None):
        """Simulate a key event.

        Common keycodes:
        - 3: HOME
        - 4: BACK
        - 24: VOLUME_UP
        - 25: VOLUME_DOWN
        - 26: POWER
        - 66: ENTER
        - 67: DEL
        - 187: APP_SWITCH
        """
        return await input_tools.input_keyevent(keycode, serial)

    @mcp.tool()
    async def adb_input_scroll(x: int, y: int, dx: int, dy: int, serial: Optional[str] = None):
        """Simulate a scroll gesture."""
        return await input_tools.input_scroll(x, y, dx, dy, serial)

    # Register app management tools
    @mcp.tool()
    async def adb_install(apk_path: str, reinstall: bool = False, serial: Optional[str] = None):
        """Install an APK on the device."""
        return await app_tools.install_app(apk_path, reinstall, serial)

    @mcp.tool()
    async def adb_uninstall(package_name: str, keep_data: bool = False, serial: Optional[str] = None):
        """Uninstall an app from the device."""
        return await app_tools.uninstall_app(package_name, keep_data, serial)

    @mcp.tool()
    async def adb_list_packages(filter_type: Optional[str] = None, serial: Optional[str] = None):
        """List installed packages.

        Filter types:
        - "-3": third party packages only
        - "-s": system packages only
        """
        return await app_tools.list_packages(filter_type, serial)

    @mcp.tool()
    async def adb_start_app(package_name: str, activity: Optional[str] = None, serial: Optional[str] = None):
        """Start an application."""
        return await app_tools.start_app(package_name, activity, serial)

    @mcp.tool()
    async def adb_stop_app(package_name: str, serial: Optional[str] = None):
        """Force stop an application."""
        return await app_tools.stop_app(package_name, serial)

    @mcp.tool()
    async def adb_clear_app(package_name: str, serial: Optional[str] = None):
        """Clear application data."""
        return await app_tools.clear_app(package_name, serial)

    # Register file operation tools
    @mcp.tool()
    async def adb_push(local_path: str, remote_path: str, serial: Optional[str] = None):
        """Push a file to the device."""
        return await file_tools.push_file(local_path, remote_path, serial)

    @mcp.tool()
    async def adb_pull(remote_path: str, local_path: str, serial: Optional[str] = None):
        """Pull a file from the device."""
        return await file_tools.pull_file(remote_path, local_path, serial)

    # Register system info tools
    @mcp.tool()
    async def adb_getprop(property_name: Optional[str] = None, serial: Optional[str] = None):
        """Get system properties.

        Without arguments, returns allowed properties.
        With a property name, returns that specific property.
        Allowed patterns: ro.build.*, ro.product.*, ro.version.*
        """
        return await system_tools.getprop(property_name, serial)

    @mcp.tool()
    async def adb_dumpsys(service: Optional[str] = None, serial: Optional[str] = None):
        """Get system service information.

        Allowed services: window, activity, package, meminfo, cpuinfo,
        display, battery, power, statusbar, notification
        """
        return await system_tools.dumpsys(service, serial)

    @mcp.tool()
    async def adb_wm_size(serial: Optional[str] = None):
        """Get the device screen size."""
        return await system_tools.wm_size(serial)

    @mcp.tool()
    async def adb_ps(serial: Optional[str] = None):
        """Get process list."""
        return await system_tools.ps(serial)

    @mcp.tool()
    async def adb_netstat(serial: Optional[str] = None):
        """Get network statistics."""
        return await system_tools.netstat(serial)

    # Register screen tools
    @mcp.tool()
    async def adb_screencap(serial: Optional[str] = None):
        """Capture the device screen and return as base64 PNG."""
        return await screen_tools.screencap(serial)

    @mcp.tool()
    async def adb_screenrecord(
        duration: int = 10,
        bit_rate: int = 4000000,
        resolution: Optional[str] = None,
        serial: Optional[str] = None,
    ):
        """Record the device screen.

        Recording is saved to /sdcard/ on the device.
        Use adb_pull to download the video file.
        Maximum duration is 180 seconds.
        """
        return await screen_tools.screenrecord(duration, bit_rate, resolution, serial)

    @mcp.tool()
    async def scrcpy_start(
        bit_rate: int = 8000000,
        max_fps: int = 60,
        max_size: int = 1920,
        serial: Optional[str] = None,
    ):
        """Start a scrcpy session for real-time screen streaming."""
        return await screen_tools.scrcpy_start(bit_rate, max_fps, max_size, serial)

    @mcp.tool()
    async def scrcpy_stop():
        """Stop the scrcpy session."""
        return await screen_tools.scrcpy_stop()

    # Register resources
    @mcp.resource("device://list")
    async def device_list_resource():
        """List all connected devices as a resource."""
        devices = device_manager.refresh_devices()
        return "\n".join([f"- {d.display_name}: {d.serial} ({d.state.value})" for d in devices.values()])

    @mcp.resource("device://{serial}")
    async def device_resource(serial: str):
        """Get information about a specific device."""
        device = device_manager.get_device(serial)
        if not device:
            return f"Device {serial} not found"
        info = await device_tools.get_device_info(serial)
        return str(info)

    @mcp.resource("screen://{serial}")
    async def screen_resource(serial: str):
        """Get current screen screenshot for a device."""
        result = await screen_tools.screencap(serial)
        if "error" in result:
            return f"Error: {result['error']}"
        return f"data:image/png;base64,{result['image']}"

    return mcp
