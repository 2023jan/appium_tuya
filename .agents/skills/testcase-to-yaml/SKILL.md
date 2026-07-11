---
name: testcase-to-yaml
description: 将自然语言、TXT、Markdown、聊天文本、手工测试步骤或缺陷复现过程转换为统一 YAML 测试规格，并在进入自动化前执行完整性、明确性、可观察性、可重复性和恢复条件的质量评分与门禁。用户要求检查或结构化测试用例、转换或保存 YAML、根据文本生成 Appium/pytest 脚本、使用 Appium MCP 探索并生成测试，或其他自动化 Skill 收到尚未结构化的测试输入时使用；也用于校验下游流程收到的 YAML 是否已经通过门禁。
---

# 测试用例结构化与质量门禁

将本 Skill 作为自然语言测试输入进入 Appium 自动化流程前的必经步骤。只处理测试业务语义、结构化规格和自动化就绪性，不探索页面、不生成 locator、不生成 Appium 或 pytest 代码。

## 按需读取参考资料

- 评估任何输入前，读取 [references/quality-gate.md](references/quality-gate.md)，按统一维度、阈值和硬阻塞规则评分。
- 需要输出或检查 YAML 时，读取 [references/schema.md](references/schema.md)，严格使用其中的字段和约束。
- 需要判断边界或校准输出时，读取 [references/examples.md](references/examples.md)。其中包含 CASE00、CASE01 和低质量输入示例。

## 执行流程

1. 读取原始文本及用户提供的项目上下文；保留原始文件，不覆盖、不改写业务内容。
2. 识别测试目标、前置条件、测试数据、步骤、操作对象、预期结果、清理动作以及环境影响。
3. 先检查硬阻塞问题，再按六个维度评分。不得用文本长度或步骤数量代替质量判断。
4. 识别删除、解绑、清除数据、恢复出厂、注销等破坏性操作，并判断可重复性、人工准备、人工清理和默认回归资格。
5. 将密码、Token、API Key、验证码等敏感值转换为 `value_ref`；不得把真实秘密写入 YAML。
6. 根据评分和硬阻塞规则输出 `passed`、`review_required` 或 `blocked`。
7. 仅在 `passed` 时生成正式 YAML。未知信息写入 `missing_info`，真实歧义写入 `review_questions`，不得臆造 App package、Activity、locator、系统版本、账号、等待时间或业务规则。
8. 根据用户要求决定是否保存；仅在用户明确要求保存且门禁通过时写入 `appium_auto/specs/`。

## 忠实转换规则

- 保留原始测试意图和范围，不自动增加异常网络、设备离线、OTA、删除、重新配网或边界值场景。
- 将混合描述拆成 `action`、`target`、`value`/`value_ref` 和 `expected`；关键操作尽量关联就近预期。
- 只描述业务对象，例如“名称为 V4#4 的设备卡片”。禁止生成 XPath、resource-id、accessibility id、坐标或其他 locator。
- 破坏性不等于低质量。恢复影响和恢复方式明确时，破坏性用例仍可通过门禁，但通常关闭默认回归。
- 简单不等于低质量。若测试目标本身简单且前置、操作和可观察预期完整，应按实际复杂度给分。
- 不为凑齐 Schema 填充空泛或猜测内容；可选信息未知时保持空值，影响语义的信息缺失时进入门禁问题列表。

## 门禁行为

### `passed`

- 生成符合 Schema 的正式 YAML。
- 设置 `quality_gate.automation_ready: true`。
- 允许交给 Appium MCP、页面探索 Skill 或 Appium 脚本生成 Skill。
- 不要求用户重复提供同一份测试内容。

### `review_required`

- 暂停 Appium MCP 探索和正式代码生成。
- 输出逐维评分、缺失项、警告和少量高价值确认问题。
- 可以展示结构化预览，但必须标记“未通过自动化质量门禁”，默认不保存正式 YAML。
- 用户补充后基于合并后的输入重新检查硬阻塞并评分。

### `blocked`

- 停止后续自动化，不调用 Appium MCP，不生成正式 YAML 或 Appium Python 脚本。
- 说明硬阻塞原因，并只询问解除阻塞所需的最少信息。

## 文件写入规则

- 用户只要求“检查”时，只输出质量报告，不创建文件。
- 用户要求“转成 YAML”时，门禁通过后在响应中输出；是否保存以用户要求为准。
- 用户明确要求“转换并保存到项目”时，保存到 `appium_auto/specs/`，保留原始 TXT 或 Markdown。
- 目标 YAML 已存在时，先读取并比较人工修改字段；不得直接覆盖 `status: approved` 的规格。先报告变化与潜在冲突，用户确认后再更新。
- `review_required` 或 `blocked` 时不得创建看似完整、实际依赖猜测的正式规格文件。

## 下游交接

本 Skill 是 `appium-script-generator`、`appium-page-explorer`、`appium-failure-analysis`、`iot-test-generator` 等后续 Skill 的前置规格处理能力。

- 下游收到原始或非结构化测试用例时，先执行本 Skill。
- 只有同时满足以下字段时，才允许探索页面或生成代码：

```yaml
quality_gate:
  gate_status: "passed"
  automation_ready: true
```

- 收到 `review_required` 或 `blocked` 时，停止下游流程并把缺失项与确认问题交还用户。
- 收到已通过门禁的 YAML 时，不重复转换原始文本；只检查 `schema_version` 和必要字段。校验失败时退回本 Skill 重新评估。

## 输出顺序

对用户依次给出：门禁状态、总分和逐维评分、硬阻塞/警告/缺失信息、必要确认问题。仅在 `passed` 时继续给出标准 YAML 或保存路径。
