"""Device management and state."""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

from .client import ADBClient, DeviceInfo, DeviceState


class ScrcpyState(Enum):
    """scrcpy session state."""
    STOPPED = "stopped"
    RUNNING = "running"


@dataclass
class Device:
    """Represents a connected Android device."""
    serial: str
    state: DeviceState
    product: Optional[str] = None
    model: Optional[str] = None
    device_name: Optional[str] = None
    transport_id: Optional[str] = None
    _client: Optional[ADBClient] = field(default=None, repr=False)

    @property
    def client(self) -> ADBClient:
        """Get the ADB client for this device."""
        if self._client is None:
            self._client = ADBClient(serial=self.serial)
        return self._client

    @property
    def display_name(self) -> str:
        """Get a human-readable display name for the device."""
        if self.model:
            return f"{self.model} ({self.serial})"
        return self.serial

    def to_dict(self) -> Dict[str, Any]:
        """Convert device info to a dictionary."""
        return {
            "serial": self.serial,
            "state": self.state.value,
            "product": self.product,
            "model": self.model,
            "device": self.device_name,
            "transport_id": self.transport_id,
        }


class DeviceManager:
    """Manages device connections and the current active device."""

    _instance: Optional["DeviceManager"] = None

    def __new__(cls):
        """Singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the device manager."""
        if self._initialized:
            return
        self._devices: Dict[str, Device] = {}
        self._active_device: Optional[Device] = None
        self._scrcpy_state = ScrcpyState.STOPPED
        self._initialized = True

    def refresh_devices(self) -> Dict[str, Device]:
        """Refresh the list of connected devices.

        Returns:
            Dictionary of serial -> Device
        """
        client = ADBClient()
        device_infos = client.devices()
        self._devices = {}

        for info in device_infos:
            if info.state == DeviceState.DEVICE:
                device = Device(
                    serial=info.serial,
                    state=info.state,
                    product=info.product,
                    model=info.model,
                    device_name=info.device,
                    transport_id=info.transport_id,
                )
                self._devices[info.serial] = device

        # Update active device if it disconnected
        if self._active_device and self._active_device.serial not in self._devices:
            self._active_device = None

        return self._devices

    def get_device(self, serial: str) -> Optional[Device]:
        """Get a device by serial.

        Args:
            serial: Device serial number

        Returns:
            Device if found, None otherwise
        """
        if serial not in self._devices:
            self.refresh_devices()
        return self._devices.get(serial)

    def set_active_device(self, serial: str) -> bool:
        """Set the active device for single-device operations.

        Args:
            serial: Device serial number

        Returns:
            True if successful, False if device not found
        """
        device = self.get_device(serial)
        if device:
            self._active_device = device
            return True
        return False

    @property
    def active_device(self) -> Optional[Device]:
        """Get the currently active device."""
        if self._active_device is None and self._devices:
            # Auto-select first available device
            self._active_device = next(iter(self._devices.values()))
        return self._active_device

    @property
    def scrcpy_state(self) -> ScrcpyState:
        """Get the scrcpy session state."""
        return self._scrcpy_state

    @scrcpy_state.setter
    def scrcpy_state(self, state: ScrcpyState) -> None:
        """Set the scrcpy session state."""
        self._scrcpy_state = state

    def clear(self) -> None:
        """Clear all device state."""
        self._devices = {}
        self._active_device = None
        self._scrcpy_state = ScrcpyState.STOPPED


# Global device manager instance
device_manager = DeviceManager()
