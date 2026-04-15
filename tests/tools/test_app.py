"""Tests for app management tools."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from android_mcp.tools.app import (
    adb_install_app,
    adb_uninstall_app,
    adb_list_packages,
    adb_start_app,
    adb_stop_app,
)


@pytest.fixture
def mock_adb_client():
    """Create a mock ADB client."""
    with patch("android_mcp.tools.app.get_adb_client") as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.mark.asyncio
async def test_adb_install_app(mock_adb_client):
    """Test installing an app."""
    mock_adb_client.install.return_value = "Success"
    result = await adb_install_app("serial123", "/path/to/app.apk")
    assert result == "Success"
    mock_adb_client.install.assert_called_once_with("serial123", "/path/to/app.apk")


@pytest.mark.asyncio
async def test_adb_uninstall_app(mock_adb_client):
    """Test uninstalling an app."""
    mock_adb_client.uninstall.return_value = "Success"
    result = await adb_uninstall_app("serial123", "com.example.app")
    assert result == "Success"
    mock_adb_client.uninstall.assert_called_once_with("serial123", "com.example.app")


@pytest.mark.asyncio
async def test_adb_list_packages(mock_adb_client):
    """Test listing packages."""
    mock_adb_client.list_packages.return_value = ["com.example.app1", "com.example.app2"]
    result = await adb_list_packages("serial123")
    assert result == ["com.example.app1", "com.example.app2"]
    mock_adb_client.list_packages.assert_called_once_with("serial123")


@pytest.mark.asyncio
async def test_adb_start_app_without_activity(mock_adb_client):
    """Test starting an app without specifying activity."""
    mock_adb_client.start_app.return_value = "Starting"
    result = await adb_start_app("serial123", "com.example.app")
    assert result == "Starting"
    mock_adb_client.start_app.assert_called_once_with("serial123", "com.example.app", None)


@pytest.mark.asyncio
async def test_adb_start_app_with_activity(mock_adb_client):
    """Test starting an app with activity."""
    mock_adb_client.start_app.return_value = "Starting"
    result = await adb_start_app("serial123", "com.example.app", ".MainActivity")
    assert result == "Starting"
    mock_adb_client.start_app.assert_called_once_with("serial123", "com.example.app", ".MainActivity")


@pytest.mark.asyncio
async def test_adb_stop_app(mock_adb_client):
    """Test stopping an app."""
    mock_adb_client.stop_app.return_value = "Stopped"
    result = await adb_stop_app("serial123", "com.example.app")
    assert result == "Stopped"
    mock_adb_client.stop_app.assert_called_once_with("serial123", "com.example.app")