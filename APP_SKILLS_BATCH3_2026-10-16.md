# 第三批：5 個自訂 App 工作流程 Skills

新增 deepseek-app-integration、mobile-offline-sync、mobile-notifications-background、mobile-release-readiness、mobile-purchases-subscriptions。每個包含 SKILL.md、Codex UI metadata 和官方來源清單。Claude/Codex 沿用原有共用目錄連結。所有既有檔案、舊 skills、ori、設定和安裝腳本保持不變。

這是 T1 自訂流程，並非 DeepSeek/Expo/PowerSync/Apple/Google 官方 skills 的原樣複製。依先前研究及官方文件編寫，沒有整包導入 PowerSync 或 RevenueCat，也沒有自動安裝或啟用服務。PowerSync 已有官方 skill；需要時讀官方來源，不假稱已安裝。

## 驗證結果與界線

- 5 個 skills 的名稱、frontmatter、Codex metadata、檔案大小（每個 SKILL.md 小於 8KB）、相對引用、重複路徑及 placeholder 檢查通過。
- 官方 quick_validate.py 因環境缺少 PyYAML 且 PyPI 無法連線，未能執行；改以 Python 標準庫檢查本批使用的嚴格 YAML 子集（純量名稱及 JSON quoted 字串），不宣稱官方驗證器通過。
- 獨立文件情境審查涵蓋：部分串流失敗、伺服器已寫入後逾時與切換帳號、背景任務準時誤解、資料庫備份缺檔案、pending 購買與重複通知。
- 未執行 API 付費請求、手機/模擬器、資料庫恢復或 sandbox 付款。這些情境是流程文件審查，不是實作測試。
- 官方來源為 API/規則依據；實作時重新核對當前 SDK、端點、商店規則與服務方案。YouTube 僅核對介紹/章節，未完整觀看。
- DeepSeek 技能不新增金鑰、不充值、不更改 Codex/Claude 模型設定；用戶本次僅授權寫入 skills。
