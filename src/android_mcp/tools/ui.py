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


async def adb_dump_ui_tree(serial: str) -> str:
    """Dump the UI hierarchy tree from the device.

    Uses uiautomator to dump the current UI hierarchy as XML.

    Args:
        serial: Device serial number

    Returns:
        UI hierarchy XML string.
    """
    client = get_adb_client()
    # uiautomator dump writes to /sdcard/window_dump.xml by default
    # First, dump the UI hierarchy
    client.shell(serial, "uiautomator dump /sdcard/window_dump.xml")
    # Then read the file content directly
    output = client.shell(serial, "cat /sdcard/window_dump.xml")
    # Clean up the dumped file
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

    Uses uiautomator to dump the UI hierarchy and finds elements matching
    all provided criteria (AND matching). If no criteria are provided,
    returns an empty list.

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
    # If no criteria provided, return empty list
    if all(p is None for p in [resource_id, text, content_desc, class_name, enabled, clickable, focusable]):
        return []

    client = get_adb_client()

    # Dump UI hierarchy
    client.shell(serial, "uiautomator dump /sdcard/window_dump.xml")
    xml_content = client.shell(serial, "cat /sdcard/window_dump.xml")
    client.shell(serial, "rm /sdcard/window_dump.xml")

    if not xml_content or not xml_content.strip():
        return []

    # Parse XML to find nodes with attributes
    # Each node line starts with '  <node' and contains various attributes
    node_pattern = re.compile(r'<node\s+(.*?)(?:/>|>)', re.DOTALL)
    results = []

    for match in node_pattern.finditer(xml_content):
        node_attrs_str = match.group(1)
        attrs = _parse_node_attributes(node_attrs_str)

        # Apply AND matching - element must match all provided criteria
        if resource_id is not None:
            if attrs.get("resource_id") != resource_id:
                continue

        if text is not None:
            if attrs.get("text") != text:
                continue

        if content_desc is not None:
            if attrs.get("content_desc") != content_desc:
                continue

        if class_name is not None:
            if attrs.get("class") != class_name:
                continue

        if enabled is not None:
            if attrs.get("enabled") != enabled:
                continue

        if clickable is not None:
            if attrs.get("clickable") != clickable:
                continue

        if focusable is not None:
            if attrs.get("focusable") != focusable:
                continue

        # Element matches all criteria - build result
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