import logging

from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from appium_auto.core.environment import EnvironmentConfig
from appium_auto.pages.add_device_page import AddDevicePage
from appium_auto.pages.device_panel_page import DevicePanelPage
from appium_auto.pages.device_settings_page import DeviceSettingsPage
from appium_auto.pages.home_page import HomePage


class DeviceLifecycleFlow:
    def __init__(
        self, driver: webdriver.Remote, environment: EnvironmentConfig
    ) -> None:
        self.driver = driver
        self.environment = environment
        self.home = HomePage(driver, environment)
        self.panel = DevicePanelPage(driver, environment)
        self.settings = DeviceSettingsPage(driver, environment)
        self.add_device = AddDevicePage(driver, environment)

    def activate_and_return_home(self) -> None:
        self.driver.activate_app(self.environment.app.package)
        WebDriverWait(self.driver, 20).until(
            lambda driver: driver.current_package == self.environment.app.package
        )
        self.home.return_to_home()

    def open_device_details(self) -> None:
        self.home.find_device().click()
        self.panel.assert_details()

    def open_device_settings(self) -> None:
        self.open_device_details()
        self.panel.open_settings()
        self.settings.assert_loaded()

    def unbind_device(self) -> None:
        self.open_device_settings()
        self.settings.unbind()
        self.settings.wait_until_home(self.home.home_tab_selector)
        self.home.assert_device_absent()

    def open_add_device(self) -> None:
        self.home.open_add_device_page()
        self.add_device.wait_until_loaded()

    def submit_default_wifi(self) -> None:
        self.add_device.continue_from_detected_device()
        self.add_device.submit_default_wifi()

    def wait_for_pairing_success(self, logger: logging.Logger) -> None:
        complete_button = self.add_device.wait_for_pairing_success(logger)
        complete_button.click()
        self.panel.assert_details()
