import pytest
from android_mcp.adb.client import ADBClient


def test_adb_client_initialization():
    client = ADBClient()
    assert client is not None


def test_adb_list_devices():
    client = ADBClient()
    devices = client.list_devices()
    assert isinstance(devices, list)


def test_adb_device_info():
    client = ADBClient()
    # This will fail until we implement the client