from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

from appium_auto.core.environment import EnvironmentConfig


class BasePage:
    def __init__(
        self, driver: webdriver.Remote, environment: EnvironmentConfig
    ) -> None:
        self.driver = driver
        self.environment = environment

    def resource_id(self, name: str) -> str:
        return f"{self.environment.app.package}:id/{name}"

    @staticmethod
    def text_selector(text: str) -> str:
        return f'new UiSelector().text("{text}")'

    def wait_for_text(self, text: str, timeout: int = 20):
        return WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, self.text_selector(text)
            )
        )

    def find_texts(self, text: str):
        return self.driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR, self.text_selector(text)
        )

    def back(self) -> None:
        self.driver.back()
