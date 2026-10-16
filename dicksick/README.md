# Dicksick — DeepSeek 專用 Skills

此資料夾獨立保存 17 個 DeepSeek Agent 用的 skills。原有 `.claude/skills`、`.agents/skills`、ori 與設定不變。來源固定為 T1 commit `7f975f4e20f9ba7c8e2cb9a70a7184c5b95ddf60`，原樣複製完整技能子目錄、參考檔、腳本、資料庫及 LICENSE/NOTICE；來源樹 SHA 見 SOURCES.json。

## 清單

- `prd`
- `create-implementation-plan`
- `ui-ux-pro-max`
- `impeccable`
- `expo-overview`
- `expo-project-structure`
- `expo-router`
- `expo-animation`
- `expo-native-ui`
- `expo-ui`
- `expo-design-system`
- `expo-data-fetching`
- `expo-upgrade`
- `expo-skill-feedback`
- `deepseek-app-integration`
- `maestro`
- `security-review`

## 使用方式

技能放在本資料夾下的 `.dsh/skills/`。如要獨立使用，把 dicksick 的內容複製到自己的 DeepSeek 專用工作區；不要在仍屬於 T1 Git 根目錄的子目錄啟動後就假定它會掃描這裡。DeepSeek Harness 的 projectRoot 以最近的 .git 為準，因此本庫根仍是 T1。

另一方式是在已安裝 Harness 的 filesystem skill provider，使用 customSkillDirs 指向這裡的絕對技能路徑。若要只掃描這套，按該版本文件使用 includeDefaultRoots=false 配合 customSkillDirs；本次不產生猜測的設定檔或改全域設定。

官方路徑文件：https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md

DeepSeek 網頁/API 本身不會載入 skills，需要 Agent 框架。這次沒有安裝 Harness、下載模型、呼叫 API、建立帳號、充值或啟用外部服務。

## 相容性

來源 skills 內容原樣保留，其中 Claude 專用工具與 `${CLAUDE_SKILL_DIR}`/`${SKILL_DIR}` 不會自動變成 DeepSeek 工具。執行前確認等價工具、將占位符映射到實際技能絕對路徑，不改原來源。impeccable 的 hooks/外部子代理沒有額外註冊，進階流程未驗證。Expo overview 可能引用未收錄技能；不代表已安裝。expo-skill-feedback 不自動送資料或開遙測。不要自動執行來源安裝、雲端或付費指令。

## 驗證界線

核對新增子樹與來源一致、技能清單完整，以及所有既有檔案不變。沒有實際 Harness/API/手機載入測試。此為檔案整理完成，不等於 DeepSeek 已在電腦啟用。
