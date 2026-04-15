"""UI element tools for MCP."""

from android_mcp.tools.device import get_adb_client


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