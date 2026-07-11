# 转换与门禁示例

## 目录

- CASE00：可重复、非破坏性
- CASE01：高质量但破坏性
- 低质量输入：阻塞

## CASE00：可重复、非破坏性

来源：`appium_auto/cases/CASE00-进入设备详情页并查看设备信息`

### 原始文本

```text
CASE00：进入设备详情页并查看设备信息

前置条件：
设备已经与智能生活 App 配网；
设备名称是 V4#4；
设备当前在线；
用户已经登录。

步骤：
启动智能生活 App；
在首页找到名称为 V4#4 的设备；
如果当前屏幕没有显示设备，则滚动设备列表；
点击 V4#4 设备卡片。

预期结果：
成功进入设备详情页；
页面显示设备相关信息；
页面存在温度区域；
页面存在湿度区域。

然后继续：
点击右上角修改图标。

预期结果：
成功进入高级设置页；
页面存在“移除设备”按钮。

最后：
返回设备详情页；
返回首页。

预期结果：
首页仍然存在 V4#4；
用例结束以后，设备和账号状态没有被修改。
```

### 质量报告

```yaml
quality_gate:
  score: 98
  grade: "A"
  gate_status: "passed"
  dimensions:
    objective_and_scope: { score: 10, max_score: 10, reason: "详情页和设备信息验证目标明确。" }
    preconditions: { score: 15, max_score: 15, reason: "配网、设备名、在线和登录状态完整。" }
    steps: { score: 25, max_score: 25, reason: "进入、查看、设置和返回顺序完整。" }
    action_and_target_clarity: { score: 14, max_score: 15, reason: "业务对象明确；修改图标的 locator 留给后续探索。" }
    expected_results: { score: 24, max_score: 25, reason: "温湿度区域、移除设备按钮和最终状态均可观察。" }
    repeatability_and_recovery: { score: 10, max_score: 10, reason: "结束后设备、账号和绑定状态不变。" }
  hard_blockers: []
  warnings: []
  missing_info: []
  review_questions: []
  automation_ready: true
```

### 标准 YAML

```yaml
schema_version: "1.0"
status: "draft"

quality_gate:
  score: 98
  grade: "A"
  gate_status: "passed"
  automation_ready: true
  dimensions:
    objective_and_scope: { score: 10, max_score: 10, reason: "详情页和设备信息验证目标明确。" }
    preconditions: { score: 15, max_score: 15, reason: "配网、设备名、在线和登录状态完整。" }
    steps: { score: 25, max_score: 25, reason: "进入、查看、设置和返回顺序完整。" }
    action_and_target_clarity: { score: 14, max_score: 15, reason: "业务对象明确；修改图标的 locator 留给后续探索。" }
    expected_results: { score: 24, max_score: 25, reason: "关键结果可观察。" }
    repeatability_and_recovery: { score: 10, max_score: 10, reason: "结束后关键状态不变。" }
  hard_blockers: []
  warnings: []

id: "CASE00"
name: "进入设备详情页并查看设备信息"
description: "验证已绑定且在线的 V4#4 可进入详情页和高级设置页，并在返回首页后保持原状态。"
module: "设备"
priority: ""
tags: []

execution:
  repeatable: true
  destructive: false
  manual_setup_required: false
  manual_cleanup_required: false
  default_regression_enabled: true

preconditions:
  - "设备已经与智能生活 App 配网"
  - "设备名称为 V4#4"
  - "设备当前在线"
  - "用户已经登录"

test_data:
  device_name: "V4#4"

steps:
  - id: 1
    action: "启动"
    target: "智能生活 App"
    value: ""
    value_ref: ""
    expected: []
  - id: 2
    action: "查找，必要时滚动"
    target: "首页设备列表中名称为 V4#4 的设备"
    value: ""
    value_ref: ""
    expected: []
  - id: 3
    action: "点击"
    target: "名称为 V4#4 的设备卡片"
    value: ""
    value_ref: ""
    expected:
      - "进入设备详情页"
      - "页面显示设备相关信息"
      - "页面存在温度区域"
      - "页面存在湿度区域"
  - id: 4
    action: "点击"
    target: "设备详情页右上角修改图标"
    value: ""
    value_ref: ""
    expected:
      - "进入高级设置页"
      - "页面存在“移除设备”按钮"
  - id: 5
    action: "返回"
    target: "设备详情页"
    value: ""
    value_ref: ""
    expected: []
  - id: 6
    action: "返回"
    target: "首页"
    value: ""
    value_ref: ""
    expected:
      - "首页仍然存在 V4#4"

expected:
  - "用例结束后设备和账号状态没有被修改"
cleanup: []
missing_info: []
review_questions: []
source_file: "appium_auto/cases/CASE00-进入设备详情页并查看设备信息"
source_text: |
  CASE00：进入设备详情页并查看设备信息

  前置条件：

  设备已经与智能生活 App 配网；
  设备名称是 V4#4；
  设备当前在线；
  用户已经登录。

  步骤：

  启动智能生活 App；
  在首页找到名称为 V4#4 的设备；
  如果当前屏幕没有显示设备，则滚动设备列表；
  点击 V4#4 设备卡片。

  预期结果：

  成功进入设备详情页；
  页面显示设备相关信息；
  页面存在温度区域；
  页面存在湿度区域。

  然后继续：

  点击右上角修改图标。

  预期结果：

  成功进入高级设置页；
  页面存在“移除设备”按钮。

  最后：

  返回设备详情页；
  返回首页。

  预期结果：

  首页仍然存在 V4#4；
  用例结束以后，设备和账号状态没有被修改。
```

结论：该用例可重复、非破坏性、不需要重新配网，未生成 locator，也没有扩展测试范围，可以进入 Appium 自动化流程。

## CASE01：高质量但破坏性

来源：`appium_auto/cases/CASE01删除设备成功.txt`

原始用例明确选择“解除绑定”并验证首页不再存在 V4#4。当前项目规划进一步明确：成功后设备解除绑定，下一次执行前需要人工重新配网，因此不进入默认重复回归。该恢复约束来自项目规划，不冒充原始用例正文。

### 原始文本

```text
前置条件：
1、设备已经和涂鸦的智能生活app配网成功，
2、设备当前在线,在智能生活app里名称是"V4#4"

操作步骤和预期结果
1、进入手机的智能生活app，找到名称为"V4#4"的设备。如果找不到，向上划一下，把列表下面的设备显示在屏幕上
预期结果：智能生活app，有名称为"V4#4"的设备
2、点击名称为"V4#4"的设备卡片
预期结果：进入详情页，展示设备的信息，例如温度，湿度
3、点击右上角的修改图标
预期：进入高级设置页面，页面底部有"移除设备"按钮
4、点击底部的"移除设备"按钮
预期结果：底部出来抽屉，有2个按钮，分别是"解除绑定"、"解绑并清除数据"
5、点击"解除绑定"按钮
预期结果：页面转圈，随后回到智能生活首页。首页上下滑动，确认没有名称为"V4#4"的设备。
```

### 质量报告

```yaml
quality_gate:
  score: 95
  grade: "A"
  gate_status: "passed"
  dimensions:
    objective_and_scope: { score: 10, max_score: 10, reason: "删除指定设备的目标明确。" }
    preconditions: { score: 13, max_score: 15, reason: "配网、在线和设备名称明确；登录态未在原文单独说明。" }
    steps: { score: 25, max_score: 25, reason: "进入详情、打开设置、选择解绑和验证删除顺序完整。" }
    action_and_target_clarity: { score: 15, max_score: 15, reason: "设备和两个解绑选项区分明确。" }
    expected_results: { score: 24, max_score: 25, reason: "页面流转和首页无设备均可观察。" }
    repeatability_and_recovery: { score: 8, max_score: 10, reason: "项目规划已明确需人工重新配网并关闭默认回归。" }
  hard_blockers: []
  warnings:
    - "该用例解除设备绑定，执行后必须人工重新配网才能再次运行。"
  missing_info: []
  review_questions: []
  automation_ready: true
```

### 标准 YAML

```yaml
schema_version: "1.0"
status: "draft"

quality_gate:
  score: 95
  grade: "A"
  gate_status: "passed"
  automation_ready: true
  dimensions:
    objective_and_scope: { score: 10, max_score: 10, reason: "删除指定设备的目标明确。" }
    preconditions: { score: 13, max_score: 15, reason: "关键设备状态明确。" }
    steps: { score: 25, max_score: 25, reason: "操作顺序完整。" }
    action_and_target_clarity: { score: 15, max_score: 15, reason: "操作对象和选项明确。" }
    expected_results: { score: 24, max_score: 25, reason: "结果可观察。" }
    repeatability_and_recovery: { score: 8, max_score: 10, reason: "人工恢复与回归限制明确。" }
  hard_blockers: []
  warnings:
    - "执行后设备解除绑定，下一次运行前需要人工重新配网。"

id: "CASE01"
name: "删除设备成功"
description: "从高级设置中解除 V4#4 的绑定，并验证首页不再显示该设备。"
module: "设备"
priority: ""
tags: []

execution:
  repeatable: false
  destructive: true
  manual_setup_required: true
  manual_cleanup_required: true
  default_regression_enabled: false

preconditions:
  - "设备已与智能生活 App 配网成功"
  - "设备当前在线"
  - "设备名称为 V4#4"

test_data:
  device_name: "V4#4"

steps:
  - id: 1
    action: "进入并查找，必要时向上滚动"
    target: "智能生活 App 首页中名称为 V4#4 的设备"
    value: ""
    value_ref: ""
    expected:
      - "首页存在名称为 V4#4 的设备"
  - id: 2
    action: "点击"
    target: "名称为 V4#4 的设备卡片"
    value: ""
    value_ref: ""
    expected:
      - "进入详情页"
      - "页面展示温度、湿度等设备信息"
  - id: 3
    action: "点击"
    target: "设备详情页右上角修改图标"
    value: ""
    value_ref: ""
    expected:
      - "进入高级设置页"
      - "页面底部存在“移除设备”按钮"
  - id: 4
    action: "点击"
    target: "移除设备按钮"
    value: ""
    value_ref: ""
    expected:
      - "底部抽屉显示“解除绑定”和“解绑并清除数据”两个按钮"
  - id: 5
    action: "点击"
    target: "解除绑定按钮"
    value: ""
    value_ref: ""
    expected:
      - "页面显示处理中状态，随后返回智能生活首页"
      - "上下滚动首页后不存在名称为 V4#4 的设备"

expected:
  - "V4#4 已解除绑定"
cleanup:
  - "下一次执行前人工重新配网并恢复名称为 V4#4 的在线设备"
missing_info: []
review_questions: []
source_file: "appium_auto/cases/CASE01删除设备成功.txt"
source_text: |
  前置条件：
  1、设备已经和涂鸦的智能生活app配网成功，
  2、设备当前在线,在智能生活app里名称是"V4#4"

  操作步骤和预期结果
  1、进入手机的智能生活app，找到名称为"V4#4"的设备。如果找不到，向上划一下，把列表下面的设备显示在屏幕上
  预期结果：智能生活app，有名称为"V4#4"的设备
  2、点击名称为"V4#4"的设备卡片
  预期结果：进入详情页，展示设备的信息，例如温度，湿度
  3、点击右上角的修改图标
  预期：进入高级设置页面，页面底部有"移除设备"按钮
  4、点击底部的"移除设备"按钮
  预期结果：底部出来抽屉，有2个按钮，分别是"解除绑定"、"解绑并清除数据"
  5、点击"解除绑定"按钮
  预期结果：页面转圈，随后回到智能生活首页。首页上下滑动，确认没有名称为"V4#4"的设备。
```

结论：破坏性不等于低质量。恢复影响和方式已明确，因此可生成 YAML 并进入受控自动化，但不能进入默认连续回归。

## 低质量输入：阻塞

### 原始文本

```text
打开 App，测试设备功能。
```

### 质量报告

```yaml
quality_gate:
  score: 19
  grade: "D"
  gate_status: "blocked"
  dimensions:
    objective_and_scope: { score: 2, max_score: 10, reason: "未说明具体设备功能和验证目标。" }
    preconditions: { score: 2, max_score: 15, reason: "未说明必要的账号、设备或开始状态。" }
    steps: { score: 5, max_score: 25, reason: "只有打开 App，缺少具体测试操作。" }
    action_and_target_clarity: { score: 4, max_score: 15, reason: "设备和功能均不明确。" }
    expected_results: { score: 0, max_score: 25, reason: "没有可观察的预期结果。" }
    repeatability_and_recovery: { score: 6, max_score: 10, reason: "未说明是否修改设备状态。" }
  hard_blockers:
    - "无法判断具体测试目标。"
    - "关键测试对象未知。"
    - "没有任何可验证的预期结果。"
  warnings: []
  missing_info:
    - "要验证的设备或功能"
    - "具体操作步骤"
    - "代表成功的可观察结果"
  review_questions:
    - "需要验证哪个设备或哪项功能？"
    - "用户需要依次执行哪些操作？"
    - "什么页面、数据或设备状态代表测试成功？"
  automation_ready: false
```

结论：不生成正式 YAML，不调用 Appium MCP，不生成 Appium 脚本；等待用户补充后重新评价。
