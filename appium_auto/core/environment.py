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
    udid: str
    platform_name: str = "Android"
    automation_name: str = "UiAutomator2"
    skip_device_initialization: bool = True
    skip_server_installation: bool = True


@dataclass(frozen=True)
class AppConfig:
    package: str
    activity: str
    display_name: str
    display_name_aliases: tuple[str, ...] = ()
    version: str = ""


@dataclass(frozen=True)
class IotDeviceConfig:
    name: str
    type: str


@dataclass(frozen=True, repr=False)
class WifiConfig:
    ssid: str
    password: str

    def __repr__(self) -> str:
        return f"WifiConfig(ssid={self.ssid!r}, password='***')"


@dataclass(frozen=True)
class EnvironmentConfig:
    phone: PhoneConfig
    app: AppConfig
    iot_device: IotDeviceConfig
    wifi: WifiConfig | None = field(default=None, repr=False)


def _read_yaml(path: Path) -> dict[str, Any]:
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
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


def _required(mapping: dict[str, Any], section: str, key: str) -> str:
    value = mapping.get(section, {}).get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"环境配置缺少必填字段：{section}.{key}")
    return value.strip()


def load_wifi_config(path: Path | None = None) -> WifiConfig | None:
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
    data = _read_yaml(DEFAULT_CONFIG_PATH)
    configured_override = path
    if configured_override is None:
        configured_override = Path(
            os.getenv("APPIUM_ENV_FILE", str(LOCAL_CONFIG_PATH))
        )
    if configured_override.is_file():
        data = _merge(data, _read_yaml(configured_override))

    env_udid = os.getenv("APPIUM_UDID")
    if env_udid:
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
        wifi=None,
    )
