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
    page = HomePage(MagicMock(), _environment())

    assert "test.app:id/deviceName" in page.device_selector
    assert 'text("sensor")' in page.device_selector
    assert "test.app:id/toolbar_top_view" in page.home_menu_xpath


def test_open_add_device_always_restores_multiwindow_setting():
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
    driver = MagicMock()
    driver.find_elements.return_value = []
    driver.find_element.side_effect = NoSuchElementException()
    page = HomePage(driver, _environment())

    page.assert_device_absent()


def test_assert_device_absent_rejects_visible_target():
    driver = MagicMock()
    driver.find_elements.return_value = [MagicMock()]
    page = HomePage(driver, _environment())

    with pytest.raises(AssertionError, match="sensor"):
        page.assert_device_absent()
