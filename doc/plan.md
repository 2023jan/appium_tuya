# AI 辅助 Appium 自动化脚本生成整体规划

## 目标

建设一个本地框架，用 AI 辅助从文本测试用例生成、调试和维护 Appium 自动化脚本。

核心流程：

1. 用户提供文本测试用例，包含操作步骤和预期结果。
2. `testcase-to-yaml` 对输入进行结构化、质量评分和质量门禁；只有通过门禁的 YAML 才进入自动化流程。
3. 第一阶段 PoC 先建立人工稳定基线，确认环境、目标 App 和测试场景可以被确定性自动化。
4. AI 通过 Appium MCP 和 Appium Server 连接手机。
5. AI 在手机上探索目标 App，通过截图、UI 层级、adb 数据和日志自行纠错。
6. 当观察到的现象与测试用例预期一致后，AI 生成对应的稳定 Appium 自动化脚本。
7. 生成的脚本至少通过 1 次确定性执行验证，并与人工稳定基线比较质量差异。
8. 后续测试用例沿用同样流程，并复用已经沉淀的框架代码。

## 产品定位

本项目定位为：AI 辅助 Appium 测试脚本生产框架。

本项目不定位为：每次正式测试执行都由 AI 自主推理和判断的移动端测试平台。

推荐边界：

- 脚本生产和调试阶段：AI 可以推理、探索、点击、查看页面、纠错。
- 回归执行阶段：使用确定性的 Appium 脚本执行，不让 AI 每一步自由判断。
- 失败分析阶段：AI 可以读取截图、page source、日志和执行报告，辅助判断原因。

## 项目价值

- 降低 Appium 使用门槛，适合对 Appium 还不熟的测试人员或开发人员。
- 把手工测试步骤转换为可重复执行的自动化资产。
- 最终产物是普通代码，可以 review、维护和复用。
- 正式回归时不需要每次消耗 AI token，也减少 AI 幻觉影响测试判定。
- 通过自动收集截图、page source、日志和步骤上下文，提高失败排查效率。

## 高层架构

```text
文本测试用例
  -> testcase-to-yaml
    -> 质量评分和质量门禁
      -> 未通过：暂停自动化，补充测试信息后重新评价
      -> 通过：生成标准 YAML
  -> 人工稳定基线
  -> 确认环境和测试场景可稳定自动化
  -> AI 脚本生产循环
    -> Appium MCP
      -> Appium Server
        -> Android 真机或模拟器
  -> 生成 pytest + Appium 脚本
  -> 至少 1 次确定性执行验证和质量比较
  -> 产物和报告
```

预期本地组件：

- Python 测试框架。
- pytest 作为测试执行器。
- Appium Python client。
- Appium Server。
- Appium MCP，用于 AI 辅助探索手机页面。
- adb，用于 Android 设备信息、日志和诊断。
- Appium Inspector，作为可选的人工页面检查工具。

## 核心原则

1. AI 可以在脚本生成阶段探索，但生成后的脚本必须确定性执行。
2. 生成脚本优先使用稳定 locator 和显式等待，不优先使用坐标点击。
3. 每个生成用例必须包含有意义的断言。
4. 每次失败必须保存诊断产物。
5. 页面对象和公共工具应逐步沉淀，不提前过度设计。
6. AI 生成的脚本进入正式回归前需要人工 review。

## 预期项目结构

实际结构可以演进，但目标方向如下：

```text
03_appium_auto/
  doc/
    plan.md
    phase_01_poc/
      plan.md
    phase_02_framework/
      plan.md
    phase_03_batch_generation/
      plan.md

  appium_auto/
    core/
      driver_factory.py
      base_page.py
      waits.py
      gestures.py
      assertions.py
      diagnostics.py
      logging.py
      log_collectors.py
    pages/
    cases/
    specs/
    logs/
    artifacts/
      runs/
      screenshots/
      page_sources/
      appium_logs/
      device_logs/
      mcp_logs/
```

## 日志模块规划

日志模块是第一阶段就需要考虑的基础能力。它不只是记录执行过程，还要服务于三个目标：

- 人工排查失败原因。
- AI 根据失败产物辅助分析。
- 后续重复执行时对比同一用例的不同行为。

### 日志类型

项目需要逐步支持以下日志和产物：

- 测试运行日志：记录用例开始、步骤开始、步骤结束、断言、失败原因、耗时和设备信息。
- Appium Server 日志：记录 Appium session 创建、命令调用、driver 错误和服务端异常。
- 设备日志：Android 阶段主要是 `adb logcat`，必要时按用例维度截取。
- Appium MCP 调用记录：记录 AI 探索时调用了哪些 MCP 工具、关键参数、返回结果摘要和失败原因。
- 页面产物：截图、page source、窗口尺寸、当前 activity/package。
- 执行索引：每次运行生成一个独立 run id，把日志、截图、page source 和报告串起来。

### 推荐目录结构

```text
appium_auto/
  logs/
    runtime.log
    appium_server.log
    device.log
    mcp.log

  artifacts/
    runs/
      20260708_001_login_success/
        run_meta.yaml
        runtime.log
        appium_server.log
        device.log
        mcp.log
        screenshots/
        page_sources/
        report.yaml
```

### 运行日志要求

运行日志默认使用中文，至少包含：

- run id。
- 用例 id 和用例名称。
- 设备 udid、系统版本、屏幕尺寸。
- App package、activity、版本号。
- 每个步骤的开始、结束、耗时和结果。
- 失败时的异常类型、错误信息、失败步骤。
- 失败时关联的截图路径、page source 路径和日志路径。

### Appium Server 日志

第一阶段可以先使用文件重定向或 Appium 启动参数保存 Appium Server 日志。后续框架化阶段再封装统一启动和停止能力。

日志重点：

- session 创建参数。
- driver 初始化失败。
- 元素查找失败。
- 点击、输入、滑动等命令失败。
- session 删除和清理结果。

### 设备日志

Android 第一阶段使用 `adb logcat`。

建议策略：

- 每个用例开始前清理或记录当前 logcat 起点。
- 用例执行期间采集 logcat 到当前 run 目录。
- 失败时保留完整片段。
- 后续可支持按 package、tag、关键字过滤。

### MCP 调用记录

MCP 调用记录用于复盘 AI 探索过程。正式回归执行不依赖 AI，但脚本生产阶段需要知道 AI 做过什么。

记录内容：

- 调用时间。
- 工具名称，例如 `appium_get_page_source`、`appium_screenshot`、`appium_find_element`。
- 关键参数摘要，避免记录账号密码等敏感数据。
- 返回结果摘要。
- 是否成功。
- 失败原因。

### 日志模块边界

第一阶段只实现最小可用能力：

- pytest 运行日志。
- 失败截图。
- 失败 page source。
- 基础 logcat 采集。
- run 目录归档。

第二阶段再提取为统一日志模块：

- `logging.py`：统一 logger 初始化、格式、run id、路径管理。
- `log_collectors.py`：Appium Server、adb logcat、MCP 调用记录等采集器。
- `diagnostics.py`：失败时统一收集截图、page source、日志索引和报告。

第三阶段再扩展：

- 多用例批量执行报告。
- 历史运行对比。
- AI 失败分析输入包。
- 可选 HTML 报告。

## 测试用例输入和结构化

项目应支持用户直接提供自然语言或普通文本格式测试用例。为了让后续 AI 探索、脚本生成、执行验证和失败分析更稳定，项目内部应先把用户输入转换成结构化 YAML，再基于 YAML 推理和生成脚本。

推荐流程：

```text
用户文本测试用例
  -> testcase-to-yaml
  -> 质量评分和质量门禁
    -> review_required / blocked：暂停自动化，补充信息后重新评价
    -> passed：生成标准 YAML 草稿
  -> 用户审核和修改
  -> AI 按审核后的 YAML 探索手机并生成 Appium 脚本
```

`testcase-to-yaml` 负责从用户原始描述中提取：

- 用例名称。
- 前置条件。
- 测试数据。
- 操作步骤。
- 每一步的输入值。
- 预期结果。
- 需要人工确认的歧义点。

如果用户已经提供结构化 YAML，则检查 Schema 版本、必要字段和质量门禁状态。只有 `quality_gate.gate_status: passed` 且 `automation_ready: true` 时，才跳过重复转换并进入审核和执行准备。

文本转 YAML 能力由项目级 Skill `.agents/skills/testcase-to-yaml/` 提供。该 Skill 同时负责质量评分和门禁，只把通过门禁的输入整理成正式结构化规格；它不负责操作手机、生成 locator 或生成 Appium 脚本。

示例方向：

```yaml
name: 登录成功
description: 验证使用正确手机号和验证码可以登录成功
preconditions:
  - App 已安装
  - 测试账号存在
test_data:
  phone: "13800000000"
  verify_code: "123456"
steps:
  - action: 打开 App
  - action: 输入手机号
    value_ref: phone
  - action: 输入验证码
    value_ref: verify_code
  - action: 点击登录
expected:
  - 首页已显示
  - 设备列表可见
  - 不出现登录失败提示
review_questions:
  - 验证码是否固定为测试环境通用验证码？
```

### 文本转 YAML skill 设计

建议 skill 名称：`testcase-to-yaml`。

触发场景：

- 用户提供自然语言测试用例，希望转换成可执行前的结构化规格。
- 用户粘贴手工测试用例、Excel 导出的文本、缺陷复现步骤或临时测试说明。
- 用户要求“先整理成 YAML”“生成测试规格”“把这个用例结构化”。

输入：

- 原始测试用例文本。
- 可选：目标 App 名称、模块名、环境、账号信息、约束说明。

输出：

- 一份包含六个评分维度的质量报告。
- `passed`、`review_required` 或 `blocked` 门禁状态。
- 歧义点、缺失信息和少量必要确认问题。
- 仅在门禁通过时输出标准 YAML 草稿。

约束：

- 不臆造关键测试数据。
- 不把不确定内容写成确定事实。
- 对无法判断的内容写入 `review_questions` 或 `missing_info`。
- 保留用户原始意图，不主动扩展额外测试范围。
- 不生成 locator，不替代后续 Appium MCP 页面探索。
- 质量门禁未通过时，暂停 Appium MCP 和代码生成。
- 输出 YAML 要便于后续 AI 探索和 Appium 脚本生成。

建议 YAML 字段：

```yaml
schema_version: "1.0"
status: "draft"
quality_gate:
  score: 0
  grade: ""
  gate_status: ""
  automation_ready: false
id: ""
name: ""
description: ""
module: ""
priority: ""
tags: []
execution:
  repeatable: false
  destructive: false
  manual_setup_required: false
  manual_cleanup_required: false
  default_regression_enabled: false
preconditions: []
test_data: {}
steps:
  - id: 1
    action: ""
    target: ""
    value: ""
    value_ref: ""
    expected: []
expected: []
cleanup: []
missing_info: []
review_questions: []
source_file: ""
source_text: |
  原始测试用例
```

质量门禁采用 100 分制：85-100 且没有硬阻塞时为 `passed`，70-84 为 `review_required`，0-69 为 `blocked`。硬阻塞优先于总分，包括测试目标或关键对象未知、关键步骤存在根本歧义、没有可观察预期、破坏性影响或恢复方式无法判断，以及敏感数据无法安全转换为引用等。详细规则和 Schema 以 `.agents/skills/testcase-to-yaml/references/` 为准。

## 阶段规划

### 第一阶段：PoC

用一个 App 和少量测试用例验证完整闭环。

第一阶段先在 PoC 内部建立人工稳定基线，用于确认 adb、Appium、目标 App、测试数据、locator、等待和断言本身可稳定工作。该步骤不是新的正式产品阶段，不改变现有 Phase 1、Phase 2、Phase 3 的总体阶段结构。

人工稳定基线通过后，再使用同一个测试用例验证自然语言、Appium MCP 探索和 AI 脚本生成流程。AI 生成脚本的价值需要通过与稳定基线比较来评价，而不是只看单次是否能跑通。

成功标准：

- 手机或模拟器可以通过 adb 连接。
- Appium Server 可以控制目标 App。
- 第一条非破坏性用例可以形成可重复执行的人工稳定基线。
- AI 可以通过 Appium MCP 探索页面。
- 一个文本测试用例可以转换成 pytest + Appium 脚本。
- 生成脚本可以成功执行至少 1 次，并能与人工稳定基线比较质量差异。
- 失败时可以收集诊断产物。

详细计划：`phase_01_poc/plan.md`。

### 第二阶段：框架化提取

把 PoC 代码整理成可复用的框架模块。

重点：

- driver 创建和 capabilities 管理。
- base page 页面基类。
- 显式等待工具。
- 通用手势。
- 统一日志模块。
- 诊断产物收集。
- 测试数据和环境配置。
- 常见 App 流程的页面对象。

详细计划：`phase_02_framework/plan.md`。

### 第三阶段：批量生成

支持多个测试用例，并复用已经沉淀的框架资产。

重点：

- YAML/JSON 测试用例规格。
- 批量脚本生成流程。
- 复用已有页面对象和 locator。
- 人工 review 流程。
- 回归执行和报告。
- 历史日志归档和失败分析输入包。

详细计划：`phase_03_batch_generation/plan.md`。

## 主要风险

### locator 不稳定

移动端 App 经常缺少稳定的 accessibility id。文案、层级和索引也可能随着版本或设备变化。

控制方式：

- 优先使用 `accessibility id` 和 resource-id。
- 必要时才使用 XPath。
- locator 选择不明显时，在页面对象中记录原因。
- 避免把坐标点击作为正式脚本方案。

### AI 生成脆弱脚本

AI 可能生成只成功一次、但在时序、数据或设备变化下失败的脚本。

控制方式：

- 脚本接受前必须成功执行至少 1 次验证。
- 使用显式等待和状态断言。
- 失败时保存诊断产物。
- 生成脚本进入正式使用前必须 review。

### 环境和数据污染

App 状态、账号状态、网络状态和设备权限都可能影响测试结果。

控制方式：

- 明确记录前置条件。
- 尽量加入 reset/setup 步骤。
- 使用专用测试账号和测试数据。
- 统一处理常见权限弹窗和升级弹窗。

### AI 探索阶段幻觉

AI 可能误判页面状态，或者在预期结果模糊时漏过问题。

控制方式：

- 预期结果要具体、可观察。
- 断言需要有 page source、截图或日志证据。
- 正式回归的通过/失败判定尽量不依赖 AI。

## 待决事项

- 目标 App 的 package name 和 launch activity。
- CASE00 基线执行所需的账号登录态、设备 `V4#4` 在线状态和设备列表位置。

## 已确认决策

- 第一阶段只支持 Android。
- 生成脚本语言使用 Python。
- Appium MCP 采用全局安装，并注册到 Codex MCP。
- 第一阶段 PoC 先使用 CASE00 作为人工稳定基线候选；CASE01 删除设备成功保留为破坏性或需要人工恢复环境的测试用例。
