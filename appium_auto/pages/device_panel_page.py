from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

from appium_auto.pages.base_page import BasePage


class DevicePanelPage(BasePage):
    """封装温湿度设备详情页的关键断言和设置入口。"""

    EDIT_BUTTON_XPATH = (
        '//android.view.ViewGroup[@content-desc="TopBar_Btn_Title"]'
        "/following-sibling::android.view.ViewGroup[1]"
    )

    def assert_details(self) -> None:
        """断言详情页同时显示目标设备名称、温度和湿度。"""

        self.wait_for_text(self.environment.iot_device.name)
        self.wait_for_text("温度")
        self.wait_for_text("湿度")

    def open_settings(self) -> None:
        """等待并点击设备详情页右上角的设置按钮。"""

        WebDriverWait(self.driver, 20).until(
            lambda driver: driver.find_element(
                AppiumBy.XPATH, self.EDIT_BUTTON_XPATH
            )
        ).click()
