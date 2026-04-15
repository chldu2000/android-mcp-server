"""Device management tools for MCP."""

from typing import Any
from android_mcp.adb.client import ADBClient


# Global ADB client instance
_adb_client: ADBClient | None = None


def get_adb_client() -> ADBClient:
    """Get or create the global ADB client instance."""
    global _adb_client
    if _adb_client is None:
        _adb_client = ADBClient()
    return _adb_client


async def adb_list_devices() -> list[dict[str, str]]:
    """List all connected Android devices.

    Returns:
        List of devices with serial and state.
    """
    client = get_adb_client()
    devices = client.list_devices()
    return devices


async def adb_device_info(serial: str) -> dict[str, Any]:
    """Get detailed information about a specific device.

    Args:
        serial: Device serial number

    Returns:
        Device properties and information.
    """
    client = get_adb_client()
    return client.get_device_info(serial)