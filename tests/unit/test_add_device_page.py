from unittest.mock import MagicMock, call

from appium_auto.pages.add_device_page import AddDevicePage
from tests.unit.test_home_page import _environment


def test_pairing_success_strictly_waits_for_adding_before_success():
    """验证配网页严格先断言“正在添加”，再等待“添加成功”。"""

    driver = MagicMock()
    success_view = MagicMock()
    complete_button = MagicMock()
    driver.find_element.side_effect = [success_view, complete_button]
    page = AddDevicePage(driver, _environment())
    page.wait_for_text = MagicMock()
    logger = MagicMock()

    result = page.wait_for_pairing_success(logger)

    assert page.wait_for_text.mock_calls == [
        call("正在添加", timeout=30),
        call("添加成功", timeout=170),
        call("sensor", timeout=20),
    ]
    assert result is complete_button
    logger.info.assert_called_once_with("已确认配网页面显示正在添加")
