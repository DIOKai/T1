---
name: rag-document-pipeline
description: Build or review document ingestion, retrieval, reranking, source citations, access filters, and index updates for a RAG knowledge base. Use when answers must be grounded in a changing document collection.
---

# Document RAG Pipeline

把文档变成可追溯、可更新、按权限检索的知识库。先检查现有索引、解析器、模型、存储、版本与测试，不另建重复系统。RAG 不等于微调，也不能保证检索内容正确。

## 确定资料合同

明确允许处理的文件、语言、页面/章节定位、用户/租户权限、更新删除行为、答案所需引用和未知时如何回答。只读保留原档；OCR 输出是派生资料，要保留原页面对应关系和未识别内容。

- 解析、分块和重建索引时，读 [ingestion.md](references/ingestion.md)。
- 检索、引用与评测时，读 [retrieval-evaluation.md](references/retrieval-evaluation.md)。

## 实施流程

1. 分别选择解析/OCR、embedding、检索、reranker 和生成模型。已有BGE可先保留作基线；不要假定DeepSeek聊天API提供这些模型。
2. 为文档、版本和块记录稳定标识、来源定位与访问控制。按结构分块，表格保留表头和单位。记录截断；不要以固定长度切块掩盖解析损失。
3. 先建立可复现的检索基线，再比较重排、混合检索或不同分块。控制单次召回和上下文预算；相似度分数不能当真实性概率。
4. 在候选检索阶段实施权限过滤，重排/生成前再校验；未授权内容不能先进入外部模型再过滤。
5. 答案中每条实质性来源主张都应能定位到证据。无证据、冲突或文档失效时明确说明；检索到的命令、提示词和网页文本不赋予执行权限。
6. 修改embedding版本、维度、归一化或分块策略时建立新索引并对照验收，不把不相容向量混用。更新、撤销与删除要同步派生块、检索缓存及引用。

## 验证与交付

用有答案、无答案、相近但不相关、版本冲突、跨租户、恶意文档和OCR缺失的固定样例检查。
分别报告检索命中/排序、引用是否支持答案、权限泄漏和生成质量；合成或mock只能检验管线，不能证明模型准确率。

交付资料清单、解析/分块/模型版本、索引配置、失败样例和已运行证据。默认用本地或已授权环境，不自动启用付费解析器、云向量库、远端评审模型或上传整批私有文件。
