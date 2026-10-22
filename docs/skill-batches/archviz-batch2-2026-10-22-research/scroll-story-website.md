# scroll-story-website 研究笔记

研究日期：2026-10-22。每条事实后附来源 URL。**未验证** = 只有二手/社区来源、经验值，或我没读到官方原文。**付费** = 要钱，用之前先问用户。

背景（用户看的 reels）：洗车/贴膜店的小商家网站，滚动时像电影一样播放一段画面（脏车变干净、镜头推到车标、光扫过车漆），颜色/膜色选择器（"Try it on"），右边滑出的预约面板（"30 秒预约"），商家收到短信，客户资料进后台表格。卖家一个站收 ~$900。

---

## 1. 动画库授权

### GSAP + ScrollTrigger
- gsap.com/pricing："100% free for all users, thanks to Webflow's support"，列出的插件包括 ScrollTrigger、ScrollSmoother、SplitText、MorphSVG、DrawSVG、Flip、Inertia 等全部插件。https://gsap.com/pricing/
- 授权是 "Standard 'No Charge' GSAP License"：允许在任何网站、web app 上使用（含商业）；**禁止**把 GSAP 用在"让用户不写代码做视觉动画、与 Webflow 动画构建器竞争"的工具里（要 Webflow 书面同意）。给商家做网站不受影响。
  - 文本镜像：https://open.windriver.com/info/uni-license-list/licenses/gsap-standard-no-charge-2025.html 、https://scancode-licensedb.aboutcode.org/gsap-standard-no-charge-2025.html
  - Webflow 公告：https://webflow.com/blog/gsap-becomes-free
  - gsap.com/community/standard-license/ 页面我抓到的内容里没有条文原文（只看到 "GSAP is now free for everyone"），条文来自上面的镜像 → **部分未验证**，交付前让用户看一眼官方条文。
- 用法：CDN 要锁版本（如 `gsap@3.x.y`），本技能模板默认**不用** GSAP，原生 JS 就能做；需要复杂时间线时再加。

### 原生 CSS scroll-driven animations（`animation-timeline: scroll()/view()`）
- MDN：**Limited availability，不是 Baseline**。https://developer.mozilla.org/en-US/docs/Web/CSS/animation-timeline
- Chrome/Edge 115+（2023-07）；Safari 26（2025-09），26.4 加了线程化，26.5（2026-06）修了 progress 精度 bug；Firefox 152（2026-06）稳定版仍在 flag `layout.css.scroll-driven-animations.enabled` 后面，Interop 2026 重点项；caniuse 全球 ~82.6%。来源是一篇博客 https://www.buildmvpfast.com/blog/css-scroll-driven-animations-replace-js-2026 → **未验证**（MDN 兼容表没抓到）。
- 结论：只拿来做**装饰性**的淡入/位移，用 `@supports (animation-timeline: view())` 包起来，默认样式要是"已显示"状态，不然 Firefox 用户会看到 opacity:0 卡住。画布帧序列仍用 JS。

### Lenis 平滑滚动
- MIT 授权，版本 1.3.27（README 安装片段）。默认 `respectReducedMotion: true`；不支持 CSS scroll-snap；iframe 上失效；Safari 限 60fps、低电量 30fps。https://github.com/darkroomengineering/lenis
- 结论：可选。平滑滚动不是必要的，小商家站默认不加（多一个依赖、手机上用户常觉得"滑不动"）。

---

## 2. 画布帧序列（Apple 产品页做法）

- CSS-Tricks 经典做法：148 张 JPEG，`<canvas>` 固定在视口，body 约 5 倍视口高，progress = scrollTop / 最大滚动距离 → `Math.floor(progress * frameCount)`，在 `requestAnimationFrame` 里画；全部用 `new Image()` 预载；慢网络给一张静态图。https://css-tricks.com/lets-make-one-of-those-fancy-scrolling-animations-used-on-apple-product-pages/
- 手机内存：解码后的位图 = 宽 × 高 × 4 字节（1280×720 ≈ 3.7 MB/帧，120 帧 ≈ 440 MB）——这是标准计算，不同浏览器的实际占用**未验证**。WebKit bug 讨论：大画布/漏画布是 iOS 崩溃常见原因，createImageBitmap 在旧 iOS 有内存不释放的报告。https://bugs.webkit.org/show_bug.cgi?id=172533 、https://www2.webkit.org/show_bug.cgi?id=229825
- 经验值（**未验证**，社区常用）：
  - 帧数 60–150；桌面 1280–1920 宽，手机单独一套 720–960 宽。
  - WebP 质量 70–80，单帧 30–80 KB；整段 3–8 MB。AVIF 更小但解码慢，帧序列用 WebP 更稳。
  - 先加载第 1 帧（当 LCP 图），再按"每隔 N 帧"粗到细加载，用户先滚也有画面。
  - 画布尺寸按 `devicePixelRatio` 但上限 2，避免超大画布。
  - 不在 scroll 事件里画，只记录目标帧，rAF 里画；同一帧不重画。
- 替代：一段 `<video>` 用 `currentTime` 跟着滚动（要每帧关键帧 `ffmpeg -g 1`，否则拖动卡）；文件更小但 iOS Safari 拖动 seek 不顺 → **未验证**，模板用图片序列。

## 3. 免费做帧序列
- Blender：`archviz-cinematic` 技能（本仓库）——Cycles 渲染图片序列、运镜配方；渲成 PNG 再转 WebP。
- 从视频抽帧（ffmpeg 免费）：`ffmpeg -i clip.mp4 -vf "fps=24,scale=1600:-2" -c:v libwebp -quality 78 frames/f_%04d.webp`（ffmpeg 自带 libwebp 编码器；参数为经验值）。用户机器上已有 ffmpeg 9.0.1。
- 用户自己拍的视频（手机慢慢绕车走一圈、洗车前后固定机位延时）最便宜也最真实。
- AI 视频（Kling、Runway、Veo、Seedance）多数**付费**，先问；本仓库 `ai-archviz-render` 有本地 ComfyUI + Wan2.2 的免费路线。
- 素材授权：不要拿别人网站的帧/视频；Pixabay 视频可用（`pixabay-assets` 技能）。

## 4. three.js 替代
- 有真实 3D 车模（glTF）时，可用 three.js 让滚动驱动镜头和车漆颜色（换色器就直接改材质颜色，任何角度都对）。本仓库有 `threejs-web`、`threejs-camera-controls-and-rigs`、`threejs-materials`、`threejs-performance`、`threejs-image-pipeline`。
- 代价：车模要授权（`free-3d-assets` 找 CC0/CC-BY），手机 GPU 负担大，LCP 晚；小商家站一般图片序列 + 预渲染的几种颜色更稳（经验判断）。

## 5. 无障碍
- WCAG 2.3.3 Animation from Interactions（**AAA**）：交互触发的动画要能关掉，除非是必要的；滚动带出的额外动画、视差都"不必要"。技法 C39（CSS `prefers-reduced-motion`）、SCR40（JS 里读它）。https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html
- 不要滚动劫持：不拦 `wheel`/`touchmove` 默认行为，不锁 body 滚动（除了打开对话框时），键盘 PageDown/空格/方向键照常能滚，故事区有"跳过动画"链接。
- 抽屉表单：用 `<dialog>` + `showModal()`（浏览器自带焦点困住、Esc 关闭、背景 inert）；关闭后焦点回到按钮。错误用 `aria-invalid` + `aria-describedby`，提交结果用 `role="status"`。
- 颜色选择器：用原生 radio 组（方向键切换），颜色名用文字写出，不只靠色块。

## 6. 性能预算
- Core Web Vitals 好的标准：LCP ≤ 2.5 s、INP ≤ 200 ms、CLS ≤ 0.1，按 75 百分位、手机桌面分开。https://web.dev/articles/vitals
- 做法：首帧图 `fetchpriority="high"`；其他帧懒加载；画布有固定宽高比不跳版面；字体 2 个以内、`font-display: swap`。帧总量手机 ≤ 4 MB（经验值，**未验证**）。

## 7. 预约表单 + 线索存储（免费）
- Supabase 免费版：每项目 500 MB 数据库、5 GB egress、5 万 MAU、最多 2 个活跃项目、**闲置 1 周会暂停**（商家站要提醒：一周没人提交就会睡，要定期有流量或升级——升级是**付费**）。https://supabase.com/pricing
- RLS：暴露 schema 里每张表都要开 RLS；只给 anon `insert` 权限 + `with check` 策略，不给 select；secret key 不能放浏览器。https://supabase.com/docs/guides/database/postgres/row-level-security
  - `insert ... returning` 没有 select 权限会报 42501 → 前端用 `Prefer: return=minimal`（**未验证**，按 PostgREST 惯例）。
- 后台"表格"：Supabase Studio 的 Table Editor 就是现成的表格；或者用户自己的 Google Sheet。
- 备选（不用数据库）：Formspree / Web3Forms 之类的表单转发服务有免费额度（具体额度**未验证**，没查）。

## 8. 通知商家
| 方式 | 费用 | 说明 |
|---|---|---|
| Twilio SMS 到马来西亚 | **付费**，约 US$0.3389/条 + 号码 US$1.15/月起（表格栏位不清楚，**部分未验证**）https://www.twilio.com/en-us/sms/pricing/my | 要先问；还有发送者注册要求 |
| Telegram Bot | 免费；同一聊天 ≤1 条/秒，群 20 条/分 https://core.telegram.org/bots/faq ；`https://api.telegram.org/bot<token>/sendMessage` https://core.telegram.org/bots/api | 商家要先对机器人按 Start（Telegram 规则，FAQ 页没直接写 → **未验证**）；token 只能放服务端 |
| Email（Resend 免费版） | 免费 3000 封/月、100 封/天 https://resend.com/pricing | 要自己的域名验证 |
| WhatsApp click-to-chat `https://wa.me/<号码>?text=...` | 免费 | 客户自己点开发给商家；马来西亚最常用。格式按惯例，官方页没抓到 → **未验证** |
- 触发方式：Supabase Database Webhook（after insert → pg_net 异步 POST 到 Edge Function，Edge Function 再调 Telegram/Resend）。https://supabase.com/docs/guides/database/webhooks

## 9. 防垃圾
- Cloudflare Turnstile 免费：20 个 widget、无限次验证。https://developers.cloudflare.com/turnstile/plans/ ；token 要在服务端 siteverify（Plans 页没写，按 Turnstile 文档惯例 → **未验证**）。
- 不要钱的基本做法：隐藏 honeypot 字段、填表最短时间（<3 秒拒收）、数据库层面限长度/格式（check 约束）。

## 10. 隐私（马来西亚 PDPA）
- PDPA (Amendment) Act 2024：2025-01-01 / 04-01 / 06-01 分三阶段生效；6 月那批包括委任 DPO、数据泄露通报、数据可携权（可携权日期来源有冲突）。https://insightplus.bakermckenzie.com/bm/data-technology/malaysia-personal-data-protection-amendment-act-2024-to-come-into-force 、https://www.dfdl.com/insights/legal-and-tax-updates/malaysia-implementation-of-the-personal-data-protection-amendment-act-2024/
- 小商家网站最低要求（一般做法，**不是法律意见**）：表单旁写清楚收集什么、拿来做什么、存多久、怎么要求删除（PDPA 的通知与选择原则）；同意勾选框不预先勾；只收需要的栏位（名字、电话、车型、日期）；不放第三方追踪器就不用 cookie 横幅。

## 11. 免费托管
- Cloudflare Pages 免费：每月 500 次构建、每站 2 万个文件、单文件 ≤25 MiB；没写带宽上限。https://developers.cloudflare.com/pages/platform/limits/ —— 帧序列文件多，2 万文件够用。
- GitHub Pages、Netlify 免费版也行（额度没查，**未验证**）。

## 12. 给技能的结论
1. 模板零依赖：原生 canvas + rAF 帧序列；CSS scroll-driven 只做装饰；GSAP/Lenis 可选、锁版本。
2. 帧来源顺序：用户自己拍 → Blender（archviz-cinematic）→ ffmpeg 抽帧；AI 视频付费先问。
3. 表单默认本地演示；接 Supabase（anon 只能 insert + RLS）；通知用 Telegram/Email 免费，SMS 是付费选项。
4. reduced-motion 时整段换成静态前后对比图，不滚动劫持，`<dialog>` 做抽屉。
5. 交付清单：LCP ≤2.5 s、手机帧 ≤4 MB、隐私说明、Turnstile/honeypot。
