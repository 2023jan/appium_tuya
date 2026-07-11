# 第二阶段框架化提取计划

## 目标

把第一阶段 PoC 整理成可维护的 Appium 自动化框架。

## 计划重点

- driver 创建和 capabilities 管理。
- base page 页面基类和 locator 约定。
- 显式等待工具。
- 通用手势。
- 权限弹窗和普通弹窗处理。
- 诊断产物收集。
- 测试数据管理。
- 环境配置。

## 进入条件

- 第一阶段已经有至少一个稳定生成脚本。
- 生成脚本已经至少成功执行 1 次验证。
- 已经理解目标 App 的常见启动流程。

## 环境配置约定

- `appium_auto/config/default.yaml` 保存可提交的公共默认值。
- `appium_auto/config/local.yaml` 保存当前手机、App 和 IoT 设备覆盖值，并由 Git Ignore 排除。
- `appium_auto/config/wifi.local.yaml` 单独保存真实 Wi-Fi SSID 和密码，并由 Git Ignore 排除。
- 配置优先级为默认配置、本机覆盖、运行时环境变量。
- CASE00-02 不读取 Wi-Fi 配置，后续 CASE03 再接入。

## 公共代码边界

- pytest fixture 负责环境加载、driver 创建和 Appium Server 生命周期。
- `BasePage` 只提供定位和显式等待等页面基础能力。
- Page Object 负责单页面 locator、操作和断言。
- 设备生命周期 Flow 负责详情、解绑和重新配网等跨页面业务流程。
- 运行上下文负责日志、证据和失败步骤，敏感页面可以关闭 UI 证据采集。

## 退出条件

- 新测试可以复用 driver 和诊断工具。
- 至少存在两个常用页面的 page object。
- 第二条测试用例可以用比第一阶段更少的重复代码创建。

