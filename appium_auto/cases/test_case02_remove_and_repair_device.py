import os

import pytest

from appium_auto.core.environment import EnvironmentConfig
from appium_auto.core.run_context import RunContext
from appium_auto.flows.device_lifecycle import DeviceLifecycleFlow


@pytest.mark.case_id("CASE02")
@pytest.mark.stateful
@pytest.mark.skipif(
    os.getenv("RUN_STATEFUL_CASE02") != "1",
    reason="CASE02 会先解绑再配网；设置 RUN_STATEFUL_CASE02=1 后才允许执行",
)
def test_case02_remove_and_repair_device_successfully(
    driver,
    environment: EnvironmentConfig,
    run_context: RunContext,
):
    """验证设备解绑后能在配网窗口内重新添加并恢复在线详情状态。"""

    flow = DeviceLifecycleFlow(driver, environment)
    run_context.logger.info(
        "开始执行 CASE02，目标设备=%s", environment.iot_device.name
    )

    with run_context.step(driver, "启动 App 并恢复到设备列表首页"):
        flow.activate_and_return_home()

    with run_context.step(driver, "解除绑定并验证首页不存在目标设备"):
        flow.unbind_device()

    with run_context.step(
        driver,
        "自动发现设备并使用 App 默认 Wi-Fi 信息",
        capture_ui=False,
    ):
        # Wi-Fi 页面可能显示密码，关闭 UI 证据采集以避免敏感信息落盘。
        flow.open_add_device()
        flow.submit_default_wifi()

    with run_context.step(driver, "验证正在添加并等待配网成功"):
        # 必须先观察到“正在添加”，不能因发现成功状态而跳过过程断言。
        flow.wait_for_pairing_success(run_context.logger)
        run_context.save_evidence(driver, "final_device_details")

    run_context.logger.info(
        "CASE02 执行成功，设备 %s 已删除并重新配网",
        environment.iot_device.name,
    )
