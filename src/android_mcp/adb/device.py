"""Device utilities and helpers."""

from typing import Any


class AndroidDevice:
    """Represents a connected Android device."""

    def __init__(self, serial: str, state: str, client: Any):
        self.serial = serial
        self.state = state
        self._client = client

    def is_connected(self) -> bool:
        """Check if device is connected and online."""
        return self.state == "device"

    def get_info(self) -> dict[str, Any]:
        """Get device information."""
        return self._client.get_device_info(self.serial)

    def get_screen_size(self) -> dict[str, int]:
        """Get screen resolution."""
        return self._client.get_screen_size(self.serial)

    def get_battery(self) -> dict[str, Any]:
        """Get battery status."""
        return self._client.get_battery(self.serial)

    def __repr__(self) -> str:
        return f"AndroidDevice(serial={self.serial}, state={self.state})"