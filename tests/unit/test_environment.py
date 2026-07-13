from pathlib import Path

import pytest

from appium_auto.core.environment import load_environment, load_wifi_config


def _write(path: Path, content: str) -> Path:
    """将测试配置写入临时目录并返回文件路径。"""

    path.write_text(content, encoding="utf-8")
    return path


def test_local_config_overrides_default(monkeypatch, tmp_path):
    """验证 local.yaml 只覆盖指定字段，其余字段继续继承默认配置。"""

    override = _write(
        tmp_path / "local.yaml",
        "phone:\n  udid: local-device\niot_device:\n  name: local-sensor\n",
    )
    monkeypatch.delenv("APPIUM_UDID", raising=False)
    monkeypatch.setenv("WIFI_CONFIG_FILE", str(tmp_path / "missing-wifi.yaml"))

    environment = load_environment(override)

    assert environment.phone.udid == "local-device"
    assert environment.iot_device.name == "local-sensor"
    assert environment.app.package == "com.tuya.smartlifeiot"
    assert environment.wifi is None


def test_udid_environment_variable_has_highest_priority(monkeypatch, tmp_path):
    """验证 APPIUM_UDID 的优先级高于本地 YAML 配置。"""

    override = _write(tmp_path / "local.yaml", "phone:\n  udid: yaml-device\n")
    monkeypatch.setenv("APPIUM_UDID", "environment-device")
    monkeypatch.setenv("WIFI_CONFIG_FILE", str(tmp_path / "missing-wifi.yaml"))

    environment = load_environment(override)

    assert environment.phone.udid == "environment-device"


def test_required_environment_field_reports_actionable_error(monkeypatch, tmp_path):
    """验证必填字段为空时，错误信息能指出具体配置路径。"""

    override = _write(tmp_path / "local.yaml", "app:\n  package: ''\n")
    monkeypatch.setenv("APPIUM_UDID", "test-device")
    monkeypatch.setenv("WIFI_CONFIG_FILE", str(tmp_path / "missing-wifi.yaml"))

    with pytest.raises(ValueError, match=r"app\.package"):
        load_environment(override)


def test_wifi_config_is_optional(monkeypatch, tmp_path):
    """验证 Wi-Fi 配置文件不存在时返回空值而不是阻塞普通用例。"""

    missing_path = tmp_path / "missing.yaml"
    monkeypatch.delenv("WIFI_CONFIG_FILE", raising=False)

    assert load_wifi_config(missing_path) is None


def test_wifi_config_repr_hides_password(tmp_path):
    """验证 Wi-Fi 对象保留真实密码但调试输出始终脱敏。"""

    wifi_path = _write(
        tmp_path / "wifi.yaml",
        "wifi:\n  ssid: test-network\n  password: top-secret\n",
    )

    wifi = load_wifi_config(wifi_path)

    assert wifi is not None
    assert wifi.password == "top-secret"
    assert "top-secret" not in repr(wifi)
    assert "***" in repr(wifi)


def test_environment_does_not_load_wifi_before_case03(monkeypatch, tmp_path):
    """验证 CASE00-02 使用的环境加载器不会自动读取 Wi-Fi 凭据。"""

    override = _write(tmp_path / "local.yaml", "phone:\n  udid: test-device\n")
    wifi_path = _write(
        tmp_path / "wifi.yaml",
        "wifi:\n  ssid: test-network\n  password: top-secret\n",
    )
    monkeypatch.setenv("WIFI_CONFIG_FILE", str(wifi_path))

    environment = load_environment(override)

    assert environment.wifi is None
