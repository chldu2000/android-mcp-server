"""ADB Client for communicating with Android devices using adb-shell library."""

import subprocess
from typing import Any, Optional

from adb_shell.adb_device import AdbDevice
from adb_shell.transport.tcp_transport import TcpTransport


class ADBClient:
    """Client for ADB operations using adb-shell library.

    Supports both USB and TCP/IP connections:
    - USB devices: Falls back to subprocess for operations, but can enable TCP/IP mode
    - TCP/IP devices: Uses adb-shell's TcpTransport directly
    """

    def __init__(self):
        self._adb_path = "adb"

    def _validate_serial(self, serial: str) -> None:
        """Validate serial parameter."""
        if not serial:
            raise ValueError("serial parameter cannot be None or empty")

    def _parse_device_address(self, serial: str) -> tuple[str, int]:
        """Parse device serial to get host and port.

        Supports formats:
        - IP:PORT (e.g., 192.168.1.100:5555)
        - Device ID with port via USB TCP/IP
        """
        if ":" in serial:
            parts = serial.rsplit(":", 1)
            host = parts[0]
            try:
                port = int(parts[1])
            except ValueError:
                port = 5555
            return host, port
        # Default ADB port
        return serial, 5555

    def _run_adb_command(self, args: list[str]) -> str:
        """Run an ADB command via subprocess and return output."""
        cmd = [self._adb_path] + args
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            raise RuntimeError("ADB command timed out")
        except FileNotFoundError:
            raise RuntimeError(f"ADB command not found. Please ensure '{self._adb_path}' is installed and in your PATH.")
        except PermissionError as e:
            raise RuntimeError(f"Permission denied when running ADB command: {e}")
        except OSError as e:
            raise RuntimeError(f"OS error when running ADB command: {e}")

        if result.returncode != 0:
            raise RuntimeError(f"ADB command failed: {result.stderr}")
        return result.stdout.strip()

    def _get_tcp_device(self, serial: str) -> AdbDevice:
        """Get an AdbDevice connected via TCP/IP.

        For USB devices, you need to first run:
            adb tcpip 5555
        to enable TCP/IP mode.
        """
        host, port = self._parse_device_address(serial)
        transport = TcpTransport(host, port)
        device = AdbDevice(transport)
        return device

    def list_devices(self) -> list[dict[str, str]]:
        """List all connected devices via ADB.

        Returns:
            List of devices with serial and state.
        """
        output = self._run_adb_command(["devices", "-l"])
        devices = []
        lines = output.split("\n")
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                serial = parts[0]
                state = parts[1]
                devices.append({"serial": serial, "state": state})
            elif len(parts) == 1:
                devices.append({"serial": parts[0], "state": "unknown"})
        return devices

    def get_device_info(self, serial: str) -> dict[str, Any]:
        """Get detailed info for a specific device using adb-shell.

        Args:
            serial: Device serial number or IP:PORT

        Returns:
            Dictionary of device properties.
        """
        self._validate_serial(serial)
        try:
            device = self._get_tcp_device(serial)
            device.connect()
            output = device.shell("getprop")
            device.close()

            props = {}
            for line in output.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    props[key.strip()[1:-1]] = value.strip()
            return props
        except Exception:
            # Fallback to subprocess if adb-shell fails
            output = self._run_adb_command(["-s", serial, "shell", "getprop"])
            props = {}
            for line in output.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    props[key.strip()[1:-1]] = value.strip()
            return props

    def shell(self, serial: str, command: str) -> str:
        """Execute shell command on device using adb-shell.

        Args:
            serial: Device serial number or IP:PORT
            command: Shell command to execute

        Returns:
            Command output.
        """
        self._validate_serial(serial)
        try:
            device = self._get_tcp_device(serial)
            device.connect()
            output = device.shell(command)
            device.close()
            return output
        except Exception:
            # Fallback to subprocess
            return self._run_adb_command(["-s", serial, "shell", command])

    def install(self, serial: str, apk_path: str) -> str:
        """Install an APK on the device.

        Args:
            serial: Device serial number
            apk_path: Path to the APK file

        Returns:
            Installation result message.
        """
        self._validate_serial(serial)
        return self._run_adb_command(["-s", serial, "install", "-r", apk_path])

    def uninstall(self, serial: str, package_name: str) -> str:
        """Uninstall an app from the device.

        Args:
            serial: Device serial number
            package_name: Package name to uninstall

        Returns:
            Uninstall result message.
        """
        self._validate_serial(serial)
        return self._run_adb_command(["-s", serial, "uninstall", package_name])

    def list_packages(self, serial: str) -> list[str]:
        """List installed packages on the device.

        Args:
            serial: Device serial number or IP:PORT

        Returns:
            List of package names.
        """
        self._validate_serial(serial)
        output = self.shell(serial, "pm list packages")
        packages = []
        for line in output.split("\n"):
            if line.startswith("package:"):
                packages.append(line.replace("package:", "").strip())
        return packages

    def start_app(self, serial: str, package_name: str, activity: Optional[str] = None) -> str:
        """Start an application on the device.

        Args:
            serial: Device serial number or IP:PORT
            package_name: Package name
            activity: Optional activity name

        Returns:
            Start result message.
        """
        self._validate_serial(serial)
        if activity:
            component = f"{package_name}/{activity}"
            return self.shell(serial, f"am start -n {component}")
        return self.shell(serial, f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")

    def stop_app(self, serial: str, package_name: str) -> str:
        """Force stop an application on the device.

        Args:
            serial: Device serial number or IP:PORT
            package_name: Package name

        Returns:
            Stop result message.
        """
        self._validate_serial(serial)
        return self.shell(serial, f"am force-stop {package_name}")

    def pull_file(self, serial: str, device_path: str, local_path: str) -> str:
        """Pull a file from device to local using adb-shell.

        Args:
            serial: Device serial number or IP:PORT
            device_path: Path on the device
            local_path: Local destination path

        Returns:
            Success message.
        """
        self._validate_serial(serial)
        try:
            device = self._get_tcp_device(serial)
            device.connect()
            device.pull(device_path, local_path)
            device.close()
            return f"Pulled {device_path} to {local_path}"
        except Exception:
            # Fallback to subprocess
            return self._run_adb_command(["-s", serial, "pull", device_path, local_path])

    def push_file(self, serial: str, local_path: str, device_path: str) -> str:
        """Push a file from local to device using adb-shell.

        Args:
            serial: Device serial number or IP:PORT
            local_path: Local file path
            device_path: Destination on device

        Returns:
            Success message.
        """
        self._validate_serial(serial)
        try:
            device = self._get_tcp_device(serial)
            device.connect()
            device.push(local_path, device_path)
            device.close()
            return f"Pushed {local_path} to {device_path}"
        except Exception:
            # Fallback to subprocess
            return self._run_adb_command(["-s", serial, "push", local_path, device_path])

    def tap(self, serial: str, x: int, y: int) -> str:
        """Simulate a tap at coordinates.

        Args:
            serial: Device serial number or IP:PORT
            x: X coordinate
            y: Y coordinate

        Returns:
            Command result.
        """
        self._validate_serial(serial)
        return self.shell(serial, f"input tap {x} {y}")

    def swipe(self, serial: str, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> str:
        """Simulate a swipe gesture.

        Args:
            serial: Device serial number or IP:PORT
            x1: Start X
            y1: Start Y
            x2: End X
            y2: End Y
            duration: Duration in milliseconds

        Returns:
            Command result.
        """
        self._validate_serial(serial)
        return self.shell(serial, f"input swipe {x1} {y1} {x2} {y2} {duration}")

    def input_text(self, serial: str, text: str) -> str:
        """Input text on the device.

        Args:
            serial: Device serial number or IP:PORT
            text: Text to input

        Returns:
            Command result.
        """
        self._validate_serial(serial)
        # Escape special characters for shell
        escaped = (
            text.replace("\\", "\\\\")
            .replace(" ", "%s")
            .replace("'", "'\\''")
            .replace(";", "\\;")
            .replace("&", "\\&")
            .replace("|", "\\|")
            .replace("<", "\\<")
            .replace(">", "\\>")
            .replace("`", "\\`")
            .replace("$", "\\$")
        )
        return self.shell(serial, f"input text '{escaped}'")

    def press_key(self, serial: str, keycode: int) -> str:
        """Press a key event.

        Args:
            serial: Device serial number or IP:PORT
            keycode: Android keycode

        Returns:
            Command result.
        """
        self._validate_serial(serial)
        return self.shell(serial, f"input keyevent {keycode}")

    def get_screen_size(self, serial: str) -> dict[str, int]:
        """Get screen resolution.

        Args:
            serial: Device serial number or IP:PORT

        Returns:
            Dictionary with width and height.
        """
        self._validate_serial(serial)
        output = self.shell(serial, "wm size")
        if "x" in output:
            size = output.split(":")[-1].strip()
            if "x" in size:
                width, height = size.split("x")
                return {"width": int(width), "height": int(height)}
        return {"width": 0, "height": 0}

    def get_battery(self, serial: str) -> dict[str, Any]:
        """Get battery status.

        Args:
            serial: Device serial number or IP:PORT

        Returns:
            Battery information.
        """
        self._validate_serial(serial)
        output = self.shell(serial, "dumpsys battery")
        battery = {}
        for line in output.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower().replace(" ", "_")
                value = value.strip()
                battery[key] = value
        return battery
