# DeepSeek API 與 Skills 使用入口

## 已收錄技能

使用 [deepseek-app-integration](../.dsh/skills/deepseek-app-integration/SKILL.md)。完整技能和來源原樣保留，不另建同名副本。

它涵蓋後端保管 key、串流解析、工具呼叫、取消、錯誤分類、重試、每位使用者配額與成本控制。Skills 需要 Agent 讀取並配合實際工具執行，DeepSeek API 本身不會自動讀取 GitHub skills。

| 工作 | 配合技能 |
|---|---|
| 功能與驗收 | [prd](../.dsh/skills/prd/SKILL.md) |
| 開發步驟 | [create-implementation-plan](../.dsh/skills/create-implementation-plan/SKILL.md) |
| DeepSeek 接入 | [deepseek-app-integration](../.dsh/skills/deepseek-app-integration/SKILL.md) |
| 安全與權限 | [security-review](../.dsh/skills/security-review/SKILL.md) |
| 手機功能測試 | [maestro](../.dsh/skills/maestro/SKILL.md) |

## 官方 API 邊界

截至 2026-10-16，官方價目頁列出 OpenAI 格式 base URL `https://api.deepseek.com`，model ID `deepseek-flash` 對應 DeepSeek-V4.1-Flash，另列 `deepseek-v4-pro`。實作前重新讀當前模型頁，不將名稱/價格當永久設定。未寫入金鑰，未設定預設 paid provider，未執行 API 請求。

Chat Completions、Responses、Anthropic 相容介面參數和工具歷史規則不完全相同；先選端點再按對應文件實作，不僅替換 base URL。第三方 Hive 的 model ID、金鑰、串流與 billing 需另外適配，這裡不自動啟用 Hive。

## API 外圍開源工具（來源索引，尚未安裝）

| 工具 | 來源 | 用途與限制 |
|---|---|---|
| DeepSeek Harness | https://github.com/deepseek-ai/deepseek-harness | 執行 Agent 與讀取技能；不是模型權重 |
| LiteLLM | https://github.com/BerriAI/litellm | API 統一介面、routing、重試、用量；Hosted/Enterprise 與付費 provider 另計，不開啟未授權 fallback |
| Promptfoo | https://github.com/promptfoo/promptfoo | 用固定題目評估 prompts/agents/RAG；先用 mock，本機工具免費不代表模型評測呼叫免費 |
| LlamaIndex | https://github.com/run-llama/llama_index | 文件索引、檢索；不是把資料訓練進 DeepSeek，embedding/外部服務須另選 |

這些是工具倉庫，不假稱已有可直接載入的 SKILL.md 或已安裝插件。使用前核對當前授權與必要環境。

## 接入驗證順序

1. 讀既有 skill 與官方端點文件，核對預期輸入輸出及版本。
2. 無 key 用 mock 驗證 fragmented SSE、取消、401/402/429、部分輸出後斷線和無權限工具。
3. 只有憑證與費用已明確授權時，才做有上限的 live smoke test；金鑰只在服務端安全配置。
4. 報告通過證據及尚未驗證項目；不將靜態文件整理說成 API 已運作。

官方依據：
- https://api-docs.deepseek.com/quick_start/pricing/
- https://api-docs.deepseek.com/guides/tool_calls/
- https://api-docs.deepseek.com/guides/thinking_mode/
- https://api-docs.deepseek.com/quick_start/error_codes/
- https://api-docs.deepseek.com/quick_start/rate_limit/

模型目錄見 [20 個模型](../models/README.md)。來源技能和原有 T1 設定未修改。
