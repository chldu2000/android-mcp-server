"""Application management tools for MCP."""

from typing import Any
from android_mcp.tools.device import get_adb_client


async def adb_install_app(serial: str, apk_path: str) -> str:
    """Install an APK on the device.

    Args:
        serial: Device serial number
        apk_path: Path to the APK file on local filesystem

    Returns:
        Installation result message.
    """
    client = get_adb_client()
    return client.install(serial, apk_path)


async def adb_uninstall_app(serial: str, package_name: str) -> str:
    """Uninstall an application from the device.

    Args:
        serial: Device serial number
        package_name: Package name of the app to uninstall

    Returns:
        Uninstall result message.
    """
    client = get_adb_client()
    return client.uninstall(serial, package_name)


async def adb_list_packages(serial: str) -> list[str]:
    """List all installed packages on the device.

    Args:
        serial: Device serial number

    Returns:
        List of package names.
    """
    client = get_adb_client()
    return client.list_packages(serial)


async def adb_start_app(serial: str, package_name: str, activity: str = None) -> str:
    """Start an application on the device.

    Args:
        serial: Device serial number
        package_name: Package name of the app to start
        activity: Optional activity name (e.g., '.MainActivity')

    Returns:
        Start result message.
    """
    client = get_adb_client()
    return client.start_app(serial, package_name, activity)


async def adb_stop_app(serial: str, package_name: str) -> str:
    """Force stop an application on the device.

    Args:
        serial: Device serial number
        package_name: Package name of the app to stop

    Returns:
        Stop result message.
    """
    client = get_adb_client()
    return client.stop_app(serial, package_name)