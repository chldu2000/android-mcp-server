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