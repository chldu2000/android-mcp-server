"""Input simulation tools."""

from typing import Optional, Dict, Any
from ..adb.client import ADBClient, ADBError
from ..adb.device import device_manager


async def input_tap(x: int, y: int, serial: Optional[str] = None) -> Dict[str, Any]:
    """Simulate a tap at the given coordinates.

    Args:
        x: X coordinate
        y: Y coordinate
        serial: Device serial (uses active device if not specified)

    Returns:
        Result dictionary
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        device.client.input_tap(x, y)
        return {"success": True, "action": "tap", "x": x, "y": y}
    except ADBError as e:
        return {"error": str(e)}


async def input_swipe(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    duration: int = 300,
    serial: Optional[str] = None,
) -> Dict[str, Any]:
    """Simulate a swipe gesture.

    Args:
        x1: Start X coordinate
        y1: Start Y coordinate
        x2: End X coordinate
        y2: End Y coordinate
        duration: Duration in milliseconds
        serial: Device serial (uses active device if not specified)

    Returns:
        Result dictionary
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        device.client.input_swipe(x1, y1, x2, y2, duration)
        return {
            "success": True,
            "action": "swipe",
            "from": {"x": x1, "y": y1},
            "to": {"x": x2, "y": y2},
            "duration": duration,
        }
    except ADBError as e:
        return {"error": str(e)}


async def input_text(text: str, serial: Optional[str] = None) -> Dict[str, Any]:
    """Simulate text input.

    Args:
        text: Text to input
        serial: Device serial (uses active device if not specified)

    Returns:
        Result dictionary
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        device.client.input_text(text)
        return {"success": True, "action": "text_input", "text": text}
    except ADBError as e:
        return {"error": str(e)}


async def input_keyevent(keycode: int, serial: Optional[str] = None) -> Dict[str, Any]:
    """Simulate a key event.

    Args:
        keycode: Android keycode (e.g., 3 for HOME, 4 for BACK, 66 for ENTER)
        serial: Device serial (uses active device if not specified)

    Returns:
        Result dictionary
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    # Keycode mapping for common keys
    KEYCODE_NAMES = {
        3: "HOME",
        4: "BACK",
        5: "CALL",
        6: "ENDCALL",
        24: "VOLUME_UP",
        25: "VOLUME_DOWN",
        26: "POWER",
        27: "CAMERA",
        66: "ENTER",
        67: "DEL",
        112: "FORWARD_DEL",
        187: "APP_SWITCH",
        219: "MENU",
        220: "RECENT_APPS",
    }

    try:
        device.client.input_keyevent(keycode)
        key_name = KEYCODE_NAMES.get(keycode, f"KEYCODE_{keycode}")
        return {"success": True, "action": "keyevent", "keycode": keycode, "name": key_name}
    except ADBError as e:
        return {"error": str(e)}


async def input_scroll(
    x: int, y: int, dx: int, dy: int, serial: Optional[str] = None
) -> Dict[str, Any]:
    """Simulate a scroll gesture.

    Args:
        x: Start X coordinate
        y: Start Y coordinate
        dx: Horizontal scroll delta (positive = right)
        dy: Vertical scroll delta (positive = down)
        serial: Device serial (uses active device if not specified)

    Returns:
        Result dictionary
    """
    device = _get_device(serial)
    if not device:
        return {"error": "No device available"}

    try:
        device.client.input_scroll(x, y, dx, dy)
        return {
            "success": True,
            "action": "scroll",
            "from": {"x": x, "y": y},
            "delta": {"dx": dx, "dy": dy},
        }
    except ADBError as e:
        return {"error": str(e)}


def _get_device(serial: Optional[str]) -> Optional[Any]:
    """Get a device by serial or return the active device."""
    if serial:
        return device_manager.get_device(serial)
    return device_manager.active_device
