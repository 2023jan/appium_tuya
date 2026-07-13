from unittest.mock import MagicMock, call

import pytest
from selenium.common.exceptions import NoSuchElementException

from appium_auto.core.environment import (
    AppConfig,
    EnvironmentConfig,
    IotDeviceConfig,
    PhoneConfig,
)
from appium_auto.pages.home_page import HomePage


def _environment() -> EnvironmentConfig:
    """构造页面单元测试使用的最小环境配置。"""

    return EnvironmentConfig(
        phone=PhoneConfig(udid="test-device"),
        app=AppConfig(
            package="test.app",
            activity="test.Activity",
            display_name="Test App",
        ),
        iot_device=IotDeviceConfig(name="sensor", type="sensor-type"),
    )


def test_home_locators_come_from_environment():
    """验证首页 locator 使用环境中的 package 和设备名称。"""

    page = HomePage(MagicMock(), _environment())

    assert "test.app:id/deviceName" in page.device_selector
    assert 'text("sensor")' in page.device_selector
    assert "test.app:id/toolbar_top_view" in page.home_menu_xpath


def test_open_add_device_always_restores_multiwindow_setting():
    """验证添加设备菜单操作完成后恢复 Appium 多窗口设置。"""

    driver = MagicMock()
    menu = MagicMock()
    add_device = MagicMock(text="添加设备")
    driver.find_element.side_effect = [menu, add_device]
    page = HomePage(driver, _environment())

    page.open_add_device_page()

    assert driver.update_settings.mock_calls == [
        call({"enableMultiWindows": True}),
        call({"enableMultiWindows": False}),
    ]
    menu.click.assert_called_once_with()
    add_device.click.assert_called_once_with()


def test_assert_device_absent_accepts_full_list_search_without_target():
    """验证完整列表中找不到目标设备时，设备不存在断言通过。"""

    driver = MagicMock()
    driver.find_elements.return_value = []
    driver.find_element.side_effect = NoSuchElementException()
    page = HomePage(driver, _environment())

    page.assert_device_absent()


def test_assert_device_absent_rejects_visible_target():
    """验证目标设备仍可见时，设备不存在断言明确失败。"""

    driver = MagicMock()
    driver.find_elements.return_value = [MagicMock()]
    page = HomePage(driver, _environment())

    with pytest.raises(AssertionError, match="sensor"):
        page.assert_device_absent()
