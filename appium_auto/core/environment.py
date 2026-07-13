import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


CONFIG_DIR = Path(__file__).parents[1] / "config"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "default.yaml"
LOCAL_CONFIG_PATH = CONFIG_DIR / "local.yaml"
WIFI_CONFIG_PATH = CONFIG_DIR / "wifi.local.yaml"


@dataclass(frozen=True)
class PhoneConfig:
    """保存 Android 测试手机及 UiAutomator2 初始化策略。"""

    udid: str
    platform_name: str = "Android"
    automation_name: str = "UiAutomator2"
    skip_device_initialization: bool = True
    skip_server_installation: bool = True


@dataclass(frozen=True)
class AppConfig:
    """保存待测 App 的启动信息、显示名称和版本。"""

    package: str
    activity: str
    display_name: str
    display_name_aliases: tuple[str, ...] = ()
    version: str = ""


@dataclass(frozen=True)
class IotDeviceConfig:
    """保存测试目标 IoT 设备的业务名称和类型。"""

    name: str
    type: str


@dataclass(frozen=True, repr=False)
class WifiConfig:
    """保存本地 Wi-Fi 凭据，并避免在对象输出中暴露密码。"""

    ssid: str
    password: str

    def __repr__(self) -> str:
        """返回隐藏密码的调试文本，防止凭据进入日志和异常信息。"""

        return f"WifiConfig(ssid={self.ssid!r}, password='***')"


@dataclass(frozen=True)
class EnvironmentConfig:
    """组合手机、App、IoT 设备以及可选 Wi-Fi 配置。"""

    phone: PhoneConfig
    app: AppConfig
    iot_device: IotDeviceConfig
    wifi: WifiConfig | None = field(default=None, repr=False)


def _read_yaml(path: Path) -> dict[str, Any]:
    """读取 YAML 配置并将文件、语法和顶层类型错误转换为可操作提示。"""

    try:
        content = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except FileNotFoundError as error:
        raise ValueError(f"环境配置文件不存在：{path}") from error
    except yaml.YAMLError as error:
        raise ValueError(f"环境配置 YAML 无法解析：{path}，原因：{error}") from error
    if not isinstance(content, dict):
        raise ValueError(f"环境配置顶层必须是映射：{path}")
    return content


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """递归合并配置映射，使局部文件只需声明需要覆盖的字段。"""

    result = dict(base)
    for key, value in override.items():
        # 配置分节需要逐层合并，否则只覆盖 udid 也会丢失同节的默认策略。
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


def _required(mapping: dict[str, Any], section: str, key: str) -> str:
    """读取并校验必填字符串字段，返回去除首尾空白后的值。"""

    value = mapping.get(section, {}).get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"环境配置缺少必填字段：{section}.{key}")
    return value.strip()


def load_wifi_config(path: Path | None = None) -> WifiConfig | None:
    """按显式路径或 WIFI_CONFIG_FILE 加载可选的本地 Wi-Fi 凭据。"""

    configured_path = path or Path(
        os.getenv("WIFI_CONFIG_FILE", str(WIFI_CONFIG_PATH))
    )
    if not configured_path.is_file():
        return None
    data = _read_yaml(configured_path)
    ssid = _required(data, "wifi", "ssid")
    password = _required(data, "wifi", "password")
    return WifiConfig(ssid=ssid, password=password)


def load_environment(path: Path | None = None) -> EnvironmentConfig:
    """按默认值、本地文件、环境变量的顺序加载运行环境。"""

    data = _read_yaml(DEFAULT_CONFIG_PATH)
    configured_override = path
    if configured_override is None:
        configured_override = Path(
            os.getenv("APPIUM_ENV_FILE", str(LOCAL_CONFIG_PATH))
        )
    if configured_override.is_file():
        # local.yaml 只承载机器差异，未声明的字段继续使用可提交默认值。
        data = _merge(data, _read_yaml(configured_override))

    env_udid = os.getenv("APPIUM_UDID")
    if env_udid:
        # 运行时变量优先级最高，便于 CI 或临时切换测试手机。
        data = _merge(data, {"phone": {"udid": env_udid}})

    phone_data = data.get("phone", {})
    app_data = data.get("app", {})
    aliases = app_data.get("display_name_aliases", [])
    if not isinstance(aliases, list) or not all(
        isinstance(alias, str) for alias in aliases
    ):
        raise ValueError("环境配置字段 app.display_name_aliases 必须是字符串列表")

    return EnvironmentConfig(
        phone=PhoneConfig(
            udid=_required(data, "phone", "udid"),
            platform_name=_required(data, "phone", "platform_name"),
            automation_name=_required(data, "phone", "automation_name"),
            skip_device_initialization=bool(
                phone_data.get("skip_device_initialization", True)
            ),
            skip_server_installation=bool(
                phone_data.get("skip_server_installation", True)
            ),
        ),
        app=AppConfig(
            package=_required(data, "app", "package"),
            activity=_required(data, "app", "activity"),
            display_name=_required(data, "app", "display_name"),
            display_name_aliases=tuple(aliases),
            version=str(app_data.get("version", "")),
        ),
        iot_device=IotDeviceConfig(
            name=_required(data, "iot_device", "name"),
            type=_required(data, "iot_device", "type"),
        ),
        # CASE00-02 不读取 Wi-Fi 文件，避免凭据无意进入普通运行上下文。
        wifi=None,
    )
