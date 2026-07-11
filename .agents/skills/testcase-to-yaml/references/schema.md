# YAML 测试规格 Schema

## 目录

- 顶层结构
- 字段定义
- 字段约束
- 敏感信息
- 兼容与更新

## 顶层结构

仅对通过质量门禁的测试用例生成正式规格：

```yaml
schema_version: "1.0"
status: "draft"

quality_gate:
  score: 92
  grade: "A"
  gate_status: "passed"
  automation_ready: true
  dimensions:
    objective_and_scope:
      score: 10
      max_score: 10
      reason: ""
    preconditions:
      score: 13
      max_score: 15
      reason: ""
    steps:
      score: 23
      max_score: 25
      reason: ""
    action_and_target_clarity:
      score: 14
      max_score: 15
      reason: ""
    expected_results:
      score: 24
      max_score: 25
      reason: ""
    repeatability_and_recovery:
      score: 8
      max_score: 10
      reason: ""
  hard_blockers: []
  warnings: []

id: "CASE00"
name: "查看设备详情成功"
description: ""
module: ""
priority: ""
tags: []

execution:
  repeatable: true
  destructive: false
  manual_setup_required: false
  manual_cleanup_required: false
  default_regression_enabled: true

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

## 字段定义

| 字段 | 必需 | 定义 |
| --- | --- | --- |
| `schema_version` | 是 | 当前固定为字符串 `1.0`，供下游兼容检查。 |
| `status` | 是 | 规格生命周期状态。新生成使用 `draft`；`approved` 只能由明确的人工审核结果产生。 |
| `quality_gate` | 是 | 本次质量评分、门禁状态和问题摘要。 |
| `quality_gate.score` | 是 | 六个维度得分之和，范围 0 到 100。 |
| `quality_gate.grade` | 是 | 展示等级：A 为 90-100，B 为 85-89，C 为 70-84，D 为 0-69。门禁仍以阈值和硬阻塞共同判断。 |
| `quality_gate.gate_status` | 是 | `passed`、`review_required` 或 `blocked`。正式 YAML 必须为 `passed`。 |
| `quality_gate.automation_ready` | 是 | 仅在门禁通过时为 `true`。 |
| `quality_gate.dimensions` | 是 | 六个评分维度的得分、满分和简短依据。 |
| `quality_gate.hard_blockers` | 是 | 硬阻塞列表；`passed` 时必须为空。 |
| `quality_gate.warnings` | 是 | 不阻断测试含义但需下游或人工关注的问题。 |
| `id` | 是 | 稳定的用例标识。输入未提供且无法从文件名可靠提取时，列入 `missing_info`。 |
| `name` | 是 | 简洁描述测试目标，不扩大原始范围。 |
| `description` | 否 | 对目标或范围的补充说明。 |
| `module` | 否 | 业务模块；未知时留空，不猜测。 |
| `priority` | 否 | 项目优先级；未知时留空。 |
| `tags` | 是 | 分类标签列表，无标签时使用空列表。 |
| `execution` | 是 | 描述重复运行、破坏性、人工准备/清理和默认回归资格。 |
| `preconditions` | 是 | 建立测试开始状态所需的条件。 |
| `test_data` | 是 | 测试中使用的数据或安全引用。无数据时使用空映射。 |
| `steps` | 是 | 有序操作列表。每一步使用业务语义，不包含 locator。 |
| `expected` | 是 | 跨步骤或用例结束时的总体预期。 |
| `cleanup` | 是 | 自动或人工清理说明。无清理时使用空列表。 |
| `missing_info` | 是 | 已知缺失但不应被猜测的信息。影响测试含义时不得通过门禁。 |
| `review_questions` | 是 | 需要用户确认的真实歧义。`passed` 时不得包含影响测试含义的问题。 |
| `source_file` | 是 | 原始文件的仓库相对路径；聊天输入可留空。 |
| `source_text` | 是 | 原始输入原文，使用 YAML 块文本忠实保留。 |

### `execution`

| 字段 | 定义 |
| --- | --- |
| `repeatable` | 不经额外恢复是否能再次执行同一用例。 |
| `destructive` | 是否删除、解绑、清除或不可逆地改变关键状态。 |
| `manual_setup_required` | 下一次执行前是否需要人工建立前置状态。 |
| `manual_cleanup_required` | 本次执行后是否需要人工恢复或清理环境。 |
| `default_regression_enabled` | 是否适合进入默认连续回归。破坏性或需人工恢复的用例通常为 `false`。 |

### `steps[]`

| 字段 | 定义 |
| --- | --- |
| `id` | 从 1 开始的稳定步骤序号。 |
| `action` | 明确动作，如“启动”“点击”“输入”“返回”“滚动”。 |
| `target` | 业务可识别对象，如“名称为 V4#4 的设备卡片”。 |
| `value` | 非敏感的字面输入；无输入时使用空字符串。 |
| `value_ref` | 测试数据或秘密引用；与 `value` 通常只使用一个。 |
| `expected` | 该步骤完成后可观察、可断言的结果列表。 |

## 字段约束

- 不包含 locator、XPath、resource-id、accessibility id、坐标或等待秒数。
- 不自动生成原始测试未要求的步骤、异常场景或断言。
- `expected` 必须可由 UI、日志、设备状态、接口状态或用户指定的其他证据观察。
- `gate_status: passed` 时，`automation_ready` 必须为 `true`，`hard_blockers` 必须为空。
- `review_required` 和 `blocked` 只能用于质量报告或明确标记的预览，不保存为正式自动化规格。
- 破坏性操作必须显式设置 `execution.destructive: true`，并说明是否需要人工恢复以及默认回归资格。

## 敏感信息

不得在规格中写入真实密码、Wi-Fi 密码、Token、API Key、私钥、验证码或其他认证信息。改用引用：

```yaml
test_data:
  password:
    value_ref: "TEST_PASSWORD"
```

引用值应由环境变量、Git Ignore 下的本地私有配置或等效秘密管理方式提供。若无法安全替换敏感值，加入硬阻塞并停止生成正式 YAML。

## 兼容与更新

- 下游收到 `schema_version: "1.0"` 且门禁通过的 YAML 时，无需重复转换原始文本，只检查必要字段。
- 已存在的规格为 `status: approved` 时，不直接覆盖。比较新旧内容，报告人工字段变化和潜在冲突，等待用户确认。
- Schema 新增字段应优先保持向后兼容；不在本 Skill 第一版引入与当前 Appium PoC 无关的平台或框架字段。
