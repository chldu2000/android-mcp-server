"""scrcpy client for screen streaming and control."""

import subprocess
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