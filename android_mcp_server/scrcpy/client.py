"""scrcpy client for controlling scrcpy sessions."""

import subprocess
import signal
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ScrcpyOptions:
    """Options for scrcpy."""
    bit_rate: int = 8000000
    max_fps: int = 60
    max_size: int = 1920
    serial: Optional[str] = None
    stay_awake: bool = True
    turn_screen_off: bool = False


class ScrcpyClient:
    """Client for managing scrcpy sessions."""

    def __init__(self):
        self._process: Optional[subprocess.Popen] = None
        self._options: Optional[ScrcpyOptions] = None

    def start(self, options: ScrcpyOptions = None) -> bool:
        """Start scrcpy.

        Args:
            options: scrcpy options

        Returns:
            True if started successfully
        """
        if self._process:
            return False

        if options is None:
            options = ScrcpyOptions()

        self._options = options

        cmd = ["scrcpy"]

        if options.bit_rate:
            cmd.extend(["--bit-rate", str(options.bit_rate)])
        if options.max_fps:
            cmd.extend(["--max-fps", str(options.max_fps)])
        if options.max_size:
            cmd.extend(["--max-size", str(options.max_size)])
        if options.stay_awake:
            cmd.append("--stay-awake")
        if options.turn_screen_off:
            cmd.append("--turn-screen-off")
        if options.serial:
            cmd.extend(["--serial", options.serial])

        # Run scrcpy without creating a window (for streaming purposes)
        # scrcpy doesn't support headless mode natively, so this is mainly
        # for checking if scrcpy is available
        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return True
        except FileNotFoundError:
            raise RuntimeError("scrcpy not found. Is scrcpy installed?")
        except Exception as e:
            raise RuntimeError(f"Failed to start scrcpy: {e}")

    def stop(self) -> bool:
        """Stop scrcpy.

        Returns:
            True if stopped successfully
        """
        if not self._process:
            return False

        try:
            # Kill the process group to ensure all child processes are terminated
            os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
            self._process.wait(timeout=5)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            try:
                os.killpg(os.getpgid(self._process.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
        finally:
            self._process = None

        return True

    @property
    def is_running(self) -> bool:
        """Check if scrcpy is running."""
        if not self._process:
            return False
        return self._process.poll() is None

    def get_frame(self) -> Optional[bytes]:
        """Get the current frame from scrcpy.

        Note: scrcpy doesn't provide an API for this directly.
        This would require using scrcpy's socket interface or
        a modified version of scrcpy.

        Returns:
            None - scrcpy streams to a window, not to a buffer
        """
        return None


# Global scrcpy client instance
scrcpy_client = ScrcpyClient()
