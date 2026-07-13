import logging

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

from appium_auto.pages.base_page import BasePage


class AddDevicePage(BasePage):
    """封装自动发现设备、默认 Wi-Fi 提交和配网结果确认。"""

    WIFI_ACTIVITY = "com.thingclips.smart.activator.input.wifi.InputWifiActivity"

    def wait_until_loaded(self) -> None:
        """等待添加设备页面标题出现。"""

        self.wait_for_text("添加设备", timeout=20)

    def continue_from_detected_device(self) -> None:
        """兼容发现页或已进入 Wi-Fi 页两种状态，并推进到 Wi-Fi 信息页。"""

        device_type = self.environment.iot_device.type
        # 自动发现速度不固定：可能先看到设备卡片，也可能直接跳到 Wi-Fi 页面。
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
        """提交 App 已填充的默认 Wi-Fi 信息，并等待离开敏感信息页面。"""

        WebDriverWait(self.driver, 15).until(
            lambda driver: driver.find_element(
                AppiumBy.ID, self.resource_id("tvConfirm")
            )
        ).click()
        WebDriverWait(self.driver, 20).until(
            lambda driver: driver.current_activity != self.WIFI_ACTIVITY
        )

    def wait_for_pairing_success(self, logger: logging.Logger):
        """严格确认“正在添加”后等待成功状态，并返回完成按钮。"""

        # 不允许直接从“添加成功”继续，否则无法证明配网过程状态被正确展示。
        self.wait_for_text("正在添加", timeout=30)
        logger.info("已确认配网页面显示正在添加")
        self.wait_for_text("添加成功", timeout=170)
        self.wait_for_text(self.environment.iot_device.name, timeout=20)
        # successView 是绿色成功标识的稳定 resource-id，用来补强纯文本断言。
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
