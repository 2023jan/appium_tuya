from __future__ import annotations

import argparse
import ast
import hashlib
import re
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Definition:
    symbol: str
    module: str
    name: str
    file: Path
    line: int
    node: ast.FunctionDef | ast.AsyncFunctionDef
    class_symbol: str | None = None
    is_fixture: bool = False
    is_case: bool = False


@dataclass
class ModuleInfo:
    name: str
    file: Path
    tree: ast.Module
    imports: dict[str, str] = field(default_factory=dict)


class CallGraphAnalyzer:
    def __init__(self, root: Path, sources: list[Path]) -> None:
        self.root = root.resolve()
        self.sources = sources
        self.modules: dict[str, ModuleInfo] = {}
        self.definitions: dict[str, Definition] = {}
        self.classes: set[str] = set()
        self.class_bases: dict[str, tuple[str, ...]] = {}
        self.class_attrs: dict[tuple[str, str], str] = {}
        self.fixtures: dict[str, str] = {}
        self.edges: set[tuple[str, str, str]] = set()

    def analyze(self) -> None:
        self._parse_modules()
        self._collect_definitions()
        self._collect_class_bases()
        self._collect_class_attributes()
        self._collect_calls()
        self._collect_fixture_injections()

    def _python_files(self) -> list[Path]:
        files: set[Path] = set()
        for source in self.sources:
            path = (self.root / source).resolve()
            if path.is_file() and path.suffix == ".py":
                files.add(path)
            elif path.is_dir():
                files.update(path.rglob("*.py"))
        return sorted(
            path
            for path in files
            if not any(
                part in {".venv", "__pycache__", "artifacts"}
                for part in path.parts
            )
        )

    def _module_name(self, path: Path) -> str:
        relative = path.relative_to(self.root).with_suffix("")
        parts = list(relative.parts)
        if parts[-1] == "__init__":
            parts.pop()
        return ".".join(parts)

    def _parse_modules(self) -> None:
        for path in self._python_files():
            module_name = self._module_name(path)
            tree = ast.parse(
                path.read_text(encoding="utf-8-sig"), filename=str(path)
            )
            info = ModuleInfo(module_name, path, tree)
            for node in tree.body:
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        info.imports[alias.asname or alias.name.split(".")[0]] = (
                            alias.name
                        )
                elif isinstance(node, ast.ImportFrom) and node.module:
                    for alias in node.names:
                        info.imports[alias.asname or alias.name] = (
                            f"{node.module}.{alias.name}"
                        )
            self.modules[module_name] = info

    @staticmethod
    def _decorator_name(node: ast.expr) -> str:
        if isinstance(node, ast.Call):
            return CallGraphAnalyzer._decorator_name(node.func)
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            prefix = CallGraphAnalyzer._decorator_name(node.value)
            return f"{prefix}.{node.attr}" if prefix else node.attr
        return ""

    def _collect_definitions(self) -> None:
        for module, info in self.modules.items():
            relative = info.file.relative_to(self.root).as_posix()
            for node in info.tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbol = f"{module}.{node.name}"
                    decorators = {
                        self._decorator_name(item) for item in node.decorator_list
                    }
                    definition = Definition(
                        symbol=symbol,
                        module=module,
                        name=node.name,
                        file=info.file,
                        line=node.lineno,
                        node=node,
                        is_fixture=any(
                            name.endswith("fixture") for name in decorators
                        ),
                        is_case=(
                            "/cases/" in f"/{relative}"
                            and node.name.startswith("test_")
                        ),
                    )
                    self.definitions[symbol] = definition
                    if definition.is_fixture:
                        self.fixtures[node.name] = symbol
                elif isinstance(node, ast.ClassDef):
                    class_symbol = f"{module}.{node.name}"
                    self.classes.add(class_symbol)
                    for item in node.body:
                        if not isinstance(
                            item, (ast.FunctionDef, ast.AsyncFunctionDef)
                        ):
                            continue
                        symbol = f"{class_symbol}.{item.name}"
                        self.definitions[symbol] = Definition(
                            symbol=symbol,
                            module=module,
                            name=item.name,
                            file=info.file,
                            line=item.lineno,
                            node=item,
                            class_symbol=class_symbol,
                        )

    def _collect_class_bases(self) -> None:
        for module, info in self.modules.items():
            for node in info.tree.body:
                if not isinstance(node, ast.ClassDef):
                    continue
                class_symbol = f"{module}.{node.name}"
                bases: list[str] = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        candidate = self._resolve_name(module, base.id)
                    else:
                        candidate = self._attribute_text(base)
                    if candidate in self.classes:
                        bases.append(candidate)
                self.class_bases[class_symbol] = tuple(bases)

    def _resolve_name(self, module: str, name: str) -> str | None:
        local = f"{module}.{name}"
        if local in self.definitions or local in self.classes:
            return local
        imported = self.modules[module].imports.get(name)
        if imported in self.definitions or imported in self.classes:
            return imported
        return None

    def _annotation_type(
        self, module: str, node: ast.expr | None
    ) -> str | None:
        if isinstance(node, ast.Name):
            candidate = self._resolve_name(module, node.id)
            return candidate if candidate in self.classes else None
        if isinstance(node, ast.Attribute):
            candidate = self._attribute_text(node)
            return candidate if candidate in self.classes else None
        return None

    @staticmethod
    def _attribute_parts(node: ast.expr) -> list[str] | None:
        parts: list[str] = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if not isinstance(current, ast.Name):
            return None
        parts.append(current.id)
        return list(reversed(parts))

    @staticmethod
    def _attribute_text(node: ast.expr) -> str:
        parts = CallGraphAnalyzer._attribute_parts(node)
        return ".".join(parts) if parts else ""

    def _constructor_type(self, module: str, node: ast.expr) -> str | None:
        if not isinstance(node, ast.Call):
            return None
        if isinstance(node.func, ast.Name):
            candidate = self._resolve_name(module, node.func.id)
            return candidate if candidate in self.classes else None
        return None

    def _collect_class_attributes(self) -> None:
        for definition in self.definitions.values():
            if not definition.class_symbol or definition.name != "__init__":
                continue
            for node in ast.walk(definition.node):
                if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                    continue
                value = node.value
                if value is None:
                    continue
                class_type = self._constructor_type(definition.module, value)
                if not class_type:
                    continue
                targets = (
                    node.targets if isinstance(node, ast.Assign) else [node.target]
                )
                for target in targets:
                    parts = self._attribute_parts(target)
                    if parts and len(parts) == 2 and parts[0] == "self":
                        self.class_attrs[(definition.class_symbol, parts[1])] = (
                            class_type
                        )

    def _local_types(self, definition: Definition) -> dict[str, str]:
        result: dict[str, str] = {}
        arguments = list(definition.node.args.posonlyargs) + list(
            definition.node.args.args
        )
        for argument in arguments:
            class_type = self._annotation_type(
                definition.module, argument.annotation
            )
            if class_type:
                result[argument.arg] = class_type
        for node in ast.walk(definition.node):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            value = node.value
            if value is None:
                continue
            class_type = self._constructor_type(definition.module, value)
            if not class_type:
                continue
            targets = (
                node.targets if isinstance(node, ast.Assign) else [node.target]
            )
            for target in targets:
                if isinstance(target, ast.Name):
                    result[target.id] = class_type
        return result

    def _method_target(
        self, class_symbol: str, attributes: list[str]
    ) -> str | None:
        current = class_symbol
        for attribute in attributes[:-1]:
            current = self.class_attrs.get((current, attribute), "")
            if not current:
                return None
        return self._find_method(current, attributes[-1])

    def _find_method(
        self, class_symbol: str, method_name: str, seen: set[str] | None = None
    ) -> str | None:
        visited = seen or set()
        if class_symbol in visited:
            return None
        visited.add(class_symbol)
        target = f"{class_symbol}.{method_name}"
        if target in self.definitions:
            return target
        for base in self.class_bases.get(class_symbol, ()):
            inherited = self._find_method(base, method_name, visited)
            if inherited:
                return inherited
        return None

    def _resolve_call(
        self,
        definition: Definition,
        call: ast.Call,
        local_types: dict[str, str],
    ) -> str | None:
        if isinstance(call.func, ast.Name):
            candidate = self._resolve_name(definition.module, call.func.id)
            if candidate in self.classes:
                return self._find_method(candidate, "__init__")
            return candidate if candidate in self.definitions else None

        parts = self._attribute_parts(call.func)
        if not parts or len(parts) < 2:
            return None
        root, attributes = parts[0], parts[1:]
        if root == "self" and definition.class_symbol:
            return self._method_target(definition.class_symbol, attributes)
        if root in local_types:
            return self._method_target(local_types[root], attributes)

        imported = self.modules[definition.module].imports.get(root)
        if imported in self.classes:
            return self._method_target(imported, attributes)
        return None

    def _collect_calls(self) -> None:
        for definition in self.definitions.values():
            local_types = self._local_types(definition)
            for node in ast.walk(definition.node):
                if not isinstance(node, ast.Call):
                    continue
                target = self._resolve_call(definition, node, local_types)
                if target and target != definition.symbol:
                    self.edges.add((definition.symbol, target, "call"))

    def _collect_fixture_injections(self) -> None:
        for definition in self.definitions.values():
            if not (definition.is_case or definition.is_fixture):
                continue
            arguments = list(definition.node.args.posonlyargs) + list(
                definition.node.args.args
            )
            for argument in arguments:
                target = self.fixtures.get(argument.arg)
                if target and target != definition.symbol:
                    self.edges.add((definition.symbol, target, "fixture"))


def layer_of(definition: Definition) -> str:
    path = definition.file.as_posix()
    if definition.is_case:
        return "用例"
    if definition.is_fixture or path.endswith("/conftest.py"):
        return "Fixture"
    if "/flows/" in path:
        return "Flow"
    if "/pages/" in path:
        return "Page"
    if "/core/" in path:
        return "Core"
    if "/tests/" in f"/{path}":
        return "单元测试"
    return "其他"


def short_name(definition: Definition) -> str:
    if definition.class_symbol:
        class_name = definition.class_symbol.rsplit(".", 1)[-1]
        return f"{class_name}.{definition.name}()"
    return f"{definition.name}()"


def node_id(symbol: str) -> str:
    digest = hashlib.sha1(symbol.encode("utf-8")).hexdigest()[:10]
    return f"n{digest}"


def case_id(definition: Definition) -> str:
    match = re.search(r"case(\d+)", definition.file.name, re.IGNORECASE)
    return f"CASE{match.group(1)}" if match else definition.name


def reachable_edges(
    root: str,
    edges: set[tuple[str, str, str]],
    max_depth: int,
) -> set[tuple[str, str, str]]:
    outgoing: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for source, target, kind in edges:
        outgoing[source].append((target, kind))
    result: set[tuple[str, str, str]] = set()
    seen_depth: dict[str, int] = {root: 0}
    queue = deque([root])
    while queue:
        source = queue.popleft()
        depth = seen_depth[source]
        if depth >= max_depth:
            continue
        for target, kind in sorted(outgoing.get(source, [])):
            result.add((source, target, kind))
            next_depth = depth + 1
            if next_depth < seen_depth.get(target, max_depth + 1):
                seen_depth[target] = next_depth
                queue.append(target)
    return result


def render_graph(
    definitions: dict[str, Definition],
    graph_edges: set[tuple[str, str, str]],
    root: str | None = None,
) -> list[str]:
    symbols = {item for edge in graph_edges for item in edge[:2]}
    if root:
        symbols.add(root)
    lines = ["```mermaid", "flowchart TD"]
    for symbol in sorted(symbols):
        definition = definitions[symbol]
        label = short_name(definition)
        if definition.is_case:
            label = f"{case_id(definition)}<br/>{label}"
        elif definition.is_fixture:
            label = f"fixture<br/>{label}"
        lines.append(f'    {node_id(symbol)}["{label}"]')
    for source, target, kind in sorted(graph_edges):
        connector = " -->|fixture| " if kind == "fixture" else " --> "
        lines.append(f"    {node_id(source)}{connector}{node_id(target)}")
    lines.append("```")
    return lines


def render_document(analyzer: CallGraphAnalyzer, max_depth: int) -> str:
    definitions = analyzer.definitions
    case_roots = sorted(
        (
            definition
            for definition in definitions.values()
            if definition.is_case
        ),
        key=lambda item: item.file.name,
    )
    lines = [
        "# Python 代码调用关系图",
        "",
        "> 本文档由 `.agents/skills/code-callgraph/scripts/generate_callgraph.py` 基于 Python AST 生成。",
        "> 图中只包含可静态解析的项目内部调用和 pytest fixture 注入；动态反射、字符串调用及第三方库内部调用不在图中。",
        "",
        "## 项目分层总览",
        "",
        "```mermaid",
        "flowchart LR",
        '    specs["测试规格 YAML"] --> cases["CASE 测试用例"]',
        '    cases --> fixtures["pytest fixtures"]',
        '    cases --> flows["DeviceLifecycleFlow"]',
        '    flows --> pages["Page Objects"]',
        '    pages --> base["BasePage"]',
        '    fixtures --> core["环境 / Driver / RunContext"]',
        '    flows --> core',
        '    pages --> core',
        '    core --> external["Appium / Selenium / Android"]',
        "```",
        "",
    ]

    for root_definition in case_roots:
        graph_edges = reachable_edges(
            root_definition.symbol, analyzer.edges, max_depth
        )
        lines.extend(
            [
                f"## {case_id(root_definition)} 调用图",
                "",
                *render_graph(
                    definitions, graph_edges, root_definition.symbol
                ),
                "",
            ]
        )

    direct_by_target: dict[str, set[str]] = defaultdict(set)
    edge_kind: dict[tuple[str, str], str] = {}
    case_symbols = {definition.symbol for definition in case_roots}
    for source, target, kind in analyzer.edges:
        if source in case_symbols:
            direct_by_target[target].add(source)
            edge_kind[(source, target)] = kind
    shared_targets = {
        target
        for target, callers_for_target in direct_by_target.items()
        if len(callers_for_target) >= 2
    }
    shared_edges = {
        (source, target, edge_kind[(source, target)])
        for target in shared_targets
        for source in direct_by_target[target]
    }
    lines.extend(["## CASE 直接共享调用", ""])
    if shared_edges:
        lines.extend(render_graph(definitions, shared_edges))
    else:
        lines.append("当前没有至少被两个 CASE 直接调用的项目内部函数。")
    lines.append("")

    callers: dict[str, set[str]] = defaultdict(set)
    callees: dict[str, set[str]] = defaultdict(set)
    for source, target, _kind in analyzer.edges:
        callers[target].add(source)
        callees[source].add(target)
    lines.extend(
        [
            "## 函数索引",
            "",
            "| 层级 | 函数或方法 | 定义位置 | 项目内调用者数 | 项目内调用数 |",
            "| --- | --- | --- | ---: | ---: |",
        ]
    )
    sorted_definitions = sorted(
        definitions.values(),
        key=lambda item: (
            layer_of(item),
            item.file.as_posix(),
            item.line,
        ),
    )
    for definition in sorted_definitions:
        relative = definition.file.relative_to(analyzer.root).as_posix()
        lines.append(
            f"| {layer_of(definition)} | `{short_name(definition)}` | "
            f"`{relative}:{definition.line}` | "
            f"{len(callers[definition.symbol])} | "
            f"{len(callees[definition.symbol])} |"
        )
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="生成 Python 项目的 Mermaid 调用关系图"
    )
    parser.add_argument(
        "--root", type=Path, default=Path.cwd(), help="仓库根目录"
    )
    parser.add_argument(
        "--source",
        action="append",
        type=Path,
        dest="sources",
        help="相对仓库根目录的扫描目录，可重复指定",
    )
    parser.add_argument(
        "--output", type=Path, help="Markdown 输出路径；省略时输出到终端"
    )
    parser.add_argument(
        "--max-depth", type=int, default=8, help="逐用例调用图最大深度"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    sources = args.sources or [Path("appium_auto"), Path("tests")]
    analyzer = CallGraphAnalyzer(root, sources)
    analyzer.analyze()
    document = render_document(analyzer, max_depth=max(1, args.max_depth))
    if args.output:
        output = (
            (root / args.output).resolve()
            if not args.output.is_absolute()
            else args.output
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(document, encoding="utf-8")
        print(f"已生成调用关系图：{output}")
    else:
        print(document)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
