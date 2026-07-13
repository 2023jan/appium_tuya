from unittest.mock import MagicMock

from appium_auto.flows.device_lifecycle import DeviceLifecycleFlow


def _flow_without_driver_initialization() -> DeviceLifecycleFlow:
    """绕过真实 Driver 初始化，构造只包含 mock Page Object 的 Flow。"""

    flow = object.__new__(DeviceLifecycleFlow)
    flow.home = MagicMock()
    flow.panel = MagicMock()
    flow.settings = MagicMock()
    flow.add_device = MagicMock()
    return flow


def test_unbind_device_reuses_page_objects():
    """验证解绑流程按顺序复用设置页和首页对象完成状态检查。"""

    flow = _flow_without_driver_initialization()
    flow.open_device_settings = MagicMock()
    flow.home.home_tab_selector = "home-selector"
    flow.home.assert_device_absent = MagicMock()

    flow.unbind_device()

    flow.open_device_settings.assert_called_once_with()
    flow.settings.unbind.assert_called_once_with()
    flow.settings.wait_until_home.assert_called_once_with("home-selector")
    flow.home.assert_device_absent.assert_called_once_with()


def test_pairing_flow_keeps_adding_assertion_before_completion():
    """验证配网 Flow 先等待页面成功，再点击完成并断言设备详情。"""

    flow = _flow_without_driver_initialization()
    logger = MagicMock()
    complete_button = MagicMock()
    flow.add_device.wait_for_pairing_success.return_value = complete_button
    flow.panel.assert_details = MagicMock()

    flow.wait_for_pairing_success(logger)

    flow.add_device.wait_for_pairing_success.assert_called_once_with(logger)
    complete_button.click.assert_called_once_with()
    flow.panel.assert_details.assert_called_once_with()
