import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

import pytest

from appium_auto.core.driver_factory import create_android_driver
from appium_auto.core.environment import EnvironmentConfig, load_environment
from appium_auto.core.run_context import RunContext


DEFAULT_SERVER_URL = "http://127.0.0.1:4723"
DEFAULT_START_TIMEOUT = 30.0


def _server_is_ready(server_url: str) -> bool:
    """调用 Appium 状态接口，判断 Server 是否已经可以建立 Session。"""

    try:
        with urlopen(f"{server_url.rstrip('/')}/status", timeout=2) as response:
            payload = json.load(response)
        return bool(payload.get("value", {}).get("ready"))
    except (OSError, TimeoutError, ValueError):
        return False


def _resolve_appium_command() -> list[str]:
    """解析当前平台可执行的 Appium 启动命令，并在缺失依赖时终止测试。"""

    appium_executable = shutil.which("appium.cmd") or shutil.which("appium")
    if not appium_executable:
        pytest.fail("未在 PATH 中找到 Appium，请先执行 npm install -g appium。")

    if os.name != "nt":
        return [appium_executable]

    # Windows 的 appium.cmd 不便直接作为无窗口子进程管理，改用 Node.js 入口。
    node_executable = shutil.which("node")
    appium_entry = Path(appium_executable).parent / "node_modules" / "appium" / "index.js"
    if not node_executable or not appium_entry.is_file():
        pytest.fail(
            "已找到 appium.cmd，但无法定位 Node.js 或 Appium 入口文件，请检查全局 Appium 安装。"
        )
    return [node_executable, str(appium_entry)]


def _stop_process(process: subprocess.Popen) -> None:
    """先温和终止 fixture 启动的进程，超时后再强制结束。"""

    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def _log_tail(log_path: Path, line_count: int = 40) -> str:
    """读取 Appium 日志末尾片段，用于启动失败提示。"""

    if not log_path.is_file():
        return "Appium Server 未生成日志。"
    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-line_count:])


@pytest.fixture(scope="session")
def appium_server_url() -> str:
    """复用现有 Appium Server，或为本次 pytest 会话启动并关闭本机服务。"""

    server_url = os.getenv("APPIUM_SERVER_URL", DEFAULT_SERVER_URL).rstrip("/")
    if _server_is_ready(server_url):
        # 外部已启动的 Server 不归本 fixture 所有，测试结束时不能关闭它。
        yield server_url
        return

    parsed_url = urlparse(server_url)
    if parsed_url.hostname not in {"127.0.0.1", "localhost", "::1"}:
        # 自动管理仅限本机进程，避免误启动或误关闭远程共享服务。
        pytest.fail(
            f"远程 Appium Server 不可用：{server_url}。项目 fixture 只自动启动本机服务。"
        )

    host = parsed_url.hostname or "127.0.0.1"
    port = parsed_url.port or 4723
    log_path = Path(__file__).parent / "logs" / "appium_server.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    command = _resolve_appium_command() + [
        "--address",
        host,
        "--port",
        str(port),
        "--log",
        str(log_path),
        "--log-timestamp",
    ]
    creation_flags = 0
    if os.name == "nt":
        # 后台运行时不弹出额外控制台窗口，同时保留独立进程组便于清理。
        creation_flags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP

    process = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        creationflags=creation_flags,
    )
    timeout = float(os.getenv("APPIUM_SERVER_START_TIMEOUT", DEFAULT_START_TIMEOUT))
    deadline = time.monotonic() + timeout
    # 轮询状态接口而不是固定 sleep，使启动快时立即继续，启动慢时保留上限。
    while time.monotonic() < deadline:
        if _server_is_ready(server_url):
            break
        if process.poll() is not None:
            break
        time.sleep(0.5)
    else:
        _stop_process(process)
        pytest.fail(
            f"Appium Server 在 {timeout:g} 秒内未就绪：{server_url}\n"
            f"日志：{log_path}\n{_log_tail(log_path)}"
        )

    if not _server_is_ready(server_url):
        _stop_process(process)
        pytest.fail(
            f"Appium Server 启动失败：{server_url}\n"
            f"日志：{log_path}\n{_log_tail(log_path)}"
        )

    try:
        yield server_url
    finally:
        # 这里只会关闭本 fixture 创建的进程，不影响用户手工启动的 Server。
        _stop_process(process)


@pytest.fixture(scope="session")
def environment() -> EnvironmentConfig:
    """在一次 pytest 会话中只加载一次分层环境配置。"""

    return load_environment()


@pytest.fixture
def driver(environment: EnvironmentConfig, appium_server_url: str):
    """为每条用例创建独立 Appium Session，并在用例结束后关闭 Session。"""

    appium_driver = create_android_driver(appium_server_url, environment)
    yield appium_driver
    appium_driver.quit()


@pytest.fixture
def run_context(request: pytest.FixtureRequest) -> RunContext:
    """根据 case_id 标记创建当前用例的日志和诊断上下文。"""

    marker = request.node.get_closest_marker("case_id")
    if marker is None or not marker.args:
        pytest.fail("测试用例缺少 @pytest.mark.case_id 标记")
    return RunContext.create(str(marker.args[0]))
