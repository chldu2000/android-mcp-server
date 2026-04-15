"""System information tools with whitelisted commands."""

import re
from typing import Optional, Dict, Any, List, Set
from ..adb.client import ADBError
from ..adb.device import device_manager


# Whitelist patterns for allowed getprop properties
ALLOWED_GETPROP_PATTERNS: Set[str] = {
    "ro.build.*",
    "ro.product.*",
    "ro.version.*",
    "ro.system.*",
    "ro.hardware.*",
    "ro.boardplatform.*",
    "ro.bootloader.*",
    "ro.debug.*",
    "persist.*",
}

# Whitelist for dumpsys services
ALLOWED_DUMPSYS_SERVICES: Set[str] = {
    "window",
    "activity",
    "package",
    "meminfo",
    "cpuinfo",
    "display",
    "battery",
    "power",
    "window",
    "statusbar",
    "notification",
}


def _matches_pattern(value: str, patterns: Set[str]) -> bool:
    """Check if a value matches any of the patterns.

    Args:
        value: String to check
        patterns: Set of glob-style patterns

    Returns:
        True if value matches any pattern
    """
    for pattern in patterns:
        if "*" in pattern:
            # Convert glob to regex
            regex_pattern = pattern.replace(".", r"\.").replace("*", ".*")
            if re.match(f"^{regex_pattern}$", value):
                return True
        elif value == pattern:
            return True
    return False


async def getprop(property_name: Optional[str] = None, serial: Optional[str] = None) -> Dict[str, Any]:
    """Get system properties.

    Args:
        property_name: Property name (e.g., ro.build.version.sdk)
                       If None, returns all allowed properties
        serial: Device serial (uses active device if not specified)

    Returns:
        Property value(s)
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        if property_name:
            # Check whitelist
            if not _matches_pattern(property_name, ALLOWED_GETPROP_PATTERNS):
                return {"error": f"Property not allowed: {property_name}"}

            value = device.client.getprop(property_name)
            return {"success": True, "property": property_name, "value": value}
        else:
            # Return all allowed properties
            all_props = device.client.getprop()
            filtered = {}
            for line in all_props.strip().split("\n"):
                if ":[" in line:
                    match = re.match(r"\[(.*?)\]:\[(.*?)\]", line)
                    if match:
                        prop_name, prop_value = match.groups()
                        if _matches_pattern(prop_name, ALLOWED_GETPROP_PATTERNS):
                            filtered[prop_name] = prop_value
            return {"success": True, "properties": filtered}
    except ADBError as e:
        return {"error": str(e)}


async def dumpsys(service: Optional[str] = None, serial: Optional[str] = None) -> Dict[str, Any]:
    """Get system service information.

    Args:
        service: Service name (e.g., window, activity, package)
                 If None, returns allowed services overview
        serial: Device serial (uses active device if not specified)

    Returns:
        Service information
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        if service:
            # Check whitelist
            if service.lower() not in ALLOWED_DUMPSYS_SERVICES:
                return {"error": f"Service not allowed: {service}"}

            info = device.client.dumpsys(service)
            return {"success": True, "service": service, "info": info}
        else:
            # Return list of allowed services
            return {
                "success": True,
                "allowed_services": sorted(ALLOWED_DUMPSYS_SERVICES),
            }
    except ADBError as e:
        return {"error": str(e)}


async def wm_size(serial: Optional[str] = None) -> Dict[str, Any]:
    """Get the device screen size.

    Args:
        serial: Device serial (uses active device if not specified)

    Returns:
        Screen size information
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        width, height = device.client.wm_size()
        return {
            "success": True,
            "width": width,
            "height": height,
            "orientation": "landscape" if width > height else "portrait",
        }
    except ADBError as e:
        return {"error": str(e)}


async def ps(serial: Optional[str] = None) -> Dict[str, Any]:
    """Get process list.

    Args:
        serial: Device serial (uses active device if not specified)

    Returns:
        List of running processes
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        output = device.client.shell("ps")
        processes = []
        for line in output.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 9:
                processes.append({
                    "user": parts[0],
                    "pid": parts[1],
                    "name": parts[-1],
                })
        return {
            "success": True,
            "processes": processes,
            "count": len(processes),
        }
    except ADBError as e:
        return {"error": str(e)}


async def netstat(serial: Optional[str] = None) -> Dict[str, Any]:
    """Get network statistics.

    Args:
        serial: Device serial (uses active device if not specified)

    Returns:
        Network statistics
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        output = device.client.shell("netstat")
        return {
            "success": True,
            "output": output,
        }
    except ADBError as e:
        return {"error": str(e)}


def _get_device(serial: Optional[str]) -> Optional[Any]:
    """Get a device by serial or return the active device."""
    if serial:
        return device_manager.get_device(serial)
    return device_manager.active_device
