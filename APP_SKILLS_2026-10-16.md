# App 開發新增 Skills

本次只新增 17 個 skills 及其完整參考檔、腳本、原始授權。所有舊 skills、ori、CLAUDE.md、LESSONS.md、README.md、既有設定及安裝腳本保持原樣。

Claude 使用 `.claude/skills/`，Codex 經既有 `.agents/skills` symlink 讀同一份。此提交不等於安裝到任何電腦的全域 skills；本機需更新此倉庫後重新載入工作階段。

## 新增內容

- Expo：expo-overview、expo-project-structure、expo-router、expo-animation、expo-native-ui、expo-ui、expo-design-system、expo-data-fetching、expo-upgrade、expo-skill-feedback。
- 後端：supabase、supabase-postgres-best-practices。
- 效能：vercel-react-native-skills（上游來源目錄叫 react-native-skills，內容原樣）。
- 測試：webapp-testing（Web，不是原生手機 E2E）、swift-testing-expert。
- iOS：swiftui-expert-skill。
- 安全：security-review。

上游版本與來源見 `APP_SKILLS_IMPORT_2026-10-16.json`。原始內容不作改寫，既有倉庫規則仍優先：使用前取得授權；不啟用付費服務；不送出任何未獲授權的回饋、遙測或外部資料。expo-skill-feedback 僅保留為被其他 Expo skills 引用的文件，不自動執行。

## 尚未加入

EAS 付費服務 skills、Sentry 外部插件，以及授權未確認的 Better Auth 暫不加入。Expo overview 是上游完整路由表，會提及未安裝技能；不能當作它們已安裝，也不能自動下載或啟用。一般原生手機端到端測試仍待補齊。

## 驗證界線

已核對來源固定 commit、完整檔案清單、原始 blob 一致性、只新增無覆寫，以及 Codex/Claude 共用連結。沒有建置 App、執行上游腳本、安裝依賴、連接服務或測試 macOS Instruments。較新的 API 必須依實際 SDK 和系統版本核對。
