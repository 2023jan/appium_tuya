# 第一阶段 PoC 计划

## 目标

验证一个文本测试用例可以通过 AI 辅助探索，转换成稳定的 Appium 自动化脚本。

本阶段输出不是完整框架，而是一个经过验证的最小闭环。

## 范围

范围内：

- Android 真机或模拟器通过 adb 连接。
- Appium Server 基础配置。
- Appium MCP 基础配置，用于 AI 辅助探索手机页面。
- 一个目标 App。
- 一到三个简单测试用例。
- Python + pytest + Appium 生成脚本。
- 失败时基础诊断产物收集。
- 最小日志能力，包括运行日志、失败截图、失败 page source 和基础 logcat。

范围外：

- 大规模批量生成。
- 完整页面对象库。
- iOS 支持。
- 多设备兼容矩阵。
- 云真机执行。
- 每次回归都由 AI 自主执行和判断。

## 目标流程

```text
输入文本测试用例
  -> AI 读取前置条件、步骤和预期结果
  -> AI 通过 Appium MCP 检查和操作手机
  -> AI 使用截图、page source、adb、日志纠正探索错误
  -> AI 用证据确认预期结果
  -> AI 生成 pytest + Appium 代码
  -> 脚本重复执行验证
  -> 失败时保存诊断产物
```

## 本地能力要求

- `adb devices` 可以识别目标手机或模拟器。
- Appium Server 可以启动并创建 session。
- 目标 App 的 package/activity 已知，或可以被发现。
- Appium MCP 可以连接到 Appium 环境。
- Python 环境可以运行 pytest 和 Appium Python client。

## 建议的最小代码结构

```text
appium_auto/
  core/
    driver_factory.py
    diagnostics.py
    logging.py
    waits.py
  cases/
    test_poc_case_001.py
  specs/
    poc_case_001.yaml
  logs/
  artifacts/
    runs/
    screenshots/
    page_sources/
    logs/
```

如果实现过程中需要更简单的起点，该结构可以调整。

## 第一条测试用例要求

第一条用例应尽量简单、稳定。

适合作为第一条的候选：

- 启动 App 并验证首页出现。
- 使用固定测试账号登录。
- 进入稳定的设置页或关于页。
- 验证已知静态文案或页面标题。

不适合作为第一条的候选：

- 复杂滚动列表操作。
- 动态后端数据检查。
- 支付、绑定、OTA 或不可逆操作。
- 对网络稳定性依赖很重的流程。
- 需要多个外部设备配合的流程。

## 生成脚本质量要求

生成脚本应满足：

- 使用显式等待。
- 除非没有更好的状态信号，否则避免固定 sleep。
- 优先使用稳定 locator。
- 对预期结果有明确断言。
- 失败时收集截图和 page source。
- 失败时保存运行日志和基础 logcat。
- 不依赖 AI 即可执行。
- 代码可读，便于人工 review。

## 验收标准

第一阶段满足以下条件时视为通过：

1. 设备可以通过 adb 识别。
2. Appium 可以启动或连接目标 App。
3. AI 可以通过 Appium MCP 检查当前页面。
4. AI 可以通过探索完成一个文本测试用例。
5. 为该用例生成 pytest + Appium 脚本。
6. 生成脚本在同一设备和同一 App 版本上至少连续成功执行 5 次。
7. 构造一次失败时，能产出有用诊断信息：
   - 截图。
   - page source。
   - 相关日志文件或 logcat 片段。
   - 失败步骤或断言上下文。
8. 每次执行有独立 run 目录或等效索引，可以把截图、page source、日志和报告关联起来。

## 风险和控制

### AI 找到的路径难以脚本化

控制方式：

- 探索阶段优先选择可以用稳定 locator 表达的交互。
- 拒绝坐标点击作为正式方案，除非明确标注为临时手段。

### 脚本成功一次但无法稳定重复

控制方式：

- 要求连续成功执行 5 次。
- 用显式等待替换固定 sleep。
- App 状态泄漏时增加 setup/reset 步骤。

### 预期结果过于模糊

控制方式：

- 把预期结果转换成可观察断言。
- 只有当预期无法从 UI、日志或设备状态观察时，才要求补充说明。

## 交付物

- 最小项目代码结构。
- 一个测试规格文件。
- 一个生成的 pytest + Appium 测试脚本。
- 基础诊断工具。
- 最小日志工具。
- 一份阶段执行结果记录。

## 需要补充的输入

- 目标 App package name。
- 目标 App launch activity，如果已知。
- 第一条文本测试用例。
- 如果需要登录，提供测试账号或测试数据。
- Android 设备型号和系统版本。
