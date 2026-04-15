"""Screen control tools using scrcpy for MCP."""

from typing import Any
from android_mcp.scrcpy.client import ScrcpyClient
from android_mcp.scrcpy.control import ScrcpyControl


# Global scrcpy client instance
_scrcpy_client: ScrcpyClient | None = None


def get_scrcpy_client() -> ScrcpyClient:
    """Get or create the global scrcpy client instance."""
    global _scrcpy_client
    if _scrcpy_client is None:
        _scrcpy_client = ScrcpyClient()
    return _scrcpy_client


async def scrcpy_start(serial: str, bit_rate: int = 8000000) -> dict[str, Any]:
    """Start screen mirroring via scrcpy.

    Args:
        serial: Device serial number
        bit_rate: Video bit rate (default 8Mbps)

    Returns:
        Status including streaming port.
    """
    client = get_scrcpy_client()
    return client.start(serial, bit_rate)


async def scrcpy_stop() -> str:
    """Stop screen mirroring.

    Returns:
        Status message.
    """
    client = get_scrcpy_client()
    return client.stop()


async def scrcpy_screenshot(serial: str, output_path: str = "/sdcard/screenshot.png") -> str:
    """Take a screenshot from the device.

    Args:
        serial: Device serial number
        output_path: Path on device to save screenshot

    Returns:
        Screenshot file path.
    """
    client = get_scrcpy_client()
    return client.screenshot(serial, output_path)


async def scrcpy_control(
    serial: str,
    action: str,
    params: dict[str, Any]
) -> str:
    """Send control command to scrcpy.

    Args:
        serial: Device serial number
        action: Action type ('tap', 'swipe', 'key', 'text')
        params: Action parameters

    Returns:
        Result message.
    """
    # Note: scrcpy control via network requires the device to be in TCP/IP mode
    # For now, we delegate most controls back to ADB input
    from android_mcp.tools.input import adb_tap, adb_swipe, adb_input_text, adb_press_key

    if action == "tap":
        x = params.get("x", 0)
        y = params.get("y", 0)
        return await adb_tap(serial, x, y)

    elif action == "swipe":
        x1 = params.get("x1", 0)
        y1 = params.get("y1", 0)
        x2 = params.get("x2", 0)
        y2 = params.get("y2", 0)
        duration = params.get("duration", 300)
        return await adb_swipe(serial, x1, y1, x2, y2, duration)

    elif action == "key":
        keycode = params.get("keycode", 0)
        return await adb_press_key(serial, keycode)

    elif action == "text":
        text = params.get("text", "")
        return await adb_input_text(serial, text)

    return f"Unknown action: {action}"