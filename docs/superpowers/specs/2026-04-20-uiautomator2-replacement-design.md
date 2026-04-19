# uiautomator2 UI Dump Replacement Design

## Overview

Replace the current ADB `uiautomator dump` approach with the uiautomator2 Python library for improved reliability in UI hierarchy dumping and element finding.

## Current State

- `adb_dump_ui_tree`: Uses `uiautomator dump` + `cat` via ADB shell, manual XML parsing
- `adb_find_element`: Uses `uiautomator dump` + regex parsing, no selector support

## Target State

### New Dependencies

Add `uiautomator2` to project dependencies (optional/wrapped).

### Changes to `src/android_mcp/tools/ui.py`

1. Add uiautomator2 device wrapper class (lazy initialization per device serial)
2. `adb_dump_ui_tree`: Use uiautomator2's `dump_hierarchy()` with XML output
3. `adb_find_element`: Use uiautomator2 selectors (`resourceId`, `text`, `contentDesc`, `className`, `enabled`, `clickable`, `focusable`)
4. **Keep existing ADB-based implementations as fallback** if uiautomator2 fails

### uiautomator2 Wrapper

```python
class Uiautomator2Device:
    def __init__(self, serial: str):
        self.serial = serial
        self._device = None

    @property
    def device(self):
        if self._device is None:
            import uiautomator2 as u2
            self._device = u2.connect(self.serial)
        return self._device
```

### Error Handling

- If uiautomator2 connect fails → fall back to ADB shell method
- If uiautomator2 operation fails → fall back to ADB shell method
- Log warnings when falling back

## Files to Modify

- `src/android_mcp/tools/ui.py` - Add uiautomator2 wrapper, update dump/find functions
- `pyproject.toml` - Add uiautomator2 dependency

## Testing

- Verify uiautomator2 path: `which uiautomator2` or `python -c "import uiautomator2"`
- Test on real device with UI elements