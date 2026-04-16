"""ADB Client for communicating with Android devices."""

import subprocess
from typing import Any, Optional


class ADBClient:
    """Client for ADB operations."""

    def __init__(self):
        self._adb_path = "adb"

    def _validate_serial(self, serial: str) -> None:
        """Validate serial parameter."""
        if not serial:
            raise ValueError("serial parameter cannot be None or empty")

    def _run_command(self, args: list[str]) -> str:
        """Run an ADB command and return output."""
        cmd = [self._adb_path] + args
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
        except FileNotFoundError:
            raise RuntimeError(f"ADB command not found. Please ensure 'adb' is installed and in your PATH.")
        except PermissionError as e:
            raise RuntimeError(f"Permission denied when running ADB command: {e}")
        except OSError as e:
            raise RuntimeError(f"OS error when running ADB command: {e}")
        if result.returncode != 0:
            raise RuntimeError(f"ADB command failed: {result.stderr}")
        return result.stdout.strip()

    def _run_command_raw(self, args: list[str]) -> bytes:
        """Run an ADB command and return raw binary output."""
        cmd = [self._adb_path] + args
        try:
            result = subprocess.run(cmd, capture_output=True)
        except FileNotFoundError:
            raise RuntimeError(f"ADB command not found. Please ensure 'adb' is installed and in your PATH.")
        except PermissionError as e:
            raise RuntimeError(f"Permission denied when running ADB command: {e}")
        except OSError as e:
            raise RuntimeError(f"OS error when running ADB command: {e}")
        if result.returncode != 0:
            raise RuntimeError(f"ADB command failed: {result.stderr}")
        return result.stdout

    def list_devices(self) -> list[dict[str, str]]:
        """List all connected devices."""
        output = self._run_command(["devices", "-l"])
        devices = []
        # Skip header line "List of devices attached"
        lines = output.split("\n")
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            # Expected format: "serial state" or "serial state key:value key:value ..."
            parts = line.split()
            if len(parts) >= 2:
                serial = parts[0]
                state = parts[1]
                devices.append({"serial": serial, "state": state})
            elif len(parts) == 1:
                # Serial only, no state (shouldn't happen but handle gracefully)
                devices.append({"serial": parts[0], "state": "unknown"})
        return devices

    def get_device_info(self, serial: str) -> dict[str, Any]:
        """Get detailed info for a specific device."""
        self._validate_serial(serial)
        output = self._run_command(["-s", serial, "shell", "getprop"])
        props = {}
        for line in output.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                props[key.strip()[1:-1]] = value.strip()
        return props

    def shell(self, serial: str, command: str) -> str:
        """Execute shell command on device."""
        self._validate_serial(serial)
        return self._run_command(["-s", serial, "shell", command])

    def exec_out(self, serial: str, command: str) -> bytes:
        """Execute command via exec-out on device (for binary output like screencap)."""
        self._validate_serial(serial)
        return self._run_command_raw(["-s", serial, "exec-out", command])

    def install(self, serial: str, apk_path: str) -> str:
        """Install an APK on the device."""
        self._validate_serial(serial)
        return self._run_command(["-s", serial, "install", "-r", apk_path])

    def uninstall(self, serial: str, package_name: str) -> str:
        """Uninstall an app from the device."""
        self._validate_serial(serial)
        return self._run_command(["-s", serial, "uninstall", package_name])

    def list_packages(self, serial: str) -> list[str]:
        """List installed packages."""
        self._validate_serial(serial)
        output = self._run_command(["-s", serial, "shell", "pm", "list", "packages"])
        packages = []
        for line in output.split("\n"):
            if line.startswith("package:"):
                packages.append(line.replace("package:", "").strip())
        return packages

    def start_app(self, serial: str, package_name: str, activity: Optional[str] = None) -> str:
        """Start an application."""
        self._validate_serial(serial)
        if activity:
            component = f"{package_name}/{activity}"
            return self._run_command(["-s", serial, "shell", "am", "start", "-n", component])
        return self._run_command(["-s", serial, "shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"])

    def stop_app(self, serial: str, package_name: str) -> str:
        """Force stop an application."""
        self._validate_serial(serial)
        return self._run_command(["-s", serial, "shell", "am", "force-stop", package_name])

    def pull_file(self, serial: str, device_path: str, local_path: str) -> str:
        """Pull a file from device to local."""
        self._validate_serial(serial)
        return self._run_command(["-s", serial, "pull", device_path, local_path])

    def push_file(self, serial: str, local_path: str, device_path: str) -> str:
        """Push a file from local to device."""
        self._validate_serial(serial)
        return self._run_command(["-s", serial, "push", local_path, device_path])

    def tap(self, serial: str, x: int, y: int) -> str:
        """Simulate a tap at coordinates."""
        self._validate_serial(serial)
        return self._run_command(["-s", serial, "shell", "input", "tap", str(x), str(y)])

    def swipe(self, serial: str, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> str:
        """Simulate a swipe gesture."""
        self._validate_serial(serial)
        return self._run_command(["-s", serial, "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)])

    def input_text(self, serial: str, text: str) -> str:
        """Input text on the device."""
        self._validate_serial(serial)
        # Android input text requires escaping for shell metacharacters
        # %s is the placeholder for spaces in Android input text
        # We also need to escape shell special characters
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
        return self._run_command(["-s", serial, "shell", "input", "text", escaped])

    def press_key(self, serial: str, keycode: int) -> str:
        """Press a key event."""
        self._validate_serial(serial)
        return self._run_command(["-s", serial, "shell", "input", "keyevent", str(keycode)])

    def get_screen_size(self, serial: str) -> dict[str, int]:
        """Get screen resolution."""
        self._validate_serial(serial)
        output = self._run_command(["-s", serial, "shell", "wm", "size"])
        # Parse output like "Physical size: 1080x1920"
        if "x" in output:
            size = output.split(":")[-1].strip()
            width, height = size.split("x")
            return {"width": int(width), "height": int(height)}
        return {"width": 0, "height": 0}

    def get_battery(self, serial: str) -> dict[str, Any]:
        """Get battery status."""
        self._validate_serial(serial)
        output = self._run_command(["-s", serial, "shell", "dumpsys", "battery"])
        battery = {}
        for line in output.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower().replace(" ", "_")
                value = value.strip()
                battery[key] = value
        return battery