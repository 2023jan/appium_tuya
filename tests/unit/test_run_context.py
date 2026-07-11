from unittest.mock import MagicMock

import pytest

from appium_auto.core.run_context import RunContext


def test_sensitive_step_does_not_save_screenshot_or_page_source(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    driver = MagicMock()
    driver.current_package = "test.app"
    driver.current_activity = "SensitiveActivity"
    context = RunContext.create("CASE_TEST")

    with pytest.raises(RuntimeError, match="sensitive failure"):
        with context.step(driver, "Wi-Fi 信息", capture_ui=False):
            raise RuntimeError("sensitive failure")

    assert not (context.run_dir / "failure.png").exists()
    assert not (context.run_dir / "failure.xml").exists()
    failure_context = (context.run_dir / "failure_context.txt").read_text(
        encoding="utf-8"
    )
    assert "UI 证据已保存: False" in failure_context
    driver.save_screenshot.assert_not_called()
