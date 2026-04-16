"""Shell command tools for MCP."""

from android_mcp.tools.device import get_adb_client


async def adb_shell(serial: str, command: str) -> str:
    """Execute a shell command on the device.

    Args:
        serial: Device serial number
        command: Shell command to execute

    Returns:
        Command output.
    """
    client = get_adb_client()
    return client.shell(serial, command)


async def adb_exec_out(serial: str, command: str) -> str:
    """Execute a command via adb exec-out on the device.

    Use this for commands that output binary data (e.g., screencap, screenrecord).

    Args:
        serial: Device serial number
        command: Command to execute via exec-out

    Returns:
        Command output.
    """
    client = get_adb_client()
    return client.exec_out(serial, command)