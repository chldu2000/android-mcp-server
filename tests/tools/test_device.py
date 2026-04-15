# tests/tools/test_device.py
import pytest
from android_mcp.tools.device import adb_list_devices, adb_device_info


@pytest.mark.asyncio
async def test_adb_list_devices():
    result = await adb_list_devices()
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_adb_device_info():
    # Requires a device serial
    pass