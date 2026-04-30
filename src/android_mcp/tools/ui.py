"""UI element tools for MCP."""

import re
from typing import Any
from android_mcp.tools.device import get_adb_client

class Uiautomator2Device:
    """Wrapper for uiautomator2 device connection with lazy initialization."""

    def __init__(self, serial: str):
        self.serial = serial
        self._device = None

    @property
    def device(self):
        """Lazily connect to device via uiautomator2."""
        if self._device is None:
            import uiautomator2 as u2
            self._device = u2.connect(self.serial)
        return self._device

    def dump_hierarchy(self) -> str:
        """Dump UI hierarchy as XML string."""
        return self.device.dump_hierarchy()


# Global uiautomator2 device cache
_u2_devices: dict[str, Uiautomator2Device] = {}


def get_u2_device(serial: str) -> Uiautomator2Device:
    """Get or create a Uiautomator2Device for the given serial."""
    if serial not in _u2_devices:
        _u2_devices[serial] = Uiautomator2Device(serial)
    return _u2_devices[serial]


async def adb_dump_ui_tree(serial: str) -> str:
    """Dump the UI hierarchy tree from the device.

    Uses uiautomator2 to dump the current UI hierarchy as XML,
    with fallback to ADB shell uiautomator dump on failure.

    Args:
        serial: Device serial number

    Returns:
        UI hierarchy XML string.
    """
    try:
        u2_dev = get_u2_device(serial)
        return u2_dev.dump_hierarchy()
    except Exception as e:
        import logging
        logging.warning(f"uiautomator2 failed, falling back to ADB: {e}")
        # Fallback to original ADB method
        client = get_adb_client()
        client.shell(serial, "uiautomator dump /sdcard/window_dump.xml")
        output = client.shell(serial, "cat /sdcard/window_dump.xml")
        client.shell(serial, "rm /sdcard/window_dump.xml")
        return output


def _parse_bounds(bounds_str: str) -> dict[str, int]:
    """Parse bounds string like '[0,0][1080,1920]' into dict."""
    match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds_str)
    if match:
        x1, y1, x2, y2 = map(int, match.groups())
        return {
            "x": x1,
            "y": y1,
            "width": x2 - x1,
            "height": y2 - y1,
        }
    return {"x": 0, "y": 0, "width": 0, "height": 0}


def _parse_node_attributes(node_line: str) -> dict[str, str]:
    """Parse a single node line and extract attributes."""
    attrs = {}

    # Match patterns like: resource-id='com.example:id/btn' text='OK' class='android.widget.Button'
    patterns = [
        (r'resource-id="([^"]*)"', 'resource_id'),
        (r'resource-id=\'([^\']*)\'', 'resource_id'),
        (r'text="([^"]*)"', 'text'),
        (r'text=\'([^\']*)\'', 'text'),
        (r'content-desc="([^"]*)"', 'content_desc'),
        (r'content-desc=\'([^\']*)\'', 'content_desc'),
        (r'class="([^"]*)"', 'class'),
        (r'class=\'([^\']*)\'', 'class'),
        (r'bounds="([^"]*)"', 'bounds'),
        (r'bounds=\'([^\']*)\'', 'bounds'),
        (r'clickable="([^"]*)"', 'clickable'),
        (r'long-clickable="([^"]*)"', 'long_clickable'),
        (r'enabled="([^"]*)"', 'enabled'),
        (r'focusable="([^"]*)"', 'focusable'),
    ]

    for pattern, key in patterns:
        match = re.search(pattern, node_line)
        if match:
            value = match.group(1)
            # Convert string booleans
            if value in ('true', 'false'):
                value = value == 'true'
            attrs[key] = value

    return attrs


def _get_element_actions(attrs: dict[str, Any]) -> list[str]:
    """Determine available actions for an element based on its attributes."""
    actions = []
    bounds = attrs.get("bounds")
    if bounds:
        actions.append("tap")
    if attrs.get("clickable") is True:
        actions.append("click")
    if attrs.get("long_clickable") is True:
        actions.append("long_click")
    return actions


async def adb_find_element(
    serial: str,
    resource_id: str = None,
    text: str = None,
    content_desc: str = None,
    class_name: str = None,
    enabled: bool = None,
    clickable: bool = None,
    focusable: bool = None,
) -> list[dict[str, Any]]:
    """Find UI elements by their attributes.

    Uses uiautomator2 selectors with fallback to ADB uiautomator dump.
    All provided criteria must match (AND logic).

    Args:
        serial: Device serial number
        resource_id: Resource ID to match (e.g., 'com.example:id/btn')
        text: Text content to match
        content_desc: Content description to match
        class_name: View class to match (e.g., 'android.widget.Button')
        enabled: Filter by enabled state
        clickable: Filter by clickable state
        focusable: Filter by focusable state

    Returns:
        List of matching elements with their attributes and available actions.
    """
    if all(p is None for p in [resource_id, text, content_desc, class_name, enabled, clickable, focusable]):
        return []

    try:
        u2_dev = get_u2_device(serial)
        return _u2_find_element_impl(u2_dev, resource_id, text, content_desc, class_name, enabled, clickable, focusable)
    except Exception as e:
        import logging
        logging.warning(f"uiautomator2 failed in find_element, falling back to ADB: {e}")
        return _adb_find_element_impl(serial, resource_id, text, content_desc, class_name, enabled, clickable, focusable)


def _u2_find_element_impl(
    u2_dev: Uiautomator2Device,
    resource_id: str = None,
    text: str = None,
    content_desc: str = None,
    class_name: str = None,
    enabled: bool = None,
    clickable: bool = None,
    focusable: bool = None,
) -> list[dict[str, Any]]:
    """Find elements using uiautomator2 selectors."""
    device = u2_dev.device

    # Build selector chain
    if resource_id is not None:
        device = device(resourceId=resource_id)
    if text is not None:
        device = device(text=text)
    if content_desc is not None:
        device = device(description=content_desc)
    if class_name is not None:
        device = device(className=class_name)
    if enabled is not None:
        device = device(enabled=enabled)
    if clickable is not None:
        device = device(clickable=clickable)
    if focusable is not None:
        device = device(focusable=focusable)

    # Get all matching elements by iterating over the UiObject
    results = []

    for elem in device:
        info = elem.info
        bounds = elem.bounds()
        attrs = {
            "resource_id": info.get("resourceName"),
            "text": info.get("text"),
            "content_desc": info.get("contentDesc"),
            "class": info.get("className"),
            "bounds": {"x": bounds[0], "y": bounds[1], "width": bounds[2] - bounds[0], "height": bounds[3] - bounds[1]},
            "enabled": info.get("enabled"),
            "clickable": info.get("clickable"),
            "long_clickable": info.get("longClickable"),
            "focusable": info.get("focusable"),
        }
        actions = []
        if bounds:
            actions.append("tap")
        if attrs.get("clickable"):
            actions.append("click")
        if attrs.get("long_clickable"):
            actions.append("long_click")
        attrs["actions"] = actions
        results.append(attrs)

    return results


def _adb_find_element_impl(
    serial: str,
    resource_id: str = None,
    text: str = None,
    content_desc: str = None,
    class_name: str = None,
    enabled: bool = None,
    clickable: bool = None,
    focusable: bool = None,
) -> list[dict[str, Any]]:
    """Find elements using ADB uiautomator dump (fallback)."""
    client = get_adb_client()
    client.shell(serial, "uiautomator dump /sdcard/window_dump.xml")
    xml_content = client.shell(serial, "cat /sdcard/window_dump.xml")
    client.shell(serial, "rm /sdcard/window_dump.xml")

    if not xml_content or not xml_content.strip():
        return []

    node_pattern = re.compile(r'<node\s+(.*?)(?:/>|>)', re.DOTALL)
    results = []

    for match in node_pattern.finditer(xml_content):
        node_attrs_str = match.group(1)
        attrs = _parse_node_attributes(node_attrs_str)

        if resource_id is not None and attrs.get("resource_id") != resource_id:
            continue
        if text is not None and attrs.get("text") != text:
            continue
        if content_desc is not None and attrs.get("content_desc") != content_desc:
            continue
        if class_name is not None and attrs.get("class") != class_name:
            continue
        if enabled is not None and attrs.get("enabled") != enabled:
            continue
        if clickable is not None and attrs.get("clickable") != clickable:
            continue
        if focusable is not None and attrs.get("focusable") != focusable:
            continue

        element = {
            "resource_id": attrs.get("resource_id"),
            "text": attrs.get("text"),
            "content_desc": attrs.get("content_desc"),
            "class": attrs.get("class"),
            "bounds": _parse_bounds(attrs.get("bounds", "[0,0][0,0]")),
            "enabled": attrs.get("enabled"),
            "clickable": attrs.get("clickable"),
            "long_clickable": attrs.get("long_clickable"),
            "focusable": attrs.get("focusable"),
            "actions": _get_element_actions(attrs),
        }
        results.append(element)

    return results