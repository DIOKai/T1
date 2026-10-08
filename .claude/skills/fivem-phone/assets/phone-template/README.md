# phone-template：沉浸式 FiveM 手机模板（直板 / 书本折叠 / 翻盖 / 三折叠）

The fivem-phone skill's reference implementation. Copy it as the starting point for a new phone, or use it as the quality bar when reviewing a phone. Every interaction happens inside the phone (lock screen, control centre, settings, the edge you drag to unfold); nothing floats outside it.

## 有什么

- **6 种机型**（`config.lua` → `Config.Device`；玩家也能在 设置 → 手机型号 换，存在自己的 KVP）。比例按真机屏幕换算（`references/real-foldables.md`），游戏里用通用名字：
  | 代号 | 参考真机 | 合起来 | 打开 |
  |---|---|---|---|
  | `bar` | 一般直板手机 | 390×844 pt | — |
  | `passport` | iPhone Duo（2026） | 5.4" 宽短 | 7.6" 横向，两栏 |
  | `wide` | Galaxy Z Fold8 | 5.5" 10:16 | 7.6" 4:3，两栏 |
  | `tall` | Galaxy Z Fold8 Ultra | 6.5" 21:9 | 8" 近正方形，两栏 |
  | `flip` | Galaxy Z Flip8 | 4.1" 外屏（时钟、通知卡片、5 个固定 app） | 6.9" 长屏，中间横向折痕 |
  | `trifold` | Galaxy Z TriFold | 6.5" | 10" 三栏，先右后左两段展开动画 |
- **锁屏**：时间、日期、最新 3 条通知；点击、上滑、Enter 或 ↑ 解锁（`Config.LockScreen` 可关）。
- **控制中心**：点状态栏右边的信号/电量图标打开。里面有深色模式、勿扰（勿扰时不弹通知）、展开/合上、手机型号、手机大小。
- **折叠方式**：拖手机外侧的边缘（书本式和三折叠拖左边，翻盖拖上边），或点一下边缘、按 F、用控制中心。折叠时信息 app 选中的对话、打到一半的字、钱包表单都会保留。
- **主屏**：直板一页；书本式两页（左边小组件、右边 app）；三折叠三页（小组件 | app | 钱包余额、音乐）。底部 dock 打开时居中，图标避开折痕。
- **信息**：合起来时是列表↔对话；两栏是列表 | 对话；三栏是列表 | 对话 | 联系人资料，资料页的「转账」会打开钱包并自动填好号码。所有玩家文字都会转义（防 XSS）。
- **钱包**：余额、交易记录、转账（有确认步骤）。一栏和两栏时转账用底部面板，三栏时直接显示在第三栏。
- **设置**：深色模式、手机大小、手机型号、关于。
- 手机关着时来通知，会在右下角弹一个小横幅，不抢鼠标和键盘焦点。

## 安装

1. 复制到 `resources/[phone]/phone-template`（可以改名，代码里没有写死资源名）。
2. 需要 `ox_lib`。伺服器端会自动判断 `qbx_core` 或 `qb-core`。
3. `server.cfg`：`ensure ox_lib` 之后 `ensure phone-template`。
4. 进游戏按 **F1** 开手机（玩家可以在 GTA 设置 → 按键绑定 → FiveM 里改）。

## 浏览器预览（不用进游戏）

直接用 Chromium 打开 `web/index.html`，会用假资料运行，没有任何多出来的按钮。预览专用按键：**O** 开/关、**N** 模拟通知。截图用网址参数：`?device=trifold&fold=open&app=messages&thread=1&theme=light&sheet=1&unlock=1&cc=1&note=1`。

## 安全和性能（已经做好，改的时候别弄坏）

- 网页只送「意图」：转账只送号码和金额。伺服器检查金额（1 到 1,000,000 的整数）、号码格式、对方在线、不能转给自己、余额够不够（QBCore 银行默认可以变负数，所以要自己查）、频率限制，同一个玩家一次只能处理一笔；扣款成功、入账失败时会退回，并记录日志。
- 每个 NUI 回调都会回 `cb`；暂停菜单、死亡、上铐时自动关手机；`onResourceStop` 会删道具、停动作、释放焦点；打字时关掉 KeepInput，按 W 不会走路。
- 只动画 transform/opacity，闲着时没有任何动画，没有 `backdrop-filter`，手机关着时 `display:none`。
- 字体（Inter，OFL 授权）和图标（Lucide，ISC 授权）都打包在资源里，不连 CDN。授权见 `LICENSES.md`。

## 还要你自己接的（标了 TODO）

- `server.lua` 里的信息存储是示范（只放在内存）。要换成 oxmysql 资料表：对话、信息、交易记录，都按 citizenid 存。
- 拿手机的道具用原版 `prop_amb_phone`，没有会折的模型。要做会折的道具：Blender + Sollumz，动作用 `fivem-animation` 技能。
- 「相机、地图、车库……」这些 app 只是示范图标。新 app 照信息/钱包的写法加进 `RENDER`/`LOAD`，按 `panes()`（1/2/3）排版，内容不要压在折痕上。

## 已验证 / 未验证

- 已验证：在 Chromium 无头浏览器里截图检查 6 种机型（720p、1080p、1440p）；自动测试了解锁、拖边缘展开、折叠后对话和草稿还在、XSS；Lua 语法检查通过；用 `scripts/check_phone_app.py` 检查没有发现问题。
- 未验证：还没在真的 FiveM 客户端里跑过。FiveM 的 CEF 应该支持 `linear()` 缓动（不支持的话会自动退回 cubic-bezier），上服前在游戏里试一次：开关 10 次、折叠和展开、死亡、暂停菜单、重启资源。
