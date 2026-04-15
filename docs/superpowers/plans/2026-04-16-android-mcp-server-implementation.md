# Android MCP Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single MCP Server using fastmcp that provides ADB and scrcpy capabilities for controlling Android devices via USB or network.

**Architecture:** FastMCP-based server with modular structure: ADB client for device operations, scrcpy client for screen streaming/control, and tools organized by functionality (device, app, file, shell, input, system, screen).

**Tech Stack:** Python, fastmcp, adb-shell, uv

---

## File Structure

```
android-mcp-server/
├── pyproject.toml
├── src/
│   └── android_mcp/
│       ├── __init__.py
│       ├── main.py
│       ├── adb/
│       │   ├── __init__.py
│       │   ├── client.py
│       │   └── device.py
│       ├── scrcpy/
│       │   ├── __init__.py
│       │   ├── client.py
│       │   └── control.py
│       └── tools/
│           ├── __init__.py
│           ├── device.py
│           ├── app.py
│           ├── file.py
│           ├── shell.py
│           ├── input.py
│           ├── system.py
│           └── screen.py
```

---

### Task 1: Project Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `src/android_mcp/__init__.py`
- Create: `src/android_mcp/main.py`
- Create: `src/android_mcp/adb/__init__.py`
- Create: `src/android_mcp/scrcpy/__init__.py`
- Create: `src/android_mcp/tools/__init__.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "android-mcp-server"
version = "0.1.0"
description = "MCP Server for Android device control via ADB and scrcpy"
requires-python = ">=3.10"
dependencies = [
    "fastmcp>=0.1.0",
    "adb-shell>=0.4.4",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/android_mcp"]
```

- [ ] **Step 2: Create src/android_mcp/__init__.py**

```python
"""Android MCP Server - Control Android devices via ADB and scrcpy."""
```

- [ ] **Step 3: Create src/android_mcp/main.py**

```python
"""Main entry point for the Android MCP Server."""

from fastmcp import FastMCP

mcp = FastMCP("android-mcp-server")


if __name__ == "__main__":
    mcp.run()
```

- [ ] **Step 4: Create placeholder __init__.py files**

Create empty `__init__.py` files for:
- `src/android_mcp/adb/__init__.py`
- `src/android_mcp/scrcpy/__init__.py`
- `src/android_mcp/tools/__init__.py`

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/
git commit -m "feat: project scaffold with fastmcp server entry point"
```

---

### Task 2: ADB Client Implementation

**Files:**
- Create: `src/android_mcp/adb/client.py`
- Create: `tests/adb/test_client.py`

- [ ] **Step 1: Write failing test**

```python
# tests/adb/test_client.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/adb/test_client.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'android_mcp'"

- [ ] **Step 3: Create ADBClient class in src/android_mcp/adb/client.py**

```python
"""ADB Client for communicating with Android devices."""

import subprocess
from typing import Any


class ADBClient:
    """Client for ADB operations."""

    def __init__(self):
        self._adb_path = "adb"

    def _run_command(self, args: list[str]) -> str:
        """Run an ADB command and return output."""
        cmd = [self._adb_path] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ADB command failed: {result.stderr}")
        return result.stdout.strip()

    def list_devices(self) -> list[dict[str, str]]:
        """List all connected devices."""
        output = self._run_command(["devices", "-l"])
        devices = []
        for line in output.split("\n")[1:]:
            if line.strip():
                parts = line.split()
                serial = parts[0]
                state = parts[1] if len(parts) > 1 else "unknown"
                devices.append({"serial": serial, "state": state})
        return devices

    def get_device_info(self, serial: str) -> dict[str, Any]:
        """Get detailed info for a specific device."""
        output = self._run_command(["-s", serial, "shell", "getprop"])
        props = {}
        for line in output.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                props[key.strip()[1:-1]] = value.strip()
        return props

    def shell(self, serial: str, command: str) -> str:
        """Execute shell command on device."""
        return self._run_command(["-s", serial, "shell", command])

    def install(self, serial: str, apk_path: str) -> str:
        """Install an APK on the device."""
        return self._run_command(["-s", serial, "install", "-r", apk_path])

    def uninstall(self, serial: str, package_name: str) -> str:
        """Uninstall an app from the device."""
        return self._run_command(["-s", serial, "uninstall", package_name])

    def list_packages(self, serial: str) -> list[str]:
        """List installed packages."""
        output = self._run_command(["-s", serial, "shell", "pm", "list", "packages"])
        packages = []
        for line in output.split("\n"):
            if line.startswith("package:"):
                packages.append(line.replace("package:", "").strip())
        return packages

    def start_app(self, serial: str, package_name: str, activity: str = None) -> str:
        """Start an application."""
        if activity:
            component = f"{package_name}/{activity}"
            return self._run_command(["-s", serial, "shell", "am", "start", "-n", component])
        return self._run_command(["-s", serial, "shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"])

    def stop_app(self, serial: str, package_name: str) -> str:
        """Force stop an application."""
        return self._run_command(["-s", serial, "shell", "am", "force-stop", package_name])

    def pull_file(self, serial: str, device_path: str, local_path: str) -> str:
        """Pull a file from device to local."""
        return self._run_command(["-s", serial, "pull", device_path, local_path])

    def push_file(self, serial: str, local_path: str, device_path: str) -> str:
        """Push a file from local to device."""
        return self._run_command(["-s", serial, "push", local_path, device_path])

    def tap(self, serial: str, x: int, y: int) -> str:
        """Simulate a tap at coordinates."""
        return self._run_command(["-s", serial, "shell", "input", "tap", str(x), str(y)])

    def swipe(self, serial: str, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> str:
        """Simulate a swipe gesture."""
        return self._run_command(["-s", serial, "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)])

    def input_text(self, serial: str, text: str) -> str:
        """Input text on the device."""
        # Escape special characters
        escaped = text.replace(" ", "%s")
        return self._run_command(["-s", serial, "shell", "input", "text", escaped])

    def press_key(self, serial: str, keycode: int) -> str:
        """Press a key event."""
        return self._run_command(["-s", serial, "shell", "input", "keyevent", str(keycode)])

    def get_screen_size(self, serial: str) -> dict[str, int]:
        """Get screen resolution."""
        output = self._run_command(["-s", serial, "shell", "wm", "size"])
        # Parse output like "Physical size: 1080x1920"
        if "x" in output:
            size = output.split(":")[-1].strip()
            width, height = size.split("x")
            return {"width": int(width), "height": int(height)}
        return {"width": 0, "height": 0}

    def get_battery(self, serial: str) -> dict[str, Any]:
        """Get battery status."""
        output = self._run_command(["-s", serial, "shell", "dumpsys", "battery"])
        battery = {}
        for line in output.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower().replace(" ", "_")
                value = value.strip()
                battery[key] = value
        return battery
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/adb/test_client.py -v`
Expected: PASS (or skip if no real device)

- [ ] **Step 5: Commit**

```bash
git add src/android_mcp/adb/client.py tests/
git commit -m "feat: implement ADB client with all basic operations"
```

---

### Task 3: ADB Device Helper

**Files:**
- Create: `src/android_mcp/adb/device.py`

- [ ] **Step 1: Create device helper in src/android_mcp/adb/device.py**

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add src/android_mcp/adb/device.py
git commit -m "feat: add AndroidDevice helper class"
```

---

### Task 4: ADB Tools - Device Management

**Files:**
- Create: `src/android_mcp/tools/device.py`
- Create: `tests/tools/test_device.py`

- [ ] **Step 1: Write failing tests in tests/tools/test_device.py**

```python
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
```

- [ ] **Step 2: Create src/android_mcp/tools/device.py**

```python
"""Device management tools for MCP."""

from typing import Any
from android_mcp.adb.client import ADBClient


# Global ADB client instance
_adb_client: ADBClient | None = None


def get_adb_client() -> ADBClient:
    """Get or create the global ADB client instance."""
    global _adb_client
    if _adb_client is None:
        _adb_client = ADBClient()
    return _adb_client


async def adb_list_devices() -> list[dict[str, str]]:
    """List all connected Android devices.

    Returns:
        List of devices with serial and state.
    """
    client = get_adb_client()
    devices = client.list_devices()
    return devices


async def adb_device_info(serial: str) -> dict[str, Any]:
    """Get detailed information about a specific device.

    Args:
        serial: Device serial number

    Returns:
        Device properties and information.
    """
    client = get_adb_client()
    return client.get_device_info(serial)
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/tools/test_device.py -v`

- [ ] **Step 4: Commit**

```bash
git add src/android_mcp/tools/device.py tests/tools/test_device.py
git commit -m "feat: add device management tools (list_devices, device_info)"
```

---

### Task 5: ADB Tools - App Management

**Files:**
- Create: `src/android_mcp/tools/app.py`
- Create: `tests/tools/test_app.py`

- [ ] **Step 1: Create src/android_mcp/tools/app.py**

```python
"""Application management tools for MCP."""

from typing import Any
from android_mcp.adb.client import ADBClient
from android_mcp.tools.device import get_adb_client


async def adb_install_app(serial: str, apk_path: str) -> str:
    """Install an APK on the device.

    Args:
        serial: Device serial number
        apk_path: Path to the APK file on local filesystem

    Returns:
        Installation result message.
    """
    client = get_adb_client()
    return client.install(serial, apk_path)


async def adb_uninstall_app(serial: str, package_name: str) -> str:
    """Uninstall an application from the device.

    Args:
        serial: Device serial number
        package_name: Package name of the app to uninstall

    Returns:
        Uninstall result message.
    """
    client = get_adb_client()
    return client.uninstall(serial, package_name)


async def adb_list_packages(serial: str) -> list[str]:
    """List all installed packages on the device.

    Args:
        serial: Device serial number

    Returns:
        List of package names.
    """
    client = get_adb_client()
    return client.list_packages(serial)


async def adb_start_app(serial: str, package_name: str, activity: str = None) -> str:
    """Start an application on the device.

    Args:
        serial: Device serial number
        package_name: Package name of the app to start
        activity: Optional activity name (e.g., '.MainActivity')

    Returns:
        Start result message.
    """
    client = get_adb_client()
    return client.start_app(serial, package_name, activity)


async def adb_stop_app(serial: str, package_name: str) -> str:
    """Force stop an application on the device.

    Args:
        serial: Device serial number
        package_name: Package name of the app to stop

    Returns:
        Stop result message.
    """
    client = get_adb_client()
    return client.stop_app(serial, package_name)
```

- [ ] **Step 2: Create tests/tools/test_app.py**

```python
# tests/tools/test_app.py
import pytest
from android_mcp.tools.app import (
    adb_install_app,
    adb_uninstall_app,
    adb_list_packages,
    adb_start_app,
    adb_stop_app,
)
```

- [ ] **Step 3: Commit**

```bash
git add src/android_mcp/tools/app.py tests/tools/test_app.py
git commit -m "feat: add app management tools (install, uninstall, list, start, stop)"
```

---

### Task 6: ADB Tools - File Operations

**Files:**
- Create: `src/android_mcp/tools/file.py`
- Create: `tests/tools/test_file.py`

- [ ] **Step 1: Create src/android_mcp/tools/file.py**

```python
"""File operation tools for MCP."""

from android_mcp.tools.device import get_adb_client


async def adb_pull_file(serial: str, device_path: str, local_path: str) -> str:
    """Pull a file from the device to local filesystem.

    Args:
        serial: Device serial number
        device_path: Path to the file on the device
        local_path: Local destination path

    Returns:
        Pull result message.
    """
    client = get_adb_client()
    return client.pull_file(serial, device_path, local_path)


async def adb_push_file(serial: str, local_path: str, device_path: str) -> str:
    """Push a file from local filesystem to the device.

    Args:
        serial: Device serial number
        local_path: Path to the local file
        device_path: Destination path on the device

    Returns:
        Push result message.
    """
    client = get_adb_client()
    return client.push_file(serial, local_path, device_path)
```

- [ ] **Step 2: Commit**

```bash
git add src/android_mcp/tools/file.py tests/tools/test_file.py
git commit -m "feat: add file operation tools (pull, push)"
```

---

### Task 7: ADB Tools - Shell Commands

**Files:**
- Create: `src/android_mcp/tools/shell.py`

- [ ] **Step 1: Create src/android_mcp/tools/shell.py**

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add src/android_mcp/tools/shell.py
git commit -m "feat: add shell execution tool"
```

---

### Task 8: ADB Tools - Input Control

**Files:**
- Create: `src/android_mcp/tools/input.py`

- [ ] **Step 1: Create src/android_mcp/tools/input.py**

```python
"""Input control tools for MCP."""

from android_mcp.tools.device import get_adb_client


async def adb_tap(serial: str, x: int, y: int) -> str:
    """Simulate a tap at the specified coordinates.

    Args:
        serial: Device serial number
        x: X coordinate
        y: Y coordinate

    Returns:
        Command result.
    """
    client = get_adb_client()
    return client.tap(serial, x, y)


async def adb_swipe(
    serial: str,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    duration: int = 300
) -> str:
    """Simulate a swipe gesture.

    Args:
        serial: Device serial number
        x1: Start X coordinate
        y1: Start Y coordinate
        x2: End X coordinate
        y2: End Y coordinate
        duration: Duration in milliseconds

    Returns:
        Command result.
    """
    client = get_adb_client()
    return client.swipe(serial, x1, y1, x2, y2, duration)


async def adb_input_text(serial: str, text: str) -> str:
    """Input text on the device.

    Args:
        serial: Device serial number
        text: Text to input

    Returns:
        Command result.
    """
    client = get_adb_client()
    return client.input_text(serial, text)


async def adb_press_key(serial: str, keycode: int) -> str:
    """Press a key event.

    Args:
        serial: Device serial number
        keycode: Android keycode (e.g., 26 for POWER, 4 for BACK)

    Returns:
        Command result.
    """
    client = get_adb_client()
    return client.press_key(serial, keycode)
```

- [ ] **Step 2: Commit**

```bash
git add src/android_mcp/tools/input.py
git commit -m "feat: add input control tools (tap, swipe, text, key)"
```

---

### Task 9: ADB Tools - System Info

**Files:**
- Create: `src/android_mcp/tools/system.py`

- [ ] **Step 1: Create src/android_mcp/tools/system.py**

```python
"""System information tools for MCP."""

from typing import Any
from android_mcp.tools.device import get_adb_client


async def adb_get_screen_size(serial: str) -> dict[str, int]:
    """Get the screen resolution of the device.

    Args:
        serial: Device serial number

    Returns:
        Dictionary with width and height.
    """
    client = get_adb_client()
    return client.get_screen_size(serial)


async def adb_get_battery(serial: str) -> dict[str, Any]:
    """Get battery status of the device.

    Args:
        serial: Device serial number

    Returns:
        Battery information including level, status, etc.
    """
    client = get_adb_client()
    return client.get_battery(serial)


async def adb_get_properties(serial: str, keys: list[str] = None) -> dict[str, str]:
    """Get system properties from the device.

    Args:
        serial: Device serial number
        keys: Optional list of property keys to retrieve

    Returns:
        Dictionary of property key-value pairs.
    """
    client = get_adb_client()
    info = client.get_device_info(serial)
    if keys:
        return {k: v for k, v in info.items() if k in keys}
    return info
```

- [ ] **Step 2: Commit**

```bash
git add src/android_mcp/tools/system.py
git commit -m "feat: add system info tools (screen_size, battery, properties)"
```

---

### Task 10: scrcpy Client Implementation

**Files:**
- Create: `src/android_mcp/scrcpy/client.py`
- Create: `src/android_mcp/scrcpy/control.py`
- Create: `tests/scrcpy/test_client.py`

- [ ] **Step 1: Create src/android_mcp/scrcpy/client.py**

```python
"""scrcpy client for screen streaming and control."""

import subprocess
import socket
import time
from typing import Any


class ScrcpyClient:
    """Client for scrcpy operations."""

    def __init__(self):
        self._scrcpy_path = "scrcpy"
        self._process: subprocess.Popen | None = None
        self._port = 15555  # Default scrcpy port

    def start(self, serial: str, bit_rate: int = 8000000) -> dict[str, Any]:
        """Start scrcpy screen mirroring.

        Args:
            serial: Device serial number
            bit_rate: Video bit rate

        Returns:
            Status including port for streaming.
        """
        if self._process is not None:
            return {"status": "already_running", "port": self._port}

        # Start scrcpy with TCP/IP mode (requires ADB tunnel)
        cmd = [
            self._scrcpy_path,
            "-s", serial,
            "--tcpip",  # Enable TCP/IP mode
            "-b", str(bit_rate),
            "--port", str(self._port),
        ]

        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        time.sleep(2)  # Give scrcpy time to start

        return {
            "status": "started",
            "port": self._port,
            "serial": serial
        }

    def stop(self) -> str:
        """Stop scrcpy screen mirroring."""
        if self._process is None:
            return "scrcpy not running"

        self._process.terminate()
        self._process.wait()
        self._process = None
        return "scrcpy stopped"

    def is_running(self) -> bool:
        """Check if scrcpy is running."""
        if self._process is None:
            return False
        return self._process.poll() is None

    def screenshot(self, serial: str, output_path: str = "/sdcard/screenshot.png") -> str:
        """Take a screenshot using ADB.

        Args:
            serial: Device serial number
            output_path: Path to save screenshot on device

        Returns:
            Screenshot file path.
        """
        subprocess.run(
            ["adb", "-s", serial, "shell", "screencap", "-p", output_path],
            capture_output=True
        )
        return output_path
```

- [ ] **Step 2: Create src/android_mcp/scrcpy/control.py**

```python
"""Control commands for scrcpy."""

from typing import Any


class ScrcpyControl:
    """Control commands for scrcpy."""

    @staticmethod
    def create_touch_event(x: int, y: int, action: str = "down") -> dict[str, Any]:
        """Create a touch event.

        Args:
            x: X coordinate
            y: Y coordinate
            action: 'down', 'move', or 'up'

        Returns:
            Event dictionary.
        """
        return {
            "type": "touch",
            "action": action,
            "position": {"x": x, "y": y}
        }

    @staticmethod
    def create_key_event(keycode: int, action: str = "down") -> dict[str, Any]:
        """Create a key event.

        Args:
            keycode: Android keycode
            action: 'down', 'up', or 'click'

        Returns:
            Event dictionary.
        """
        return {
            "type": "key",
            "action": action,
            "keycode": keycode
        }

    @staticmethod
    def create_swipe_event(
        x1: int, y1: int,
        x2: int, y2: int,
        duration: int = 300
    ) -> dict[str, Any]:
        """Create a swipe event.

        Args:
            x1: Start X coordinate
            y1: Start Y coordinate
            x2: End X coordinate
            y2: End Y coordinate
            duration: Duration in milliseconds

        Returns:
            Event dictionary.
        """
        return {
            "type": "touch",
            "action": "swipe",
            "start": {"x": x1, "y": y1},
            "end": {"x": x2, "y": y2},
            "duration": duration
        }
```

- [ ] **Step 3: Commit**

```bash
git add src/android_mcp/scrcpy/client.py src/android_mcp/scrcpy/control.py tests/scrcpy/
git commit -m "feat: implement scrcpy client and control commands"
```

---

### Task 11: Screen Control Tools

**Files:**
- Create: `src/android_mcp/tools/screen.py`
- Create: `tests/tools/test_screen.py`

- [ ] **Step 1: Create src/android_mcp/tools/screen.py**

```python
"""Screen control tools using scrcpy for MCP."""

from typing import Any
from android_mcp.scrcpy.client import ScrcpyClient
from android_mcp.scrcpy.control import ScrcpyControl


# Global scrcpy client instance
_scrcpy_client: ScrcpyClient | None = None


def get_scrcpy_client() -> ScrcpyClient:
    """Get or create the global scrcpy client instance."""
    global _scrcpy_client
    if _scrcpy_client is None:
        _scrcpy_client = ScrcpyClient()
    return _scrcpy_client


async def scrcpy_start(serial: str, bit_rate: int = 8000000) -> dict[str, Any]:
    """Start screen mirroring via scrcpy.

    Args:
        serial: Device serial number
        bit_rate: Video bit rate (default 8Mbps)

    Returns:
        Status including streaming port.
    """
    client = get_scrcpy_client()
    return client.start(serial, bit_rate)


async def scrcpy_stop() -> str:
    """Stop screen mirroring.

    Returns:
        Status message.
    """
    client = get_scrcpy_client()
    return client.stop()


async def scrcpy_screenshot(serial: str, output_path: str = "/sdcard/screenshot.png") -> str:
    """Take a screenshot from the device.

    Args:
        serial: Device serial number
        output_path: Path on device to save screenshot

    Returns:
        Screenshot file path.
    """
    client = get_scrcpy_client()
    return client.screenshot(serial, output_path)


async def scrcpy_control(
    serial: str,
    action: str,
    params: dict[str, Any]
) -> str:
    """Send control command to scrcpy.

    Args:
        serial: Device serial number
        action: Action type ('tap', 'swipe', 'key', 'text')
        params: Action parameters

    Returns:
        Result message.
    """
    # Note: scrcpy control via network requires the device to be in TCP/IP mode
    # For now, we delegate most controls back to ADB input
    from android_mcp.tools.input import adb_tap, adb_swipe, adb_input_text, adb_press_key

    if action == "tap":
        x = params.get("x", 0)
        y = params.get("y", 0)
        return await adb_tap(serial, x, y)

    elif action == "swipe":
        x1 = params.get("x1", 0)
        y1 = params.get("y1", 0)
        x2 = params.get("x2", 0)
        y2 = params.get("y2", 0)
        duration = params.get("duration", 300)
        return await adb_swipe(serial, x1, y1, x2, y2, duration)

    elif action == "key":
        keycode = params.get("keycode", 0)
        return await adb_press_key(serial, keycode)

    elif action == "text":
        text = params.get("text", "")
        return await adb_input_text(serial, text)

    return f"Unknown action: {action}"
```

- [ ] **Step 2: Commit**

```bash
git add src/android_mcp/tools/screen.py tests/tools/test_screen.py
git commit -m "feat: add screen control tools (scrcpy_start, scrcpy_stop, screenshot, control)"
```

---

### Task 12: MCP Server Entry Point Integration

**Files:**
- Modify: `src/android_mcp/main.py`

- [ ] **Step 1: Update src/android_mcp/main.py to register all tools**

```python
"""Main entry point for the Android MCP Server."""

from fastmcp import FastMCP

from android_mcp.tools.device import adb_list_devices, adb_device_info
from android_mcp.tools.app import (
    adb_install_app,
    adb_uninstall_app,
    adb_list_packages,
    adb_start_app,
    adb_stop_app,
)
from android_mcp.tools.file import adb_pull_file, adb_push_file
from android_mcp.tools.shell import adb_shell
from android_mcp.tools.input import adb_tap, adb_swipe, adb_input_text, adb_press_key
from android_mcp.tools.system import (
    adb_get_screen_size,
    adb_get_battery,
    adb_get_properties,
)
from android_mcp.tools.screen import (
    scrcpy_start,
    scrcpy_stop,
    scrcpy_screenshot,
    scrcpy_control,
)


mcp = FastMCP("android-mcp-server")


# Device management tools
@mcp.tool()
async def adb_list_devices():
    """List all connected Android devices."""
    return await adb_list_devices()


@mcp.tool()
async def adb_device_info(serial: str):
    """Get detailed information about a specific device."""
    return await adb_device_info(serial)


# App management tools
@mcp.tool()
async def adb_install_app(serial: str, apk_path: str):
    """Install an APK on the device."""
    return await adb_install_app(serial, apk_path)


@mcp.tool()
async def adb_uninstall_app(serial: str, package_name: str):
    """Uninstall an application from the device."""
    return await adb_uninstall_app(serial, package_name)


@mcp.tool()
async def adb_list_packages(serial: str):
    """List all installed packages on the device."""
    return await adb_list_packages(serial)


@mcp.tool()
async def adb_start_app(serial: str, package_name: str, activity: str = None):
    """Start an application on the device."""
    return await adb_start_app(serial, package_name, activity)


@mcp.tool()
async def adb_stop_app(serial: str, package_name: str):
    """Force stop an application on the device."""
    return await adb_stop_app(serial, package_name)


# File operation tools
@mcp.tool()
async def adb_pull_file(serial: str, device_path: str, local_path: str):
    """Pull a file from the device to local filesystem."""
    return await adb_pull_file(serial, device_path, local_path)


@mcp.tool()
async def adb_push_file(serial: str, local_path: str, device_path: str):
    """Push a file from local filesystem to the device."""
    return await adb_push_file(serial, local_path, device_path)


# Shell tools
@mcp.tool()
async def adb_shell(serial: str, command: str):
    """Execute a shell command on the device."""
    return await adb_shell(serial, command)


# Input control tools
@mcp.tool()
async def adb_tap(serial: str, x: int, y: int):
    """Simulate a tap at the specified coordinates."""
    return await adb_tap(serial, x, y)


@mcp.tool()
async def adb_swipe(serial: str, x1: int, y1: int, x2: int, y2: int, duration: int = 300):
    """Simulate a swipe gesture."""
    return await adb_swipe(serial, x1, y1, x2, y2, duration)


@mcp.tool()
async def adb_input_text(serial: str, text: str):
    """Input text on the device."""
    return await adb_input_text(serial, text)


@mcp.tool()
async def adb_press_key(serial: str, keycode: int):
    """Press a key event."""
    return await adb_press_key(serial, keycode)


# System info tools
@mcp.tool()
async def adb_get_screen_size(serial: str):
    """Get the screen resolution of the device."""
    return await adb_get_screen_size(serial)


@mcp.tool()
async def adb_get_battery(serial: str):
    """Get battery status of the device."""
    return await adb_get_battery(serial)


@mcp.tool()
async def adb_get_properties(serial: str, keys: list[str] = None):
    """Get system properties from the device."""
    return await adb_get_properties(serial, keys)


# Screen control tools
@mcp.tool()
async def scrcpy_start(serial: str, bit_rate: int = 8000000):
    """Start screen mirroring via scrcpy."""
    return await scrcpy_start(serial, bit_rate)


@mcp.tool()
async def scrcpy_stop():
    """Stop screen mirroring."""
    return await scrcpy_stop()


@mcp.tool()
async def scrcpy_screenshot(serial: str, output_path: str = "/sdcard/screenshot.png"):
    """Take a screenshot from the device."""
    return await scrcpy_screenshot(serial, output_path)


@mcp.tool()
async def scrcpy_control(serial: str, action: str, params: dict):
    """Send control command to scrcpy."""
    return await scrcpy_control(serial, action, params)


if __name__ == "__main__":
    mcp.run()
```

- [ ] **Step 2: Commit**

```bash
git add src/android_mcp/main.py
git commit -m "feat: integrate all tools into MCP server entry point"
```

---

### Task 13: Final Verification

- [ ] **Step 1: Verify project structure**

Run: `find src -name "*.py" | sort`

Expected output:
```
src/android_mcp/__init__.py
src/android_mcp/main.py
src/android_mcp/adb/__init__.py
src/android_mcp/adb/client.py
src/android_mcp/adb/device.py
src/android_mcp/scrcpy/__init__.py
src/android_mcp/scrcpy/client.py
src/android_mcp/scrcpy/control.py
src/android_mcp/tools/__init__.py
src/android_mcp/tools/device.py
src/android_mcp/tools/app.py
src/android_mcp/tools/file.py
src/android_mcp/tools/shell.py
src/android_mcp/tools/input.py
src/android_mcp/tools/system.py
src/android_mcp/tools/screen.py
```

- [ ] **Step 2: Verify server can start**

Run: `python -c "from android_mcp.main import mcp; print('Server loaded successfully')"`

Expected: "Server loaded successfully"

- [ ] **Step 3: Commit final state**

```bash
git add -A
git commit -m "feat: complete Android MCP Server implementation"
```

---

## Self-Review Checklist

1. **Spec coverage:** All tools from the spec are implemented
   - [x] adb_list_devices, adb_device_info
   - [x] adb_install_app, adb_uninstall_app, adb_list_packages, adb_start_app, adb_stop_app
   - [x] adb_pull_file, adb_push_file
   - [x] adb_shell
   - [x] adb_tap, adb_swipe, adb_input_text, adb_press_key
   - [x] adb_get_screen_size, adb_get_battery, adb_get_properties
   - [x] scrcpy_start, scrcpy_stop, scrcpy_screenshot, scrcpy_control

2. **Placeholder scan:** No TBD/TODO placeholders found

3. **Type consistency:** All method signatures are consistent across files
