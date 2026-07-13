---
name: code-callgraph
description: 分析 Python 仓库的模块分层、函数和类方法调用、pytest fixture 注入与测试用例复用关系，并生成 Mermaid 调用关系图和函数索引。用户要求理解分散代码、查看某个测试用例如何执行、追踪函数由谁调用、评审分层或在重构后更新代码地图时使用。
---

# Code Callgraph

## 工作流

1. 先读取仓库级指导文件和当前阶段文档，确认扫描范围与输出位置。
2. 运行 `scripts/generate_callgraph.py`，默认扫描 `appium_auto` 和 `tests`。
3. 检查生成文档中的项目总览、逐用例调用图、共享复用图和函数索引。
4. 对图中缺失或可疑的动态调用使用 `rg` 回查源码，不推测反射、字符串调用或第三方库内部行为。
5. 修改代码后重新生成，确认调用关系文档与当前源码一致。

## 生成命令

在仓库根目录运行：

```powershell
python .agents/skills/code-callgraph/scripts/generate_callgraph.py `
  --root . `
  --source appium_auto `
  --source tests `
  --output doc/code-callgraph.md
```

只分析业务代码时省略 `--source tests`。使用 `--max-depth` 控制逐用例调用图的递归深度。

## 输出要求

- 使用 Mermaid 表示静态结构和函数调用，不生成一张难以阅读的全量大图。
- 分别输出项目分层总览、每个 CASE 调用链、多个 CASE 的直接共享调用和函数索引。
- 在节点中保留函数或方法名，在索引中保留中文职责说明、相对文件路径和行号。
- 用 `fixture` 边区分 pytest 参数注入与普通函数调用。
- 排除 `.venv`、缓存、运行产物和非 Python 文件，不读取配置值或诊断产物。
- 明确声明静态分析边界：动态导入、反射、字符串定位和第三方库内部调用不保证可见。

## 判断原则

- 把图作为导航和评审入口，不把它当作运行时 trace。
- 优先展示项目内部调用；省略 `driver.click()`、`WebDriverWait.until()` 等第三方细节，避免噪声淹没业务关系。
- 当一个调用无法唯一解析到项目内定义时，宁可不连边，也不要制造错误关系。
- 发现层级反向依赖、跨层直连或大量共享函数时，在图外简要指出，不自动重构业务代码。
