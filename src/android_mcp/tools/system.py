"""System information tools for MCP."""

from typing import Any
from android_mcp.tools.device import get_adb_client


async def adb_get_screen_size(serial: str) -> dict[str, int]:
    """Get the screen resolution of the device.

    Args:
        serial: Device serial number

    Returns:
        Dictionary with width and height.
    """
    client = get_adb_client()
    return client.get_screen_size(serial)


async def adb_get_battery(serial: str) -> dict[str, Any]:
    """Get battery status of the device.

    Args:
        serial: Device serial number

    Returns:
        Battery information including level, status, etc.
    """
    client = get_adb_client()
    return client.get_battery(serial)


async def adb_get_properties(serial: str, keys: list[str] = None) -> dict[str, str]:
    """Get system properties from the device.

    Args:
        serial: Device serial number
        keys: Optional list of property keys to retrieve

    Returns:
        Dictionary of property key-value pairs.
    """
    client = get_adb_client()
    info = client.get_device_info(serial)
    if keys:
        return {k: v for k, v in info.items() if k in keys}
    return info