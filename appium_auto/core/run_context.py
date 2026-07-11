import logging
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator

from appium import webdriver


@dataclass
class RunContext:
    case_id: str
    run_dir: Path
    logger: logging.Logger

    @classmethod
    def create(cls, case_id: str) -> "RunContext":
        run_id = datetime.now().strftime(f"%Y%m%d_%H%M%S_%f_{case_id}")
        run_dir = Path("appium_auto/artifacts/runs") / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        logger = logging.getLogger(f"{case_id}.{run_id}")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        handler = logging.FileHandler(run_dir / "runtime.log", encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )
        logger.addHandler(handler)
        return cls(case_id=case_id, run_dir=run_dir, logger=logger)

    def save_evidence(self, driver: webdriver.Remote, name: str) -> None:
        driver.save_screenshot(str(self.run_dir / f"{name}.png"))
        (self.run_dir / f"{name}.xml").write_text(
            driver.page_source, encoding="utf-8"
        )

    def _save_failure(
        self,
        driver: webdriver.Remote,
        step: str,
        error: Exception,
        capture_ui: bool,
    ) -> None:
        if capture_ui:
            try:
                self.save_evidence(driver, "failure")
            except Exception as evidence_error:
                (self.run_dir / "evidence_error.txt").write_text(
                    str(evidence_error), encoding="utf-8"
                )

        context = [
            f"失败步骤: {step}",
            f"异常类型: {type(error).__name__}",
            f"异常信息: {error}",
            f"UI 证据已保存: {capture_ui}",
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
        (self.run_dir / "failure_context.txt").write_text(
            "\n".join(context), encoding="utf-8"
        )

    @contextmanager
    def step(
        self, driver: webdriver.Remote, name: str, capture_ui: bool = True
    ) -> Iterator[None]:
        self.logger.info("开始步骤：%s", name)
        try:
            yield
        except Exception as error:
            self.logger.exception("步骤失败：%s", name)
            self._save_failure(driver, name, error, capture_ui)
            raise
        self.logger.info("完成步骤：%s", name)
