import pytest

from appium_auto.core.environment import EnvironmentConfig
from appium_auto.core.run_context import RunContext
from appium_auto.flows.device_lifecycle import DeviceLifecycleFlow


@pytest.mark.case_id("CASE00")
def test_case00_enter_device_details_and_view_information(
    driver,
    environment: EnvironmentConfig,
    run_context: RunContext,
):
    flow = DeviceLifecycleFlow(driver, environment)
    run_context.logger.info(
        "开始执行 CASE00，目标设备=%s", environment.iot_device.name
    )

    with run_context.step(driver, "启动 App 并恢复到设备列表首页"):
        flow.activate_and_return_home()

    with run_context.step(driver, "滚动查找并打开目标设备"):
        flow.open_device_details()
        run_context.save_evidence(driver, "device_details")

    with run_context.step(driver, "打开高级设置并验证移除设备按钮"):
        flow.panel.open_settings()
        flow.settings.assert_loaded()
        run_context.save_evidence(driver, "advanced_settings")

    with run_context.step(driver, "返回设备详情页"):
        flow.settings.back()
        flow.panel.assert_details()

    with run_context.step(driver, "返回首页并确认目标设备仍存在"):
        flow.panel.back()
        flow.home.find_device()
        run_context.save_evidence(driver, "final_home")

    run_context.logger.info("CASE00 执行成功，设备和账号状态未被修改")
