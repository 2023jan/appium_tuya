import logging
import os
from datetime import datetime
from pathlib import Path

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait


APP_PACKAGE = "com.tuya.smartlifeiot"
DEVICE_NAME = "V4#4"
DEFAULT_UDID = "ff73089e"

DEVICE_SELECTOR = (
    'new UiSelector().resourceId("com.tuya.smartlifeiot:id/deviceName")'
    '.text("V4#4")'
)
SCROLL_TO_DEVICE_SELECTOR = (
    'new UiScrollable(new UiSelector().className("androidx.recyclerview.widget.RecyclerView")'
    ".scrollable(true)).setAsVerticalList()"
    '.scrollIntoView(new UiSelector()'
    '.resourceId("com.tuya.smartlifeiot:id/deviceName").text("V4#4"))'
)
EDIT_BUTTON_XPATH = (
    '//android.view.ViewGroup[@content-desc="TopBar_Btn_Title"]'
    "/following-sibling::android.view.ViewGroup[1]"
)
HOME_TAB_SELECTOR = (
    'new UiSelector().resourceId("com.tuya.smartlifeiot:id/title")'
    '.text("首页").selected(true)'
)


def _create_run_dir() -> Path:
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_CASE01")
    run_dir = Path("appium_auto/artifacts/runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _configure_logger(run_dir: Path) -> logging.Logger:
    logger = logging.getLogger(f"CASE01.{run_dir.name}")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(run_dir / "runtime.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


def _text_selector(text: str) -> str:
    return f'new UiSelector().text("{text}")'


def _wait_for_text(driver: webdriver.Remote, text: str, timeout: int = 20):
    return WebDriverWait(driver, timeout).until(
        lambda current_driver: current_driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR, _text_selector(text)
        )
    )


def _find_device(driver: webdriver.Remote):
    _select_common_devices(driver)
    devices = driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, DEVICE_SELECTOR)
    if devices:
        return devices[0]

    driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, SCROLL_TO_DEVICE_SELECTOR)
    return WebDriverWait(driver, 15).until(
        lambda current_driver: current_driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR, DEVICE_SELECTOR
        )
    )


def _select_common_devices(driver: webdriver.Remote) -> None:
    common_tabs = driver.find_elements(
        AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("常用")'
    )
    if common_tabs:
        common_tabs[0].click()


def _return_to_home(driver: webdriver.Remote) -> None:
    for _ in range(3):
        if driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, HOME_TAB_SELECTOR):
            return
        driver.back()
        WebDriverWait(driver, 8).until(
            lambda current_driver: current_driver.current_package == APP_PACKAGE
        )
    raise AssertionError("连续返回后仍未进入智能生活 App 首页")


def _assert_device_absent(driver: webdriver.Remote) -> None:
    _select_common_devices(driver)
    if driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, DEVICE_SELECTOR):
        raise AssertionError(f"首页仍然存在设备 {DEVICE_NAME}")

    try:
        driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR, SCROLL_TO_DEVICE_SELECTOR
        )
    except NoSuchElementException:
        pass

    if driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, DEVICE_SELECTOR):
        raise AssertionError(f"滚动首页后仍然存在设备 {DEVICE_NAME}")


def _save_evidence(driver: webdriver.Remote, run_dir: Path, name: str) -> None:
    driver.save_screenshot(str(run_dir / f"{name}.png"))
    (run_dir / f"{name}.xml").write_text(driver.page_source, encoding="utf-8")


def _save_failure_context(
    driver: webdriver.Remote, run_dir: Path, step: str, error: Exception
) -> None:
    try:
        _save_evidence(driver, run_dir, "failure")
    except Exception as evidence_error:
        (run_dir / "evidence_error.txt").write_text(
            str(evidence_error), encoding="utf-8"
        )

    context = [
        f"失败步骤: {step}",
        f"异常类型: {type(error).__name__}",
        f"异常信息: {error}",
    ]
    try:
        context.extend(
            [
                f"当前 package: {driver.current_package}",
                f"当前 activity: {driver.current_activity}",
            ]
        )
    except Exception as context_error:
        context.append(f"读取当前页面上下文失败: {context_error}")
    (run_dir / "failure_context.txt").write_text(
        "\n".join(context), encoding="utf-8"
    )


@pytest.fixture
def driver(appium_server_url):
    options = UiAutomator2Options()
    options.load_capabilities(
        {
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:udid": os.getenv("APPIUM_UDID", DEFAULT_UDID),
            "appium:noReset": True,
            "appium:fullReset": False,
            "appium:newCommandTimeout": 600,
            "appium:skipDeviceInitialization": True,
            "appium:skipServerInstallation": True,
            "appium:disableWindowAnimation": False,
        }
    )
    appium_driver = webdriver.Remote(appium_server_url, options=options)
    yield appium_driver
    appium_driver.quit()


@pytest.mark.destructive
@pytest.mark.skipif(
    os.getenv("RUN_DESTRUCTIVE_CASE01") != "1",
    reason="CASE01 会解除设备绑定；设置 RUN_DESTRUCTIVE_CASE01=1 后才允许执行",
)
def test_case01_remove_device_successfully(driver):
    run_dir = _create_run_dir()
    logger = _configure_logger(run_dir)
    step = "启动 TEST-智能生活"

    try:
        logger.info("开始执行 CASE01，目标设备=%s", DEVICE_NAME)
        driver.activate_app(APP_PACKAGE)
        WebDriverWait(driver, 20).until(
            lambda current_driver: current_driver.current_package == APP_PACKAGE
        )

        step = "恢复到设备列表首页"
        _return_to_home(driver)

        step = "滚动查找并打开 V4#4"
        _find_device(driver).click()

        step = "验证设备详情页"
        _wait_for_text(driver, DEVICE_NAME)
        _wait_for_text(driver, "温度")
        _wait_for_text(driver, "湿度")

        step = "打开高级设置页"
        WebDriverWait(driver, 20).until(
            lambda current_driver: current_driver.find_element(
                AppiumBy.XPATH, EDIT_BUTTON_XPATH
            )
        ).click()

        step = "打开移除设备抽屉"
        _wait_for_text(driver, "移除设备").click()
        _wait_for_text(driver, "解除绑定")
        _wait_for_text(driver, "解绑并清除数据")
        _save_evidence(driver, run_dir, "remove_device_options")

        step = "选择解除绑定"
        _wait_for_text(driver, "解除绑定").click()
        _wait_for_text(driver, "确定要解绑设备吗？")
        _save_evidence(driver, run_dir, "unbind_confirmation")

        step = "确认解除绑定"
        _wait_for_text(driver, "确定").click()
        WebDriverWait(driver, 30).until(
            lambda current_driver: current_driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, HOME_TAB_SELECTOR
            )
        )

        step = "验证首页不存在 V4#4"
        _assert_device_absent(driver)
        _save_evidence(driver, run_dir, "final_home_without_device")

        logger.info("CASE01 执行成功，设备 %s 已解除绑定", DEVICE_NAME)
    except Exception as error:
        logger.exception("CASE01 执行失败，失败步骤=%s", step)
        _save_failure_context(driver, run_dir, step, error)
        raise
