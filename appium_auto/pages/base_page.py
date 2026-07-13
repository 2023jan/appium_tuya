from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

from appium_auto.core.environment import EnvironmentConfig


class BasePage:
    """提供所有页面对象共用的定位、显式等待和返回能力。"""

    def __init__(
        self, driver: webdriver.Remote, environment: EnvironmentConfig
    ) -> None:
        """保存 Appium Driver 和当前运行环境，供具体页面对象复用。"""

        self.driver = driver
        self.environment = environment

    def resource_id(self, name: str) -> str:
        """使用环境中的 App package 拼接完整 Android resource-id。"""

        return f"{self.environment.app.package}:id/{name}"

    @staticmethod
    def text_selector(text: str) -> str:
        """生成按完整文本匹配的 UiAutomator2 selector。"""

        return f'new UiSelector().text("{text}")'

    def wait_for_text(self, text: str, timeout: int = 20):
        """显式等待指定文本元素出现并返回元素对象。"""

        return WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, self.text_selector(text)
            )
        )

    def find_texts(self, text: str):
        """立即查找所有匹配文本的元素，不因元素不存在而抛出异常。"""

        return self.driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR, self.text_selector(text)
        )

    def back(self) -> None:
        """执行一次 Android 系统返回操作。"""

        self.driver.back()
