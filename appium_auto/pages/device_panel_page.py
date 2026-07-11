from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

from appium_auto.pages.base_page import BasePage


class DevicePanelPage(BasePage):
    EDIT_BUTTON_XPATH = (
        '//android.view.ViewGroup[@content-desc="TopBar_Btn_Title"]'
        "/following-sibling::android.view.ViewGroup[1]"
    )

    def assert_details(self) -> None:
        self.wait_for_text(self.environment.iot_device.name)
        self.wait_for_text("温度")
        self.wait_for_text("湿度")

    def open_settings(self) -> None:
        WebDriverWait(self.driver, 20).until(
            lambda driver: driver.find_element(
                AppiumBy.XPATH, self.EDIT_BUTTON_XPATH
            )
        ).click()
