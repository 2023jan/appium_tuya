from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

from appium_auto.pages.base_page import BasePage


class DeviceSettingsPage(BasePage):
    """封装设备高级设置页及解除绑定确认流程。"""

    def assert_loaded(self) -> None:
        """通过“移除设备”入口确认高级设置页已经加载。"""

        self.wait_for_text("移除设备")

    def unbind(self) -> None:
        """依次完成移除设备、解除绑定和最终确认操作。"""

        # 解绑会改变账号与设备状态，必须完整验证两层确认文案后再点击。
        self.wait_for_text("移除设备").click()
        self.wait_for_text("解除绑定")
        self.wait_for_text("解绑并清除数据")
        self.wait_for_text("解除绑定").click()
        self.wait_for_text("确定要解绑设备吗？")
        self.wait_for_text("确定").click()

    def wait_until_home(self, home_tab_selector: str) -> None:
        """等待解绑完成后 App 自动返回设备首页。"""

        WebDriverWait(self.driver, 30).until(
            lambda driver: driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, home_tab_selector
            )
        )
