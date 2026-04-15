"""Application management tools."""

from typing import Optional, Dict, Any, List
from ..adb.client import ADBError
from ..adb.device import device_manager


async def install_app(apk_path: str, reinstall: bool = False, serial: Optional[str] = None) -> Dict[str, Any]:
    """Install an APK on the device.

    Args:
        apk_path: Path to the APK file
        reinstall: If True, reinstall and keep data
        serial: Device serial (uses active device if not specified)

    Returns:
        Result dictionary
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        success = device.client.install(apk_path, reinstall=reinstall)
        return {
            "success": success,
            "action": "install",
            "apk_path": apk_path,
            "reinstall": reinstall,
        }
    except ADBError as e:
        return {"error": str(e), "action": "install", "apk_path": apk_path}


async def uninstall_app(package_name: str, keep_data: bool = False, serial: Optional[str] = None) -> Dict[str, Any]:
    """Uninstall an app from the device.

    Args:
        package_name: Package name (e.g., com.example.app)
        keep_data: If True, keep app data
        serial: Device serial (uses active device if not specified)

    Returns:
        Result dictionary
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        success = device.client.uninstall(package_name, keep_data=keep_data)
        return {
            "success": success,
            "action": "uninstall",
            "package": package_name,
            "keep_data": keep_data,
        }
    except ADBError as e:
        return {"error": str(e)}


async def list_packages(filter_type: Optional[str] = None, serial: Optional[str] = None) -> Dict[str, Any]:
    """List installed packages.

    Args:
        filter_type: Optional filter type (e.g., "-3" for third party, "-s" for system)
        serial: Device serial (uses active device if not specified)

    Returns:
        Result dictionary with list of packages
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        packages = device.client.list_packages(filter_type)
        return {
            "success": True,
            "packages": packages,
            "count": len(packages),
        }
    except ADBError as e:
        return {"error": str(e)}


async def start_app(package_name: str, activity: Optional[str] = None, serial: Optional[str] = None) -> Dict[str, Any]:
    """Start an application.

    Args:
        package_name: Package name
        activity: Optional activity name (if None, launches main activity)
        serial: Device serial (uses active device if not specified)

    Returns:
        Result dictionary
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        device.client.start_app(package_name, activity)
        return {
            "success": True,
            "action": "start_app",
            "package": package_name,
            "activity": activity,
        }
    except ADBError as e:
        return {"error": str(e)}


async def stop_app(package_name: str, serial: Optional[str] = None) -> Dict[str, Any]:
    """Force stop an application.

    Args:
        package_name: Package name
        serial: Device serial (uses active device if not specified)

    Returns:
        Result dictionary
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        device.client.stop_app(package_name)
        return {
            "success": True,
            "action": "stop_app",
            "package": package_name,
        }
    except ADBError as e:
        return {"error": str(e)}


async def clear_app(package_name: str, serial: Optional[str] = None) -> Dict[str, Any]:
    """Clear application data.

    Args:
        package_name: Package name
        serial: Device serial (uses active device if not specified)

    Returns:
        Result dictionary
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        device.client.clear_app(package_name)
        return {
            "success": True,
            "action": "clear_app",
            "package": package_name,
        }
    except ADBError as e:
        return {"error": str(e)}


def _get_device(serial: Optional[str]) -> Optional[Any]:
    """Get a device by serial or return the active device."""
    if serial:
        return device_manager.get_device(serial)
    return device_manager.active_device
