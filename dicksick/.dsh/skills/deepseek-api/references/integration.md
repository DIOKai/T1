# 协议与参数

资料核验：2026-10-17。下面是核验快照，执行时重新核对。

## 选协议

| 路径 | 用途 | 鉴权及区别 |
|---|---|---|
| OpenAI 格式，base URL https://api.deepseek.com | Chat Completions | Bearer Key；特有字段不能直接套用另一家 API 的语义 |
| Anthropic 格式，base URL https://api.deepseek.com/anthropic | Messages | x-api-key；SDK 拼接路径与直接 HTTP 写法不同，防止重复 /v1 |
| Beta，base URL https://api.deepseek.com/beta | Prefix/FIM 等指定功能 | 以对应功能说明为准，不作为所有请求的默认地址 |

Anthropic 相容接口由 DeepSeek 直接提供，无须先安装网关。相容不意味着 MCP、缓存标记或每种内容块都受到支持；检查兼容矩阵。尽量显式使用 DeepSeek 模型名，避免依赖 Claude 名称的隐式路由。

[首次调用](https://api-docs.deepseek.com/) · [Anthropic 兼容](https://api-docs.deepseek.com/guides/anthropic_api/) · [Prefix](https://api-docs.deepseek.com/guides/chat_prefix_completion/) · [FIM](https://api-docs.deepseek.com/guides/fim_completion/)

## 思考模式的版本合同

核验时默认启用思考；canonical effort 为 low/high/max。直接 API 的 xhigh 映射为 high，而 AI SDK 当前文档将 xhigh 映射为 max。应用应传 canonical 值并检查实际出站数据；不要把适配器规则复制为服务端规则。

temperature 在思考模式不生效。top_p 则必须按模型和模式分别检查；Flash 当前在思考模式支持受限范围，Pro 的规则不同。SDK 可能先过滤字段并返回警告，这不等于服务端不支持该字段。

带 tools 的思考请求要在后续历史中保留完整 reasoning_content，包括未发生工具调用的历史轮次；无 tools 时历史 reasoning_content 会被忽略。将所需字段作为受控的协议数据处理，用户界面与普通日志不默认展示或持久化推理内容。

[官方思考说明](https://api-docs.deepseek.com/guides/thinking_mode/) · [AI SDK 适配器](https://ai-sdk.dev/providers/ai-sdk-providers/deepseek)

## 模型与身份

当前价格表列出 deepseek-flash 和 deepseek-v4-pro。前者是随版本变化的别名。使用前检查模型版本、上下文、输出上限和功能；模型卡的本地部署建议不能自动套用托管 API。

user_id 是不含个人信息的业务标识；当前官方约束为字母、数字、下划线、连字符且最长512字符。OpenAI 格式、Anthropic metadata 和 SDK 的 userId 字段位置不同。稳定的租户隔离比跨用户缓存复用优先。

[模型表](https://api-docs.deepseek.com/quick_start/pricing/) · [用户隔离](https://api-docs.deepseek.com/quick_start/rate_limit/)

中英文文档在未知模型名回退、top_p 等处可能不同步。记录差异，选择显式模型名与最小参数；必要时在已授权环境验证，不自行认定两份文档等价。
