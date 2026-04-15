"""Tests for file operation tools."""

import pytest
from unittest.mock import Mock, patch
from android_mcp.tools.file import adb_pull_file, adb_push_file


@pytest.fixture
def mock_adb_client():
    """Create a mock ADB client."""
    with patch("android_mcp.tools.file.get_adb_client") as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.mark.asyncio
async def test_adb_pull_file(mock_adb_client):
    """Test pulling a file from device."""
    mock_adb_client.pull_file.return_value = "/local/path/file.txt: 1 file pulled"
    result = await adb_pull_file("serial123", "/device/path/file.txt", "/local/path/file.txt")
    assert result == "/local/path/file.txt: 1 file pulled"
    mock_adb_client.pull_file.assert_called_once_with("serial123", "/device/path/file.txt", "/local/path/file.txt")


@pytest.mark.asyncio
async def test_adb_push_file(mock_adb_client):
    """Test pushing a file to device."""
    mock_adb_client.push_file.return_value = "/device/path/file.txt: 1 file pushed"
    result = await adb_push_file("serial123", "/local/path/file.txt", "/device/path/file.txt")
    assert result == "/device/path/file.txt: 1 file pushed"
    mock_adb_client.push_file.assert_called_once_with("serial123", "/local/path/file.txt", "/device/path/file.txt")