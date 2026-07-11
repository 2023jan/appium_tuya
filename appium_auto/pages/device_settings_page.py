from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

from appium_auto.pages.base_page import BasePage


class DeviceSettingsPage(BasePage):
    def assert_loaded(self) -> None:
        self.wait_for_text("移除设备")

    def unbind(self) -> None:
        self.wait_for_text("移除设备").click()
        self.wait_for_text("解除绑定")
        self.wait_for_text("解绑并清除数据")
        self.wait_for_text("解除绑定").click()
        self.wait_for_text("确定要解绑设备吗？")
        self.wait_for_text("确定").click()

    def wait_until_home(self, home_tab_selector: str) -> None:
        WebDriverWait(self.driver, 30).until(
            lambda driver: driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, home_tab_selector
            )
        )
