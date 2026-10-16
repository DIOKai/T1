# 架构背景与学习资料

架构资料仅在解释模型内部时读取；普通接入不需要加载参数规模、训练或基准表。

## 官方模型卡

- [DeepSeek-V4-Pro](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro)：原始 V4 模型家族、MoE、CSA/HCA、mHC、训练与本地部署说明。
- [DeepSeek-V4.1-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash)：更新后的 Flash 架构资料。

原始 V4 中 Pro 总参数1.6T、激活49B，Flash 总参数284B、激活13B；这是特定发布模型的说明，不应直接标记为所有当前线上模型规格。“两档模型”与“混合注意力结构”是两个概念。

本地权重的 KV 内存压缩、API 磁盘缓存和请求计费是不同层次；论文的缓存节省比例不能直接当 API 折扣或用户命中率。模型卡中 Think Max 的384K建议针对本地上下文设置，不要求 API 用户把每次输出预算设为384K。

## YouTube 辅助学习

以下只核对到了页面搜索元数据、简介与章节，没有取得完整字幕或逐帧观看。仅供进一步学习，不作为 API 契约依据。

1. [DeepSeek v4 in 4 Minutes — Developers Digest](https://www.youtube.com/watch?v=Oi6pQmGjH7Y)，2026-04-25。简介涉及发布、注意力、长上下文与成本；快速了解背景，价格和模型名应另查。
2. [DeepSeek V4 Architecture Explained - Tutorial — Vuk Rosić](https://www.youtube.com/watch?v=RVk4fCHbxjI)，2026-04-24。简介涉及 MoE、压缩注意力、mHC、Muon 与低精度；偏架构，不替代集成文档。

采用视频中的具体做法前，检查完整内容、示例依赖和发布日期，并用官方来源或小范围试验验证。没有读到字幕就不能声称视频证明了某条技术结论。
