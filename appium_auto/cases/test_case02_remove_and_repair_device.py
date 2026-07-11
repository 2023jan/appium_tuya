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
DEVICE_TYPE = "Wi-Fi温湿度传感器"
DEFAULT_UDID = "ff73089e"
PAIRING_TIMEOUT = 170

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
HOME_MENU_XPATH = (
    '//*[@resource-id="com.tuya.smartlifeiot:id/toolbar_top_view"]'
    "//android.widget.ImageView[@clickable=\"true\"][last()]"
)


def _create_run_dir() -> Path:
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_CASE02")
    run_dir = Path("appium_auto/artifacts/runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _configure_logger(run_dir: Path) -> logging.Logger:
    logger = logging.getLogger(f"CASE02.{run_dir.name}")
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


def _select_common_devices(driver: webdriver.Remote) -> None:
    common_tabs = driver.find_elements(
        AppiumBy.ANDROID_UIAUTOMATOR, _text_selector("常用")
    )
    if common_tabs:
        common_tabs[0].click()


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


def _open_add_device_page(driver: webdriver.Remote) -> None:
    driver.update_settings({"enableMultiWindows": True})
    try:
        WebDriverWait(driver, 15).until(
            lambda current_driver: current_driver.find_element(
                AppiumBy.XPATH, HOME_MENU_XPATH
            )
        ).click()
        add_device = WebDriverWait(driver, 10).until(
            lambda current_driver: current_driver.find_element(
                AppiumBy.ID, f"{APP_PACKAGE}:id/tv_option"
            )
        )
        if add_device.text != "添加设备":
            raise AssertionError(f"右上角菜单第一个选项不是添加设备：{add_device.text}")
        add_device.click()
    finally:
        driver.update_settings({"enableMultiWindows": False})

    _wait_for_text(driver, "添加设备", timeout=20)


def _continue_from_detected_device(driver: webdriver.Remote) -> None:
    detected_state = WebDriverWait(driver, 40).until(
        lambda current_driver: (
            "wifi"
            if current_driver.find_elements(
                AppiumBy.ANDROID_UIAUTOMATOR, _text_selector("请输入Wi-Fi信息")
            )
            else (
                "device"
                if current_driver.find_elements(
                    AppiumBy.ANDROID_UIAUTOMATOR, _text_selector(DEVICE_TYPE)
                )
                else False
            )
        )
    )
    if detected_state == "device":
        _wait_for_text(driver, DEVICE_TYPE).click()
        _wait_for_text(driver, "请输入Wi-Fi信息", timeout=15)


def _wait_for_pairing_result(driver: webdriver.Remote, logger: logging.Logger):
    _wait_for_text(driver, "正在添加", timeout=30)
    logger.info("已确认配网页面显示正在添加")
    _wait_for_text(driver, "添加成功", timeout=PAIRING_TIMEOUT)
    _wait_for_text(driver, DEVICE_NAME, timeout=20)
    WebDriverWait(driver, 20).until(
        lambda current_driver: current_driver.find_element(
            AppiumBy.ID, f"{APP_PACKAGE}:id/successView"
        )
    )
    return WebDriverWait(driver, 20).until(
        lambda current_driver: current_driver.find_element(
            AppiumBy.ID, f"{APP_PACKAGE}:id/btnDone"
        )
    )


def _save_evidence(driver: webdriver.Remote, run_dir: Path, name: str) -> None:
    driver.save_screenshot(str(run_dir / f"{name}.png"))
    (run_dir / f"{name}.xml").write_text(driver.page_source, encoding="utf-8")


def _save_failure_context(
    driver: webdriver.Remote,
    run_dir: Path,
    step: str,
    error: Exception,
    allow_ui_evidence: bool,
) -> None:
    if allow_ui_evidence:
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
        f"UI 证据已保存: {allow_ui_evidence}",
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
    os.getenv("RUN_DESTRUCTIVE_CASE02") != "1",
    reason="CASE02 会先解绑设备；设置 RUN_DESTRUCTIVE_CASE02=1 后才允许执行",
)
def test_case02_remove_and_repair_device_successfully(driver):
    run_dir = _create_run_dir()
    logger = _configure_logger(run_dir)
    step = "启动 TEST-智能生活"
    sensitive_page = False

    try:
        logger.info("开始执行 CASE02，目标设备=%s", DEVICE_NAME)
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

        step = "选择解除绑定"
        _wait_for_text(driver, "解除绑定").click()
        _wait_for_text(driver, "确定要解绑设备吗？")

        step = "确认解除绑定"
        _wait_for_text(driver, "确定").click()
        WebDriverWait(driver, 30).until(
            lambda current_driver: current_driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, HOME_TAB_SELECTOR
            )
        )

        step = "验证首页不存在 V4#4"
        _assert_device_absent(driver)

        step = "进入添加设备页"
        _open_add_device_page(driver)

        step = "等待设备发现并验证 Wi-Fi 信息"
        sensitive_page = True
        _continue_from_detected_device(driver)
        WebDriverWait(driver, 15).until(
            lambda current_driver: current_driver.find_element(
                AppiumBy.ID, f"{APP_PACKAGE}:id/tvConfirm"
            )
        ).click()
        WebDriverWait(driver, 20).until(
            lambda current_driver: current_driver.current_activity
            != "com.thingclips.smart.activator.input.wifi.InputWifiActivity"
        )
        sensitive_page = False

        step = "验证正在添加状态"
        complete_button = _wait_for_pairing_result(driver, logger)
        _save_evidence(driver, run_dir, "pairing_success")

        step = "完成配网并验证设备详情页"
        complete_button.click()
        _wait_for_text(driver, DEVICE_NAME, timeout=40)
        _wait_for_text(driver, "温度", timeout=30)
        _wait_for_text(driver, "湿度", timeout=30)
        _save_evidence(driver, run_dir, "final_device_details")

        logger.info("CASE02 执行成功，设备 %s 已删除并重新配网", DEVICE_NAME)
    except Exception as error:
        logger.exception("CASE02 执行失败，失败步骤=%s", step)
        _save_failure_context(
            driver,
            run_dir,
            step,
            error,
            allow_ui_evidence=not sensitive_page,
        )
        raise
