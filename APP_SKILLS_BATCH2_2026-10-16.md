# 第二批 App 開發 Skills

本次只新增以下 9 個 skills，沒有修改舊 skills、ori、設定或安裝腳本。Claude 從 `.claude/skills/` 讀取；Codex 透過既有 `.agents/skills` 連結共用同一份。

| Skill | 來源 | 用途 |
|---|---|---|
| prd | github/awesome-copilot，MIT | 需求文件、使用故事、驗收標準 |
| create-implementation-plan | github/awesome-copilot，MIT | 實作步驟、依賴、驗證計畫 |
| maestro | TerminalSkills/skills，Apache-2.0 | 手機 UI 自動化測試；社群指引 |
| testing-setup | android/skills，Apache-2.0 | Android 測試策略與設定 |
| adaptive | android/skills，Apache-2.0 | Compose 自適應介面 |
| jetpack-compose-performance | android/skills，Apache-2.0 | Compose 重組與渲染效能 |
| android-intent-security | android/skills，Apache-2.0 | Intent 安全 |
| android-permissions-security | android/skills，Apache-2.0 | Android 權限安全 |
| android-profiler | android/skills，Apache-2.0 | CPU、記憶體、卡頓與 Perfetto 分析 |

## 使用與限制

- 原始 skill 及參考檔案保持上游內容，固定來源 commit 和 blob 見 `APP_SKILLS_BATCH2_IMPORT_2026-10-16.json`。
- 僅加入技能資料，不等於已在電腦安裝 Maestro、Java、Android SDK 或模擬器。使用前按既有倉庫規則取得授權。
- Maestro 本機 CLI 與付費 Cloud 有區別；不啟用付費 Cloud。此 skill 的 iOS 路線是模擬器，並非實體 iPhone。應以實際安裝版本和官方文件重新核對平台支援。
- android-profiler 內含 Perfetto 下載啟動腳本（保留來源 executable mode），本次未執行。日後執行會依平台下載並校驗工具，必須先核對環境及使用授權。
- Android skills 可能要求新增測試、安裝依賴或調整產品專案；本次僅收錄，不對任何產品專案執行這些操作。
- 未把 YouTube 影片或一般官方文件冒充成可安裝 skill。DeepSeek、離線同步、推播、多語言仍按實際功能需求補齊。
- 這些是原樣導入，部分 SKILL.md 超過 8 KB；不為縮短而改寫上游。不同代理版本的載入限制需使用時驗證。

## 驗證

上游檔案 SHA、完整相依檔案清單、授權、同名衝突、只新增及原有連結。沒有實際執行手機測試或量測 App 效能。
