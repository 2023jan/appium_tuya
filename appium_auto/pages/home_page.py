from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait

from appium_auto.pages.base_page import BasePage


class HomePage(BasePage):
    """封装设备首页的定位、设备查找和添加设备入口。"""

    @property
    def home_menu_xpath(self) -> str:
        """返回首页右上角更多菜单按钮的 XPath。"""

        return (
            f'//*[@resource-id="{self.resource_id("toolbar_top_view")}"]'
            "//android.widget.ImageView[@clickable=\"true\"][last()]"
        )

    @property
    def home_tab_selector(self) -> str:
        """返回用于确认首页标签已选中的 UiAutomator2 selector。"""

        return (
            f'new UiSelector().resourceId("{self.resource_id("title")}")'
            '.text("首页").selected(true)'
        )

    @property
    def device_selector(self) -> str:
        """返回按环境设备名称定位设备卡片的 selector。"""

        device_name = self.environment.iot_device.name
        return (
            f'new UiSelector().resourceId("{self.resource_id("deviceName")}")'
            f'.text("{device_name}")'
        )

    @property
    def scroll_to_device_selector(self) -> str:
        """返回在设备列表中向下滚动查找目标设备的 selector。"""

        device_name = self.environment.iot_device.name
        return (
            'new UiScrollable(new UiSelector().className('
            '"androidx.recyclerview.widget.RecyclerView").scrollable(true))'
            ".setAsVerticalList().scrollIntoView(new UiSelector()"
            f'.resourceId("{self.resource_id("deviceName")}")'
            f'.text("{device_name}"))'
        )

    def wait_until_loaded(self, timeout: int = 20) -> None:
        """等待首页标签进入选中状态，确认设备列表已加载。"""

        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, self.home_tab_selector
            )
        )

    def return_to_home(self) -> None:
        """最多执行三次返回，将 App 内任意常见页面恢复到设备首页。"""

        # 智能生活部分页面第一次返回只关闭子页面或弹层，因此允许有限次重试。
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
        """存在“常用”标签时切换到该标签，统一后续设备查找范围。"""

        common_tabs = self.find_texts("常用")
        if common_tabs:
            common_tabs[0].click()

    def find_device(self):
        """先检查当前可见区域，再滚动设备列表并返回目标设备元素。"""

        self.select_common_devices()
        devices = self.driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR, self.device_selector
        )
        if devices:
            return devices[0]
        # 目标设备可能位于首屏以下，使用 UiScrollable 模拟人工向下查找。
        self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR, self.scroll_to_device_selector
        )
        return WebDriverWait(self.driver, 15).until(
            lambda driver: driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, self.device_selector
            )
        )

    def assert_device_absent(self) -> None:
        """检查当前区域和完整可滚动列表，断言目标设备确实不存在。"""

        self.select_common_devices()
        if self.driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR, self.device_selector
        ):
            raise AssertionError(
                f"首页仍然存在设备 {self.environment.iot_device.name}"
            )
        try:
            # 即使首屏没有目标，也要滚动完整列表，避免产生解绑成功的假阳性。
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, self.scroll_to_device_selector
            )
        except NoSuchElementException:
            # 列表已遍历且没有找到目标设备时，UiScrollable 会抛出该异常。
            pass
        if self.driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR, self.device_selector
        ):
            raise AssertionError(
                f"滚动首页后仍然存在设备 {self.environment.iot_device.name}"
            )

    def open_add_device_page(self) -> None:
        """打开右上角菜单并进入添加设备页，结束时恢复多窗口设置。"""

        # 系统弹层可能处于独立窗口，临时开启多窗口才能稳定定位菜单内容。
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
            # 无论菜单操作成功与否都恢复设置，避免影响后续页面定位。
            self.driver.update_settings({"enableMultiWindows": False})
