"""Input control tools for MCP."""

from android_mcp.tools.device import get_adb_client


async def adb_tap(serial: str, x: int, y: int) -> str:
    """Simulate a tap at the specified coordinates.

    Args:
        serial: Device serial number
        x: X coordinate
        y: Y coordinate

    Returns:
        Command result.
    """
    client = get_adb_client()
    return client.tap(serial, x, y)


async def adb_swipe(
    serial: str,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    duration: int = 300
) -> str:
    """Simulate a swipe gesture.

    Args:
        serial: Device serial number
        x1: Start X coordinate
        y1: Start Y coordinate
        x2: End X coordinate
        y2: End Y coordinate
        duration: Duration in milliseconds

    Returns:
        Command result.
    """
    client = get_adb_client()
    return client.swipe(serial, x1, y1, x2, y2, duration)


async def adb_input_text(serial: str, text: str) -> str:
    """Input text on the device.

    Args:
        serial: Device serial number
        text: Text to input

    Returns:
        Command result.
    """
    client = get_adb_client()
    return client.input_text(serial, text)


async def adb_press_key(serial: str, keycode: int) -> str:
    """Press a key event.

    Args:
        serial: Device serial number
        keycode: Android keycode (e.g., 26 for POWER, 4 for BACK)

    Returns:
        Command result.
    """
    client = get_adb_client()
    return client.press_key(serial, keycode)