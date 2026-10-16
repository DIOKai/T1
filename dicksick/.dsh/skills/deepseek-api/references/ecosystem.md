# SDK、网关与代理框架

## Bifrost

[GitHub 提供方文档](https://github.com/maximhq/bifrost/blob/dev/docs/providers/supported-providers/deepseek.mdx)说明默认走 OpenAI 格式，也可通过 use_anthropic_endpoints 改用 Anthropic 格式；alias 可覆盖 key 层设置。dev 是移动分支，实施时记录所用 release/commit。

该适配器会按端点及强制 tool_choice 组合关闭 thinking，也可能过滤额外字段。测试实际出站参数和多轮历史，不能只看调用方 JSON。其 Responses 路由可能是协议转换；提供方支持不等于网关也支持。计价数据表也可能落后于供应商。

## AI SDK

[官方 DeepSeek 适配器](https://ai-sdk.dev/providers/ai-sdk-providers/deepseek)。
读取项目 ai 与 @ai-sdk/deepseek 的版本、providerOptions、归一化 usage 和 warnings；区分通用参数与 DeepSeek 专用参数。适配器对 effort、采样参数及历史的处理不能等同于原始 API。明确使用官方直连还是 Gateway。

## Pydantic AI

[DeepSeek 提供方文档](https://pydantic.dev/docs/ai/models/deepseek/) · [GitHub](https://github.com/pydantic/pydantic-ai)。
先采用该版本支持的 DeepSeek provider/model 接法，再核查输出验证、工具历史和思考字段。不要因使用 Pydantic 类型就声称服务端严格遵守任意 Schema。验证和模型重试都应受总预算约束；不要套用其他提供方默认行为。

当前文档说明：deepseek: 前缀选择 Chat Completions；Responses 要显式选对应模型类。思考模式与强制输出工具存在限制，结构化输出可靠性需单独验收。不要通过 previous_response_id 省略历史，除非所用服务明确支持服务器侧会话。以上均需与安装版本和实际端点匹配。

## DeepSeek Harness

[官方仓库](https://github.com/deepseek-ai/deepseek-harness)。
这是独立的插件式代理框架，基于 Cordis，当前仍标明 developer preview。研究其会话、凭据、工具和权限组件时固定版本；不把某个预览版本端口、profile 或包版本写成长期契约。

与 Claude Code、Codex 比较时按模型后端、会话、工具、权限、隔离、持久化、测试与运行环境逐项比较。协议兼容不等于整个产品功能兼容，使用某个客户端名称也不代表由该厂商模型生成。仅研究 Harness 不会自动赋予安装、启动或切换全局后端的授权。
