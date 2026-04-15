"""Device management tools."""

from typing import List, Dict, Any, Optional
from ..adb.client import ADBClient, ADBError
from ..adb.device import device_manager, Device


async def list_devices() -> List[Dict[str, Any]]:
    """List all connected Android devices.

    Returns:
        List of device information dictionaries
    """
    devices = device_manager.refresh_devices()
    return [device.to_dict() for device in devices.values()]


async def connect_device(host: str, port: int = 5555) -> Dict[str, Any]:
    """Connect to a device over TCP/IP.

    Args:
        host: Device IP address
        port: ADB port (default 5555)

    Returns:
        Result dictionary with success status
    """
    client = ADBClient()
    success = client.connect(host, port)
    device_manager.refresh_devices()

    return {
        "success": success,
        "address": f"{host}:{port}",
        "message": "Connected" if success else "Connection failed",
    }


async def disconnect_device(host: str, port: int = 5555) -> Dict[str, Any]:
    """Disconnect from a TCP/IP device.

    Args:
        host: Device IP address
        port: ADB port (default 5555)

    Returns:
        Result dictionary with success status
    """
    client = ADBClient()
    success = client.disconnect(host, port)
    device_manager.refresh_devices()

    return {
        "success": success,
        "address": f"{host}:{port}",
        "message": "Disconnected" if success else "Disconnect failed",
    }


async def set_active_device(serial: str) -> Dict[str, Any]:
    """Set the active device for single-device operations.

    Args:
        serial: Device serial number

    Returns:
        Result dictionary with success status
    """
    success = device_manager.set_active_device(serial)
    device = device_manager.get_device(serial)

    return {
        "success": success,
        "serial": serial,
        "device": device.to_dict() if device else None,
        "message": "Device set as active" if success else "Device not found",
    }


async def get_device_info(serial: Optional[str] = None) -> Dict[str, Any]:
    """Get detailed information about a device.

    Args:
        serial: Device serial number (uses active device if not specified)

    Returns:
        Device information dictionary
    """
    if serial:
        device = device_manager.get_device(serial)
    else:
        device = device_manager.active_device

    if not device:
        return {"error": "No device available"}

    try:
        client = device.client
        model = client.get_model()
        manufacturer = client.get_manufacturer()
        android_version = client.get_android_version()
        sdk_version = client.get_sdk_version()
        width, height = client.wm_size()

        return {
            "serial": device.serial,
            "state": device.state.value,
            "model": model,
            "manufacturer": manufacturer,
            "android_version": android_version,
            "sdk_version": sdk_version,
            "screen_size": {"width": width, "height": height},
            "product": device.product,
        }
    except ADBError as e:
        return {"error": str(e), "serial": device.serial}
