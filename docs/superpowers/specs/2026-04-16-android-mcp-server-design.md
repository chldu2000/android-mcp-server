# Android MCP Server 设计方案

## 概述

使用 `fastmcp` 构建一个 MCP Server，通过 ADB 和 scrcpy 为外部 LLM 提供操作安卓设备的能力。

**连接方式**：USB 和网络（ADB）

**架构模式**：单 Server 模式，统一入口

---

## 项目结构

```
android-mcp-server/
├── pyproject.toml          # 依赖管理 (uv)
├── src/
│   └── android_mcp/
│       ├── __init__.py
│       ├── main.py          # fastmcp server 入口
│       ├── adb/
│       │   ├── __init__.py
│       │   ├── client.py    # ADB 客户端封装
│       │   └── device.py    # 设备操作
│       ├── scrcpy/
│       │   ├── __init__.py
│       │   ├── client.py    # scrcpy 客户端封装
│       │   └── control.py   # 控制指令
│       └── tools/
│           ├── __init__.py
│           ├── device.py     # 设备管理工具
│           ├── app.py        # 应用管理工具
│           ├── file.py       # 文件操作工具
│           ├── shell.py      # Shell工具
│           ├── input.py      # 输入控制工具
│           ├── system.py     # 系统信息工具
│           └── screen.py     # 屏幕控制工具
```

---

## 依赖

- `fastmcp` — MCP Server 框架
- `adb-shell` — ADB 通信库
- `scrcpy` — 屏幕推流（通过 subprocess 调用）
- `uv` — 依赖管理

---

## 工具清单

### 设备管理

| 工具 | 说明 | 参数 |
|------|------|------|
| `adb_list_devices` | 列出已连接设备 | 无 |
| `adb_device_info` | 获取指定设备详细信息 | `serial: str` |

### 应用管理

| 工具 | 说明 | 参数 |
|------|------|------|
| `adb_install_app` | 安装 APK | `serial: str`, `apk_path: str` |
| `adb_uninstall_app` | 卸载应用 | `serial: str`, `package_name: str` |
| `adb_list_packages` | 列出已安装应用 | `serial: str` |
| `adb_start_app` | 启动应用 | `serial: str`, `package_name: str` |
| `adb_stop_app` | 强制停止应用 | `serial: str`, `package_name: str` |

### 文件操作

| 工具 | 说明 | 参数 |
|------|------|------|
| `adb_pull_file` | 从设备拉取文件 | `serial: str`, `device_path: str`, `local_path: str` |
| `adb_push_file` | 推送文件到设备 | `serial: str`, `local_path: str`, `device_path: str` |

### Shell 命令

| 工具 | 说明 | 参数 |
|------|------|------|
| `adb_shell` | 执行 shell 命令 | `serial: str`, `command: str` |

### 输入控制

| 工具 | 说明 | 参数 |
|------|------|------|
| `adb_tap` | 模拟点击 | `serial: str`, `x: int`, `y: int` |
| `adb_swipe` | 模拟滑动 | `serial: str`, `x1: int`, `y1: int`, `x2: int`, `y2: int`, `duration: int` |
| `adb_input_text` | 输入文本 | `serial: str`, `text: str` |
| `adb_press_key` | 按物理按键 | `serial: str`, `keycode: int` |

### 系统信息

| 工具 | 说明 | 参数 |
|------|------|------|
| `adb_get_screen_size` | 获取屏幕分辨率 | `serial: str` |
| `adb_get_battery` | 获取电池状态 | `serial: str` |
| `adb_get_properties` | 获取系统属性 | `serial: str`, `keys: list[str]` |

### 屏幕控制（scrcpy）

| 工具 | 说明 | 参数 |
|------|------|------|
| `scrcpy_start` | 启动屏幕推流 | `serial: str` |
| `scrcpy_stop` | 停止推流 | `serial: str` |
| `scrcpy_screenshot` | 截取当前屏幕 | `serial: str` |
| `scrcpy_control` | 发送控制指令 | `serial: str`, `action: str`, `params: dict` |

---

## 数据流

```
LLM
 └── android-mcp-server
      ├── ADB Client ──> ADB ──> Android Device (USB/Network)
      └── scrcpy Client ──> scrcpy ──> Android Device (USB/Network)
```

---

## 多设备支持

采用**单设备模式**：每次操作一个指定设备，通过 `serial` 参数指定目标设备。

---

## 实现顺序

1. 项目脚手架（pyproject.toml、目录结构）
2. ADB Client 封装
3. ADB 工具实现（设备管理、应用管理、文件操作、Shell、输入控制、系统信息）
4. scrcpy Client 封装
5. scrcpy 工具实现
6. MCP Server 入口整合
7. 测试验证
