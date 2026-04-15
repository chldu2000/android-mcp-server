"""ADB client for Python - wraps adb-shell library."""

import subprocess
import base64
from typing import Optional, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class DeviceState(Enum):
    """Android device connection state."""
    OFFLINE = "offline"
    BOOTLOADER = "bootloader"
    DEVICE = "device"
    RECOVERY = "recovery"
    UNAUTHORIZED = "unauthorized"
    NO_DEVICE = "no device"


@dataclass
class DeviceInfo:
    """Information about a connected Android device."""
    serial: str
    state: DeviceState
    product: Optional[str] = None
    model: Optional[str] = None
    device: Optional[str] = None
    transport_id: Optional[str] = None


class ADBError(Exception):
    """Exception raised when an ADB command fails."""
    def __init__(self, message: str, stderr: str = "", returncode: int = 0):
        super().__init__(message)
        self.stderr = stderr
        self.returncode = returncode


class ADBClient:
    """Client for executing ADB commands."""

    def __init__(self, serial: Optional[str] = None):
        """Initialize ADB client.

        Args:
            serial: Device serial number. If None, uses the default device.
        """
        self.serial = serial
        self._base_command = ["adb"]
        if serial:
            self._base_command.extend(["-s", serial])

    def _run(self, args: List[str], timeout: int = 30) -> Tuple[str, str, int]:
        """Run an ADB command.

        Args:
            args: Command arguments (after 'adb')
            timeout: Command timeout in seconds

        Returns:
            Tuple of (stdout, stderr, returncode)
        """
        cmd = self._base_command + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            raise ADBError(f"Command timed out: {' '.join(cmd)}")
        except FileNotFoundError:
            raise ADBError("adb not found. Is Android SDK platform-tools installed?")

    def devices(self) -> List[DeviceInfo]:
        """List all connected devices.

        Returns:
            List of DeviceInfo objects
        """
        stdout, stderr, returncode = self._run(["devices", "-l"])
        if returncode != 0:
            raise ADBError(f"Failed to list devices: {stderr}", stderr, returncode)

        devices = []
        lines = stdout.strip().split("\n")
        for line in lines[1:]:  # Skip header
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 2:
                serial = parts[0]
                state_str = parts[1]
                try:
                    state = DeviceState(state_str)
                except ValueError:
                    state = DeviceState.NO_DEVICE

                device_info = DeviceInfo(serial=serial, state=state)

                # Parse additional info from -l output
                for part in parts[2:]:
                    if ":" in part:
                        key, value = part.split(":", 1)
                        if key == "product":
                            device_info.product = value
                        elif key == "model":
                            device_info.model = value.replace("_", " ")
                        elif key == "device":
                            device_info.device = value
                        elif key == "transport_id":
                            device_info.transport_id = value

                devices.append(device_info)
        return devices

    def connect(self, host: str, port: int = 5555) -> bool:
        """Connect to a device over TCP/IP.

        Args:
            host: Device IP address
            port: ADB port (default 5555)

        Returns:
            True if connection successful
        """
        stdout, stderr, returncode = self._run(["connect", f"{host}:{port}"])
        return "connected" in stdout.lower() or "already connected" in stdout.lower()

    def disconnect(self, host: str, port: int = 5555) -> bool:
        """Disconnect from a TCP/IP device.

        Args:
            host: Device IP address
            port: ADB port (default 5555)

        Returns:
            True if disconnection successful
        """
        stdout, stderr, returncode = self._run(["disconnect", f"{host}:{port}"])
        return "disconnected" in stdout.lower()

    def shell(self, command: str, timeout: int = 30) -> str:
        """Execute a shell command on the device.

        Args:
            command: Shell command to execute
            timeout: Command timeout in seconds

        Returns:
            Command stdout
        """
        stdout, stderr, returncode = self._run(["shell", command], timeout=timeout)
        if returncode != 0 and stderr:
            # Some commands return non-zero but still have valid output
            if not stdout:
                raise ADBError(f"Shell command failed: {stderr}", stderr, returncode)
        return stdout

    def screencap(self) -> bytes:
        """Capture the device screen.

        Returns:
            PNG image data
        """
        # Capture to a temp file on device, then pull it
        device_path = "/sdcard/screencap.png"
        self.shell(f"screencap -p {device_path}")

        # Pull the file
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            local_path = f.name

        try:
            stdout, stderr, returncode = self._run(["pull", device_path, local_path])
            if returncode != 0:
                raise ADBError(f"Failed to pull screenshot: {stderr}", stderr, returncode)

            with open(local_path, "rb") as f:
                return f.read()
        finally:
            if os.path.exists(local_path):
                os.unlink(local_path)
            self.shell(f"rm {device_path}")

    def screencap_base64(self) -> str:
        """Capture the device screen and return as base64.

        Returns:
            Base64-encoded PNG image
        """
        return base64.b64encode(self.screencap()).decode("utf-8")

    def input_tap(self, x: int, y: int) -> bool:
        """Simulate a tap at the given coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if successful
        """
        self.shell(f"input tap {x} {y}")
        return True

    def input_swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """Simulate a swipe gesture.

        Args:
            x1: Start X coordinate
            y1: Start Y coordinate
            x2: End X coordinate
            y2: End Y coordinate
            duration: Duration in milliseconds

        Returns:
            True if successful
        """
        self.shell(f"input swipe {x1} {y1} {x2} {y2} {duration}")
        return True

    def input_text(self, text: str) -> bool:
        """Simulate text input.

        Args:
            text: Text to input

        Returns:
            True if successful
        """
        # Escape special characters
        text = text.replace(" ", "%s")
        self.shell(f"input text {text}")
        return True

    def input_keyevent(self, keycode: int) -> bool:
        """Simulate a key event.

        Args:
            keycode: Android keycode (e.g., 3 for HOME, 4 for BACK)

        Returns:
            True if successful
        """
        self.shell(f"input keyevent {keycode}")
        return True

    def input_scroll(self, x: int, y: int, dx: int, dy: int) -> bool:
        """Simulate a scroll gesture.

        Args:
            x: Start X coordinate
            y: Start Y coordinate
            dx: Horizontal scroll delta
            dy: Vertical scroll delta

        Returns:
            True if successful
        """
        # Note: Android's input command doesn't have native scroll,
        # we simulate it with swipe
        duration = 300
        end_x = x + dx
        end_y = y + dy
        return self.input_swipe(x, y, end_x, end_y, duration)

    def install(self, apk_path: str, reinstall: bool = False) -> bool:
        """Install an APK on the device.

        Args:
            apk_path: Path to the APK file
            reinstall: If True, reinstall and keep data

        Returns:
            True if successful
        """
        args = ["install"]
        if reinstall:
            args.append("-r")
        args.append(apk_path)

        stdout, stderr, returncode = self._run(args, timeout=120)
        if returncode != 0:
            raise ADBError(f"Install failed: {stderr}", stderr, returncode)
        return "Success" in stdout

    def uninstall(self, package_name: str, keep_data: bool = False) -> bool:
        """Uninstall an app from the device.

        Args:
            package_name: Package name (e.g., com.example.app)
            keep_data: If True, keep app data

        Returns:
            True if successful
        """
        args = ["uninstall"]
        if keep_data:
            args.append("-k")
        args.append(package_name)

        stdout, stderr, returncode = self._run(args)
        return "Success" in stdout

    def list_packages(self, filter_string: Optional[str] = None) -> List[str]:
        """List installed packages.

        Args:
            filter_string: Optional filter (e.g., "package:")

        Returns:
            List of package names
        """
        cmd = "pm list packages"
        if filter_string:
            cmd += f" {filter_string}"

        output = self.shell(cmd)
        packages = []
        for line in output.strip().split("\n"):
            if line.startswith("package:"):
                packages.append(line.replace("package:", "").strip())
        return packages

    def start_app(self, package_name: str, activity: Optional[str] = None) -> bool:
        """Start an application.

        Args:
            package_name: Package name
            activity: Optional activity name (if None, launches main activity)

        Returns:
            True if successful
        """
        if activity:
            component = f"{package_name}/{activity}"
        else:
            component = package_name

        self.shell(f"am start -n {component}")
        return True

    def stop_app(self, package_name: str) -> bool:
        """Force stop an application.

        Args:
            package_name: Package name

        Returns:
            True if successful
        """
        self.shell(f"am force-stop {package_name}")
        return True

    def clear_app(self, package_name: str) -> bool:
        """Clear application data.

        Args:
            package_name: Package name

        Returns:
            True if successful
        """
        self.shell(f"pm clear {package_name}")
        return True

    def push(self, local_path: str, remote_path: str) -> bool:
        """Push a file to the device.

        Args:
            local_path: Local file path
            remote_path: Remote file path on device

        Returns:
            True if successful
        """
        stdout, stderr, returncode = self._run(["push", local_path, remote_path], timeout=120)
        if returncode != 0:
            raise ADBError(f"Push failed: {stderr}", stderr, returncode)
        return True

    def pull(self, remote_path: str, local_path: str) -> bool:
        """Pull a file from the device.

        Args:
            remote_path: Remote file path on device
            local_path: Local file path

        Returns:
            True if successful
        """
        stdout, stderr, returncode = self._run(["pull", remote_path, local_path], timeout=120)
        if returncode != 0:
            raise ADBError(f"Pull failed: {stderr}", stderr, returncode)
        return True

    def getprop(self, property_name: Optional[str] = None) -> str:
        """Get a system property.

        Args:
            property_name: Property name (e.g., ro.build.version.sdk)
                          If None, returns all properties

        Returns:
            Property value or all properties
        """
        if property_name:
            return self.shell(f"getprop {property_name}").strip()
        return self.shell("getprop")

    def dumpsys(self, service: Optional[str] = None) -> str:
        """Get system service information.

        Args:
            service: Service name (e.g., window, activity)
                   If None, returns all services

        Returns:
            Service information
        """
        if service:
            return self.shell(f"dumpsys {service}")
        return self.shell("dumpsys")

    def wm_size(self) -> Tuple[int, int]:
        """Get the device screen size.

        Returns:
            Tuple of (width, height) in pixels
        """
        output = self.shell("wm size").strip()
        # Format: "Physical size: 1080x1920" or "Override size: 1080x1920"
        if "x" in output:
            size_str = output.split(":")[-1].strip()
            width, height = map(int, size_str.split("x"))
            return width, height
        return 0, 0

    def get_model(self) -> str:
        """Get the device model."""
        return self.getprop("ro.product.model").strip()

    def get_manufacturer(self) -> str:
        """Get the device manufacturer."""
        return self.getprop("ro.product.manufacturer").strip()

    def get_android_version(self) -> str:
        """Get the Android version."""
        return self.getprop("ro.build.version.release").strip()

    def get_sdk_version(self) -> str:
        """Get the SDK version."""
        return self.getprop("ro.build.version.sdk").strip()
