import logging

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

from appium_auto.pages.base_page import BasePage


class AddDevicePage(BasePage):
    WIFI_ACTIVITY = "com.thingclips.smart.activator.input.wifi.InputWifiActivity"

    def wait_until_loaded(self) -> None:
        self.wait_for_text("添加设备", timeout=20)

    def continue_from_detected_device(self) -> None:
        device_type = self.environment.iot_device.type
        detected_state = WebDriverWait(self.driver, 40).until(
            lambda driver: (
                "wifi"
                if driver.find_elements(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    self.text_selector("请输入Wi-Fi信息"),
                )
                else (
                    "device"
                    if driver.find_elements(
                        AppiumBy.ANDROID_UIAUTOMATOR,
                        self.text_selector(device_type),
                    )
                    else False
                )
            )
        )
        if detected_state == "device":
            self.wait_for_text(device_type).click()
            self.wait_for_text("请输入Wi-Fi信息", timeout=15)

    def submit_default_wifi(self) -> None:
        WebDriverWait(self.driver, 15).until(
            lambda driver: driver.find_element(
                AppiumBy.ID, self.resource_id("tvConfirm")
            )
        ).click()
        WebDriverWait(self.driver, 20).until(
            lambda driver: driver.current_activity != self.WIFI_ACTIVITY
        )

    def wait_for_pairing_success(self, logger: logging.Logger):
        self.wait_for_text("正在添加", timeout=30)
        logger.info("已确认配网页面显示正在添加")
        self.wait_for_text("添加成功", timeout=170)
        self.wait_for_text(self.environment.iot_device.name, timeout=20)
        WebDriverWait(self.driver, 20).until(
            lambda driver: driver.find_element(
                AppiumBy.ID, self.resource_id("successView")
            )
        )
        return WebDriverWait(self.driver, 20).until(
            lambda driver: driver.find_element(
                AppiumBy.ID, self.resource_id("btnDone")
            )
        )
