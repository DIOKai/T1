# 新增模型与 API 后端候选（2026-10-17）

本清单补充原有20条记录，原 README.md 与 catalog.json 不变。机器可读资料见 [catalog-additions-2026-10-17.json](catalog-additions-2026-10-17.json)。

| 类型 | 名称 | 用途 |
|---|---|---|
| API后端 | [deepseek-flash](https://api-docs.deepseek.com/quick_start/pricing/) | 当前版本快照V4.1-Flash，供日常任务评测 |
| API后端 | [deepseek-v4-pro](https://api-docs.deepseek.com/quick_start/pricing/) | 当前版本快照V4-Pro-0813，供复杂任务对照 |
| 本地权重候选 | [DeepSeek-OCR-2](https://huggingface.co/deepseek-ai/DeepSeek-OCR-2) | 扫描文档/图片OCR，保留页面来源 |
| 本地权重候选 | [Qwen3-Embedding-0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B) | 文档与代码向量检索 |
| 本地权重候选 | [Qwen3-Reranker-0.6B](https://huggingface.co/Qwen/Qwen3-Reranker-0.6B) | 召回后的候选重排 |

API两项为有费用的服务资料索引，保持未配置、未启用；不改变仓库免费工具规则，不创建账号、不充值、不发请求。别名与模型版本可能变化，使用前再查官方页面。

三个权重候选未下载、未运行。OCR-2发布者示例涉及NVIDIA/CUDA及自定义代码，不能假定Windows或当前硬件直接可用。Qwen两项与原有BGE作同一资料集的对照候选，不宣称必然更好；embedding更换需新建相容索引。

这些条目不能全部装进DeepSeek官方API，也不是五个已经安装的聊天模型。未增加新的本地推理服务或云供应商。
