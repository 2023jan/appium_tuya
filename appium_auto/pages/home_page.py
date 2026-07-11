from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait

from appium_auto.pages.base_page import BasePage


class HomePage(BasePage):
    @property
    def home_menu_xpath(self) -> str:
        return (
            f'//*[@resource-id="{self.resource_id("toolbar_top_view")}"]'
            "//android.widget.ImageView[@clickable=\"true\"][last()]"
        )

    @property
    def home_tab_selector(self) -> str:
        return (
            f'new UiSelector().resourceId("{self.resource_id("title")}")'
            '.text("首页").selected(true)'
        )

    @property
    def device_selector(self) -> str:
        device_name = self.environment.iot_device.name
        return (
            f'new UiSelector().resourceId("{self.resource_id("deviceName")}")'
            f'.text("{device_name}")'
        )

    @property
    def scroll_to_device_selector(self) -> str:
        device_name = self.environment.iot_device.name
        return (
            'new UiScrollable(new UiSelector().className('
            '"androidx.recyclerview.widget.RecyclerView").scrollable(true))'
            ".setAsVerticalList().scrollIntoView(new UiSelector()"
            f'.resourceId("{self.resource_id("deviceName")}")'
            f'.text("{device_name}"))'
        )

    def wait_until_loaded(self, timeout: int = 20) -> None:
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, self.home_tab_selector
            )
        )

    def return_to_home(self) -> None:
        for _ in range(3):
            if self.driver.find_elements(
                AppiumBy.ANDROID_UIAUTOMATOR, self.home_tab_selector
            ):
                return
            self.driver.back()
            WebDriverWait(self.driver, 8).until(
                lambda driver: driver.current_package
                == self.environment.app.package
            )
        if self.driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR, self.home_tab_selector
        ):
            return
        raise AssertionError("连续返回后仍未进入智能生活 App 首页")

    def select_common_devices(self) -> None:
        common_tabs = self.find_texts("常用")
        if common_tabs:
            common_tabs[0].click()

    def find_device(self):
        self.select_common_devices()
        devices = self.driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR, self.device_selector
        )
        if devices:
            return devices[0]
        self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR, self.scroll_to_device_selector
        )
        return WebDriverWait(self.driver, 15).until(
            lambda driver: driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, self.device_selector
            )
        )

    def assert_device_absent(self) -> None:
        self.select_common_devices()
        if self.driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR, self.device_selector
        ):
            raise AssertionError(
                f"首页仍然存在设备 {self.environment.iot_device.name}"
            )
        try:
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, self.scroll_to_device_selector
            )
        except NoSuchElementException:
            pass
        if self.driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR, self.device_selector
        ):
            raise AssertionError(
                f"滚动首页后仍然存在设备 {self.environment.iot_device.name}"
            )

    def open_add_device_page(self) -> None:
        self.driver.update_settings({"enableMultiWindows": True})
        try:
            WebDriverWait(self.driver, 15).until(
                lambda driver: driver.find_element(
                    AppiumBy.XPATH, self.home_menu_xpath
                )
            ).click()
            add_device = WebDriverWait(self.driver, 10).until(
                lambda driver: driver.find_element(
                    AppiumBy.ID, self.resource_id("tv_option")
                )
            )
            if add_device.text != "添加设备":
                raise AssertionError(
                    f"右上角菜单第一个选项不是添加设备：{add_device.text}"
                )
            add_device.click()
        finally:
            self.driver.update_settings({"enableMultiWindows": False})
