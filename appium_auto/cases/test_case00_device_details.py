import logging
import os
from datetime import datetime
from pathlib import Path

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait


APP_PACKAGE = "com.tuya.smartlifeiot"
APP_ACTIVITY = "com.smart.ThingSplashActivity"
DEVICE_NAME = "V4#4"
DEVICE_NAME_ID = f"{APP_PACKAGE}:id/deviceName"
DEFAULT_UDID = "ff73089e"

DEVICE_SELECTOR = (
    'new UiSelector().resourceId("com.tuya.smartlifeiot:id/deviceName")'
    '.text("V4#4")'
)
SCROLL_TO_DEVICE_SELECTOR = (
    "new UiScrollable(new UiSelector().scrollable(true)).setAsVerticalList()"
    '.scrollIntoView(new UiSelector()'
    '.resourceId("com.tuya.smartlifeiot:id/deviceName").text("V4#4"))'
)
EDIT_BUTTON_XPATH = (
    '//android.view.ViewGroup[@content-desc="TopBar_Btn_Title"]'
    "/following-sibling::android.view.ViewGroup[1]"
)


def _create_run_dir() -> Path:
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_CASE00")
    run_dir = Path("appium_auto/artifacts/runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _configure_logger(run_dir: Path) -> logging.Logger:
    logger = logging.getLogger(f"CASE00.{run_dir.name}")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(run_dir / "runtime.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


def _wait_for_text(driver: webdriver.Remote, text: str, timeout: int = 20):
    selector = f'new UiSelector().text("{text}")'
    return WebDriverWait(driver, timeout).until(
        lambda current_driver: current_driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR, selector
        )
    )


def _find_device(driver: webdriver.Remote):
    devices = driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, DEVICE_SELECTOR)
    if devices:
        return devices[0]

    driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, SCROLL_TO_DEVICE_SELECTOR)
    return WebDriverWait(driver, 15).until(
        lambda current_driver: current_driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR, DEVICE_SELECTOR
        )
    )


def _return_to_home(driver: webdriver.Remote) -> None:
    for _ in range(3):
        if driver.find_elements(AppiumBy.ID, DEVICE_NAME_ID):
            return
        driver.back()
        WebDriverWait(driver, 8).until(
            lambda current_driver: current_driver.current_package == APP_PACKAGE
        )
    raise AssertionError("连续返回后仍未进入智能生活 App 首页")


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


def test_case00_enter_device_details_and_view_information(driver):
    run_dir = _create_run_dir()
    logger = _configure_logger(run_dir)
    step = "启动 TEST-智能生活"

    try:
        logger.info("开始执行 CASE00，目标设备=%s", DEVICE_NAME)
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
        _save_evidence(driver, run_dir, "device_details")

        step = "打开高级设置页"
        WebDriverWait(driver, 20).until(
            lambda current_driver: current_driver.find_element(
                AppiumBy.XPATH, EDIT_BUTTON_XPATH
            )
        ).click()

        step = "验证移除设备按钮"
        _wait_for_text(driver, "移除设备")
        _save_evidence(driver, run_dir, "advanced_settings")

        step = "返回设备详情页"
        driver.back()
        _wait_for_text(driver, DEVICE_NAME)
        _wait_for_text(driver, "温度")
        _wait_for_text(driver, "湿度")

        step = "返回首页并确认 V4#4 仍存在"
        driver.back()
        _find_device(driver)
        _save_evidence(driver, run_dir, "final_home")

        logger.info("CASE00 执行成功，设备和账号状态未被修改")
    except Exception as error:
        logger.exception("CASE00 执行失败，失败步骤=%s", step)
        _save_failure_context(driver, run_dir, step, error)
        raise
