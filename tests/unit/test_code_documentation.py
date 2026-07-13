import ast
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[2]
PYTHON_SOURCE_ROOTS = (
    PROJECT_ROOT / "appium_auto",
    PROJECT_ROOT / "tests",
    PROJECT_ROOT / ".agents" / "skills",
)
CHINESE_PATTERN = re.compile(r"[\u4e00-\u9fff]")


def _python_files() -> list[Path]:
    """返回需要执行中文函数说明门禁的项目 Python 文件。"""

    files: set[Path] = set()
    for source_root in PYTHON_SOURCE_ROOTS:
        files.update(source_root.rglob("*.py"))
    return sorted(
        path
        for path in files
        if not any(part in {".venv", "__pycache__", "artifacts"} for part in path.parts)
    )


def _missing_chinese_docstrings(path: Path) -> list[str]:
    """收集指定文件中缺少中文 docstring 的函数和方法位置。"""

    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    missing: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        docstring = ast.get_docstring(node, clean=False) or ""
        if not CHINESE_PATTERN.search(docstring):
            relative = path.relative_to(PROJECT_ROOT).as_posix()
            missing.append(f"{relative}:{node.lineno} {node.name}")
    return missing


def test_all_python_functions_have_chinese_docstrings():
    """确保现有及后续生成的 Python 函数都提供中文职责说明。"""

    missing = [
        item
        for path in _python_files()
        for item in _missing_chinese_docstrings(path)
    ]

    assert not missing, "以下函数缺少中文 docstring：\n" + "\n".join(missing)
