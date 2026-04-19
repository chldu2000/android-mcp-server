# uiautomator2 UI Dump Replacement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace ADB `uiautomator dump` with uiautomator2 library in `ui.py` for improved reliability.

**Architecture:** Add uiautomator2 wrapper class with lazy initialization per device serial. Functions try uiautomator2 first, fall back to ADB shell method on failure.

**Tech Stack:** Python, uiautomator2, ADB

---

## Files

- Modify: `pyproject.toml` - Add uiautomator2 dependency
- Modify: `src/android_mcp/tools/ui.py` - Add wrapper and update functions

---

## Task 1: Add uiautomator2 dependency

- [ ] **Step 1: Add uiautomator2 to dependencies in pyproject.toml**

```toml
[project]
dependencies = [
    "fastmcp>=0.1.0",
    "uiautomator2>=2.3.0",
]
```

Run: `cat pyproject.toml`
Expected: uiautomator2 added to dependencies

- [ ] **Step 2: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add uiautomator2 dependency"
```

---

## Task 2: Create Uiautomator2Device wrapper class

- [ ] **Step 1: Add Uiautomator2Device class to ui.py**

Read `src/android_mcp/tools/ui.py` first.

Add this class after imports (line ~6):

```python
class Uiautomator2Device:
    """Wrapper for uiautomator2 device connection with lazy initialization."""

    def __init__(self, serial: str):
        self.serial = serial
        self._device = None

    @property
    def device(self):
        """Lazily connect to device via uiautomator2."""
        if self._device is None:
            import uiautomator2 as u2
            self._device = u2.connect(self.serial)
        return self._device

    def dump_hierarchy(self) -> str:
        """Dump UI hierarchy as XML string."""
        return self.device.dump_hierarchy()
```

- [ ] **Step 2: Commit**

```bash
git add src/android_mcp/tools/ui.py
git commit -m "feat(ui): add Uiautomator2Device wrapper class"
```

---

## Task 3: Add global device cache and helper function

- [ ] **Step 1: Add device cache and get_u2_device function**

After the `Uiautomator2Device` class definition, add:

```python
# Global uiautomator2 device cache
_u2_devices: dict[str, Uiautomator2Device] = {}


def get_u2_device(serial: str) -> Uiautomator2Device:
    """Get or create a Uiautomator2Device for the given serial."""
    if serial not in _u2_devices:
        _u2_devices[serial] = Uiautomator2Device(serial)
    return _u2_devices[serial]
```

- [ ] **Step 2: Commit**

```bash
git add src/android_mcp/tools/ui.py
git commit -m "feat(ui): add global uiautomator2 device cache"
```

---

## Task 4: Update adb_dump_ui_tree to use uiautomator2 with fallback

- [ ] **Step 1: Replace adb_dump_ui_tree implementation**

Read current `adb_dump_ui_tree` function (lines 8-27).

Replace with:

```python
async def adb_dump_ui_tree(serial: str) -> str:
    """Dump the UI hierarchy tree from the device.

    Uses uiautomator2 to dump the current UI hierarchy as XML,
    with fallback to ADB shell uiautomator dump on failure.

    Args:
        serial: Device serial number

    Returns:
        UI hierarchy XML string.
    """
    try:
        u2_dev = get_u2_device(serial)
        return u2_dev.dump_hierarchy()
    except Exception as e:
        import logging
        logging.warning(f"uiautomator2 failed, falling back to ADB: {e}")
        # Fallback to original ADB method
        client = get_adb_client()
        client.shell(serial, "uiautomator dump /sdcard/window_dump.xml")
        output = client.shell(serial, "cat /sdcard/window_dump.xml")
        client.shell(serial, "rm /sdcard/window_dump.xml")
        return output
```

- [ ] **Step 2: Commit**

```bash
git add src/android_mcp/tools/ui.py
git commit -m "feat(ui): use uiautomator2 in adb_dump_ui_tree with fallback"
```

---

## Task 5: Update adb_find_element to use uiautomator2 selectors with fallback

- [ ] **Step 1: Review current adb_find_element implementation**

Read current `adb_find_element` function (lines 91-187).

- [ ] **Step 2: Replace adb_find_element with uiautomator2 implementation**

Replace the function with:

```python
async def adb_find_element(
    serial: str,
    resource_id: str = None,
    text: str = None,
    content_desc: str = None,
    class_name: str = None,
    enabled: bool = None,
    clickable: bool = None,
    focusable: bool = None,
) -> list[dict[str, Any]]:
    """Find UI elements by their attributes.

    Uses uiautomator2 selectors with fallback to ADB uiautomator dump.
    All provided criteria must match (AND logic).

    Args:
        serial: Device serial number
        resource_id: Resource ID to match (e.g., 'com.example:id/btn')
        text: Text content to match
        content_desc: Content description to match
        class_name: View class to match (e.g., 'android.widget.Button')
        enabled: Filter by enabled state
        clickable: Filter by clickable state
        focusable: Filter by focusable state

    Returns:
        List of matching elements with their attributes and available actions.
    """
    if all(p is None for p in [resource_id, text, content_desc, class_name, enabled, clickable, focusable]):
        return []

    try:
        u2_dev = get_u2_device(serial)
        return _u2_find_element_impl(u2_dev, resource_id, text, content_desc, class_name, enabled, clickable, focusable)
    except Exception as e:
        import logging
        logging.warning(f"uiautomator2 failed in find_element, falling back to ADB: {e}")
        return _adb_find_element_impl(serial, resource_id, text, content_desc, class_name, enabled, clickable, focusable)


def _u2_find_element_impl(
    u2_dev: Uiautomator2Device,
    resource_id: str = None,
    text: str = None,
    content_desc: str = None,
    class_name: str = None,
    enabled: bool = None,
    clickable: bool = None,
    focusable: bool = None,
) -> list[dict[str, Any]]:
    """Find elements using uiautomator2 selectors."""
    device = u2_dev.device

    # Build selector chain
    if resource_id is not None:
        device = device(resourceId=resource_id)
    if text is not None:
        device = device(text=text)
    if content_desc is not None:
        device = device(description=content_desc)
    if class_name is not None:
        device = device(className=class_name)
    if enabled is not None:
        device = device(enabled=enabled)
    if clickable is not None:
        device = device(clickable=clickable)
    if focusable is not None:
        device = device(focusable=focusable)

    # Get all matching elements
    elements = device.all()
    results = []

    for elem in elements:
        bounds = elem.bounds()
        attrs = {
            "resource_id": elem.attrib.get("resourceId"),
            "text": elem.attrib.get("text"),
            "content_desc": elem.attrib.get("content-desc"),
            "class": elem.attrib.get("class"),
            "bounds": {"x": bounds[0], "y": bounds[1], "width": bounds[2] - bounds[0], "height": bounds[3] - bounds[1]},
            "enabled": elem.attrib.get("enabled") == "true",
            "clickable": elem.attrib.get("clickable") == "true",
            "long_clickable": elem.attrib.get("long-clickable") == "true",
            "focusable": elem.attrib.get("focusable") == "true",
        }
        actions = []
        if bounds:
            actions.append("tap")
        if attrs.get("clickable"):
            actions.append("click")
        if attrs.get("long_clickable"):
            actions.append("long_click")
        attrs["actions"] = actions
        results.append(attrs)

    return results


def _adb_find_element_impl(
    serial: str,
    resource_id: str = None,
    text: str = None,
    content_desc: str = None,
    class_name: str = None,
    enabled: bool = None,
    clickable: bool = None,
    focusable: bool = None,
) -> list[dict[str, Any]]:
    """Find elements using ADB uiautomator dump (fallback)."""
    client = get_adb_client()
    client.shell(serial, "uiautomator dump /sdcard/window_dump.xml")
    xml_content = client.shell(serial, "cat /sdcard/window_dump.xml")
    client.shell(serial, "rm /sdcard/window_dump.xml")

    if not xml_content or not xml_content.strip():
        return []

    node_pattern = re.compile(r'<node\s+(.*?)(?:/>|>)', re.DOTALL)
    results = []

    for match in node_pattern.finditer(xml_content):
        node_attrs_str = match.group(1)
        attrs = _parse_node_attributes(node_attrs_str)

        if resource_id is not None and attrs.get("resource_id") != resource_id:
            continue
        if text is not None and attrs.get("text") != text:
            continue
        if content_desc is not None and attrs.get("content_desc") != content_desc:
            continue
        if class_name is not None and attrs.get("class") != class_name:
            continue
        if enabled is not None and attrs.get("enabled") != enabled:
            continue
        if clickable is not None and attrs.get("clickable") != clickable:
            continue
        if focusable is not None and attrs.get("focusable") != focusable:
            continue

        element = {
            "resource_id": attrs.get("resource_id"),
            "text": attrs.get("text"),
            "content_desc": attrs.get("content_desc"),
            "class": attrs.get("class"),
            "bounds": _parse_bounds(attrs.get("bounds", "[0,0][0,0]")),
            "enabled": attrs.get("enabled"),
            "clickable": attrs.get("clickable"),
            "long_clickable": attrs.get("long_clickable"),
            "focusable": attrs.get("focusable"),
            "actions": _get_element_actions(attrs),
        }
        results.append(element)

    return results
```

- [ ] **Step 3: Commit**

```bash
git add src/android_mcp/tools/ui.py
git commit -m "feat(ui): use uiautomator2 selectors in adb_find_element with fallback"
```

---

## Task 6: Verify syntax and run tests

- [ ] **Step 1: Check Python syntax**

Run: `python -m py_compile src/android_mcp/tools/ui.py`
Expected: No output (success)

- [ ] **Step 2: Run existing tests if any**

Run: `pytest -v 2>/dev/null || echo "No tests found"`
Expected: Tests pass or no tests

- [ ] **Step 3: Verify import works**

Run: `cd /Users/chldu/Workspace/android-mcp-server && uv run python -c "from android_mcp.tools.ui import adb_dump_ui_tree, adb_find_element; print('Import OK')"`
Expected: "Import OK"

- [ ] **Step 4: Commit any remaining changes**

```bash
git add -A
git commit -m "chore: verify syntax and imports"
```

---

## Task 7: Update README documentation

- [ ] **Step 1: Update README if needed**

Read README lines 107-113 (UI Elements section). No changes needed if existing description still applies.

---

## Summary

| Task | Description |
|------|-------------|
| 1 | Add uiautomator2 dependency |
| 2 | Add Uiautomator2Device wrapper class |
| 3 | Add global device cache |
| 4 | Update adb_dump_ui_tree with uiautomator2 + fallback |
| 5 | Update adb_find_element with uiautomator2 selectors + fallback |
| 6 | Verify syntax and imports |
| 7 | Update README (if needed) |