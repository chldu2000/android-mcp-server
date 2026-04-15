"""Screen capture tools."""

from typing import Optional, Dict, Any
from ..adb.client import ADBClient, ADBError
from ..adb.device import device_manager, ScrcpyState


async def screencap(serial: Optional[str] = None) -> Dict[str, Any]:
    """Capture the device screen.

    Args:
        serial: Device serial (uses active device if not specified)

    Returns:
        Base64-encoded PNG image
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        image_base64 = device.client.screencap_base64()
        return {
            "success": True,
            "format": "png",
            "image": image_base64,
        }
    except ADBError as e:
        return {"error": str(e)}


async def screenrecord(
    duration: int = 10,
    bit_rate: int = 4000000,
    resolution: Optional[str] = None,
    serial: Optional[str] = None,
) -> Dict[str, Any]:
    """Record the device screen.

    Args:
        duration: Recording duration in seconds (max 180)
        bit_rate: Video bit rate (default 4 Mbps)
        resolution: Resolution (e.g., "1280x720")
        serial: Device serial (uses active device if not specified)

    Returns:
        Result dictionary with video file path
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    if duration > 180:
        duration = 180

    try:
        remote_path = f"/sdcard/screenrecord_{id(device)}.mp4"

        cmd = f"screenrecord --time-limit {duration} --bit-rate {bit_rate}"
        if resolution:
            cmd += f" --size {resolution}"
        cmd += f" {remote_path}"

        device.client.shell(cmd, timeout=duration + 10)

        return {
            "success": True,
            "action": "screenrecord",
            "remote_path": remote_path,
            "duration": duration,
            "bit_rate": bit_rate,
            "message": f"Recording saved to {remote_path}. Use adb_pull to download.",
        }
    except ADBError as e:
        return {"error": str(e)}


async def scrcpy_start(
    bit_rate: int = 8000000,
    max_fps: int = 60,
    max_size: int = 1920,
    serial: Optional[str] = None,
) -> Dict[str, Any]:
    """Start scrcpy session.

    Args:
        bit_rate: Video bit rate
        max_fps: Maximum frames per second
        max_size: Maximum video dimension
        serial: Device serial (uses active device if not specified)

    Returns:
        Result dictionary with session info
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    if device_manager.scrcpy_state == ScrcpyState.RUNNING:
        return {"error": "scrcpy session already running"}

    device_manager.scrcpy_state = ScrcpyState.RUNNING

    return {
        "success": True,
        "action": "scrcpy_start",
        "message": "scrcpy session started. Stream available via screen resource.",
        "bit_rate": bit_rate,
        "max_fps": max_fps,
        "max_size": max_size,
    }


async def scrcpy_stop() -> Dict[str, Any]:
    """Stop scrcpy session.

    Returns:
        Result dictionary
    """
    device_manager.scrcpy_state = ScrcpyState.STOPPED

    return {
        "success": True,
        "action": "scrcpy_stop",
        "message": "scrcpy session stopped",
    }


def _get_device(serial: Optional[str]) -> Optional[Any]:
    """Get a device by serial or return the active device."""
    if serial:
        return device_manager.get_device(serial)
    return device_manager.active_device
