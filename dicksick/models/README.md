# 20 個模型目錄

這是之前選出的 20 個模型/尺寸版本，不是 20 個不同品牌，也不是最新排名。僅保存發布者連結與用途，沒有下載權重、執行模型或啟用推理供應商。不能把其他模型裝進 DeepSeek 官方 API；若選其他模型，須另外部署或連接相應供應商。

| # | 發布者模型頁 | 用途 |
|---|---|---|
| 1 | [Qwen/Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) | 輕量通用文字 |
| 2 | [Qwen/Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B) | 通用中文助手 |
| 3 | [Qwen/Qwen3-14B](https://huggingface.co/Qwen/Qwen3-14B) | 通用分析與文字 |
| 4 | [Qwen/Qwen3-32B](https://huggingface.co/Qwen/Qwen3-32B) | 大型通用推理 |
| 5 | [Qwen/Qwen3-30B-A3B](https://huggingface.co/Qwen/Qwen3-30B-A3B) | MoE 通用模型 |
| 6 | [Qwen/Qwen3-Coder-30B-A3B-Instruct](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct) | 程式開發與 Agent 任務 |
| 7 | [Qwen/Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct) | 輕量程式開發 |
| 8 | [Qwen/Qwen2.5-Coder-14B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-14B-Instruct) | 程式開發與除錯 |
| 9 | [Qwen/Qwen2.5-Coder-32B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct) | 大型程式任務 |
| 10 | [Qwen/Qwen3-VL-8B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct) | 圖片與文件理解 |
| 11 | [deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B) | 輕量推理實驗 |
| 12 | [deepseek-ai/DeepSeek-R1-Distill-Qwen-7B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B) | 數學與推理 |
| 13 | [deepseek-ai/DeepSeek-R1-Distill-Qwen-14B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B) | 較大型推理 |
| 14 | [deepseek-ai/DeepSeek-R1-Distill-Qwen-32B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B) | 大型推理 |
| 15 | [microsoft/Phi-4-mini-instruct](https://huggingface.co/microsoft/Phi-4-mini-instruct) | 輕量指令與推理 |
| 16 | [microsoft/phi-4](https://huggingface.co/microsoft/phi-4) | 文字、數學與邏輯 |
| 17 | [mistralai/Mistral-Small-3.1-24B-Instruct-2503](https://huggingface.co/mistralai/Mistral-Small-3.1-24B-Instruct-2503) | 文字與圖片理解 |
| 18 | [mistralai/Mistral-7B-Instruct-v0.3](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3) | 通用文字 |
| 19 | [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) | 文件向量化與檢索 |
| 20 | [BAAI/bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3) | 搜尋結果重排 |

## 選型建議

先維持 DeepSeek 官方 API 作主力候選。本地寫碼可先評估 Qwen2.5-Coder-7B；通用文字可先評估 Qwen3-8B；文件知識庫可評估 BGE-M3 + BGE-reranker-v2-m3。這是待實測建議，不是效能保證。

BGE embedding 與 reranker 不是聊天模型，也不能僅靠改 chat/completions 的 model 名稱就接入。R1 蒸餾版不等於官方線上完整 DeepSeek 模型。A3B 指啟用參數，不代表只需載入 3B 權重。

這批是可下載權重候選，不把它們全部宣稱符合嚴格開源 AI 定義。使用前核對該發布版本的 LICENSE、基底模型條款、量化來源、SDK 支援、RAM/VRAM、上下文與商用限制。不因下載免費就假設雲端運算或 API 免費。未驗證各模型在用戶硬體上的可運行性。

機器可讀資訊見 catalog.json。GitHub 中不放 `.safetensors`、GGUF 等大型權重；需要時在明確選定模型與目的地後另外下載。
