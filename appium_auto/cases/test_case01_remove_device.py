import os

import pytest

from appium_auto.core.environment import EnvironmentConfig
from appium_auto.core.run_context import RunContext
from appium_auto.flows.device_lifecycle import DeviceLifecycleFlow


@pytest.mark.case_id("CASE01")
@pytest.mark.destructive
@pytest.mark.skipif(
    os.getenv("RUN_DESTRUCTIVE_CASE01") != "1",
    reason="CASE01 会解除设备绑定；设置 RUN_DESTRUCTIVE_CASE01=1 后才允许执行",
)
def test_case01_remove_device_successfully(
    driver,
    environment: EnvironmentConfig,
    run_context: RunContext,
):
    flow = DeviceLifecycleFlow(driver, environment)
    run_context.logger.info(
        "开始执行 CASE01，目标设备=%s", environment.iot_device.name
    )

    with run_context.step(driver, "启动 App 并恢复到设备列表首页"):
        flow.activate_and_return_home()

    with run_context.step(driver, "解除绑定并验证首页不存在目标设备"):
        flow.unbind_device()
        run_context.save_evidence(driver, "final_home_without_device")

    run_context.logger.info(
        "CASE01 执行成功，设备 %s 已解除绑定", environment.iot_device.name
    )
