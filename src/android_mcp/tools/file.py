"""File operation tools for MCP."""

from android_mcp.tools.device import get_adb_client


async def adb_pull_file(serial: str, device_path: str, local_path: str) -> str:
    """Pull a file from the device to local filesystem.

    Args:
        serial: Device serial number
        device_path: Path to the file on the device
        local_path: Local destination path

    Returns:
        Pull result message.
    """
    client = get_adb_client()
    return client.pull_file(serial, device_path, local_path)


async def adb_push_file(serial: str, local_path: str, device_path: str) -> str:
    """Push a file from local filesystem to the device.

    Args:
        serial: Device serial number
        local_path: Path to the local file
        device_path: Destination path on the device

    Returns:
        Push result message.
    """
    client = get_adb_client()
    return client.push_file(serial, local_path, device_path)