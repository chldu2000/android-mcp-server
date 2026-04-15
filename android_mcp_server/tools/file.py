"""File operation tools."""

import base64
from typing import Optional, Dict, Any
from ..adb.client import ADBError
from ..adb.device import device_manager


async def push_file(local_path: str, remote_path: str, serial: Optional[str] = None) -> Dict[str, Any]:
    """Push a file to the device.

    Args:
        local_path: Local file path
        remote_path: Remote file path on device
        serial: Device serial (uses active device if not specified)

    Returns:
        Result dictionary
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        device.client.push(local_path, remote_path)
        return {
            "success": True,
            "action": "push",
            "local_path": local_path,
            "remote_path": remote_path,
        }
    except ADBError as e:
        return {"error": str(e)}


async def pull_file(remote_path: str, local_path: str, serial: Optional[str] = None) -> Dict[str, Any]:
    """Pull a file from the device.

    Args:
        remote_path: Remote file path on device
        local_path: Local file path
        serial: Device serial (uses active device if not specified)

    Returns:
        Result dictionary with file content as base64 if no local_path specified
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        device.client.pull(remote_path, local_path)
        return {
            "success": True,
            "action": "pull",
            "remote_path": remote_path,
            "local_path": local_path,
        }
    except ADBError as e:
        return {"error": str(e)}


def _get_device(serial: Optional[str]) -> Optional[Any]:
    """Get a device by serial or return the active device."""
    if serial:
        return device_manager.get_device(serial)
    return device_manager.active_device
