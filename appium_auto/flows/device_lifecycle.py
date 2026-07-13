import logging

from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from appium_auto.core.environment import EnvironmentConfig
from appium_auto.pages.add_device_page import AddDevicePage
from appium_auto.pages.device_panel_page import DevicePanelPage
from appium_auto.pages.device_settings_page import DeviceSettingsPage
from appium_auto.pages.home_page import HomePage


class DeviceLifecycleFlow:
    """组合多个 Page Object，提供设备查看、解绑和重新配网流程。"""

    def __init__(
        self, driver: webdriver.Remote, environment: EnvironmentConfig
    ) -> None:
        """使用同一 Driver 和环境构建设备生命周期所需页面对象。"""

        self.driver = driver
        self.environment = environment
        self.home = HomePage(driver, environment)
        self.panel = DevicePanelPage(driver, environment)
        self.settings = DeviceSettingsPage(driver, environment)
        self.add_device = AddDevicePage(driver, environment)

    def activate_and_return_home(self) -> None:
        """激活目标 App，等待 package 正确后恢复到设备首页。"""

        self.driver.activate_app(self.environment.app.package)
        WebDriverWait(self.driver, 20).until(
            lambda driver: driver.current_package == self.environment.app.package
        )
        self.home.return_to_home()

    def open_device_details(self) -> None:
        """在首页查找目标设备，进入并验证设备详情页。"""

        self.home.find_device().click()
        self.panel.assert_details()

    def open_device_settings(self) -> None:
        """从首页进入目标设备详情，再打开并验证高级设置页。"""

        self.open_device_details()
        self.panel.open_settings()
        self.settings.assert_loaded()

    def unbind_device(self) -> None:
        """解除目标设备绑定，并验证解绑后首页已不存在该设备。"""

        self.open_device_settings()
        self.settings.unbind()
        self.settings.wait_until_home(self.home.home_tab_selector)
        self.home.assert_device_absent()

    def open_add_device(self) -> None:
        """从首页进入添加设备页面并确认页面加载完成。"""

        self.home.open_add_device_page()
        self.add_device.wait_until_loaded()

    def submit_default_wifi(self) -> None:
        """选择自动发现的设备并提交 App 默认显示的 Wi-Fi 信息。"""

        self.add_device.continue_from_detected_device()
        self.add_device.submit_default_wifi()

    def wait_for_pairing_success(self, logger: logging.Logger) -> None:
        """等待配网成功、点击完成，并验证最终进入设备详情页。"""

        complete_button = self.add_device.wait_for_pairing_success(logger)
        complete_button.click()
        self.panel.assert_details()
