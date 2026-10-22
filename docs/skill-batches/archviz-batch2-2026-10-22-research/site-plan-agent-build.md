# 研究笔记：site-plan-agent-build（先画总平面，再多代理分区建造）

日期：2026-10-22。所有网页在当天打开；没打开到原文、只靠搜索摘要或记忆的标「未验证」。

## 0. 起因（未验证）

Threads 上流传的帖子：一座日本寺院（五重塔、红色拱桥、枯山水、石灯笼、金边柱、樱花树）「没有用 3D 模型，全部是 Claude 写的代码」，4 个提示词：
1. 先画总平面图，写出每栋建筑的位置（米）；
2. 分区，每区一个代理；
3. 每区做完截图，和参考照片对比，修；
4. 最后规划 10 个镜头，每个从小物件特写开始往外拉。
作者说「第 1 步最重要：没有平面图，每个代理各盖各的，塔就盖进池塘里」。
原帖没打开（Threads 需要登录，搜索也找不到原帖），以上来自用户的描述。视频画面像实时渲染（three.js/WebGPU 或 Blender 程序化都有可能），**作者用哪个工具未验证**。

## 1. 多代理协作（为什么要一份总平面 JSON）

- Claude Code 子代理 —— https://code.claude.com/docs/en/sub-agents
  - 子代理是 `.claude/agents/*.md`（或 `~/.claude/agents/`）带 YAML frontmatter 的文件，`name`、`description` 必填；也可由主对话用 Agent 工具直接派出。
  - 「Each subagent runs in its own context window」——**不共享对话**，只把最终结果交回主对话；会读 CLAUDE.md。
  - 可以并行（默认最多 20 个同时，`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`）；`isolation: worktree` 让子代理在临时 git worktree 里工作。
  - 子代理默认可以再派子代理（最多往下三层，`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`）。AskUserQuestion 在子代理里不可用 → 子代理不能问用户，要问的事情主代理先问完。
- Claude Code agent teams —— https://code.claude.com/docs/en/agent-teams
  - 实验功能，默认关闭（`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`）。共享任务清单 + 互发消息。
  - 原文建议：「Two teammates editing the same file leads to overwrites. Break the work so each teammate owns a different set of files.」——就是本技能的「文件归属」规则。
  - 建议 3–5 个队友；同文件修改、依赖多的工作用单会话或子代理更好。
- OpenAI Codex 子代理 —— https://developers.openai.com/codex/subagents（308 转到 https://learn.chatgpt.com/docs/agent-configuration/subagents）
  - 现在版本默认开启（`[agents]` 里 `agents.enabled`，默认 true）；**只在用户明确要求时才派子代理**（搜索摘要，未逐字核对）。
  - 自定义代理：`~/.codex/agents/` 或项目 `.codex/agents/` 下的 TOML，必填 `name`、`description`、`developer_instructions`。
  - `agents.max_concurrent_threads_per_session` 限制同时线程数；子代理继承父的沙盒和审批设置。
  - 原文提醒：「agents editing code at once can create conflicts」，建议并行主要用于偏读的工作。
  - 页面没写派代理的工具名，也没写嵌套深度 → 技能里只写「请 Codex 派子代理」，**不编工具名**。另一页 https://developers.openai.com/codex/multi-agent 的旧说法是「实验功能要手动开」，两页矛盾，以安装版本为准（未验证）。
- Anthropic《How we built our multi-agent research system》—— https://www.anthropic.com/engineering/multi-agent-research-system
  - 每个子代理需要「an objective, an output format, guidance on the tools and sources to use, and clear task boundaries」。
  - 简短指令导致子代理误解任务或重复做同一件事；代理「not yet great at coordinating and delegating to other agents in real time」。
  - 子代理把结果存到外部、只回传引用，减少「传话游戏」。
- Cognition《Don't Build Multi-Agents》—— https://cognition.com/blog/dont-build-multi-agents
  - Flappy Bird 例子：两个子代理各自做背景和小鸟，风格不一致，最后很难合并。
  - 「Actions carry implicit decisions, and conflicting decisions carry bad results.」
  - 对本技能的结论：**隐含决定（比例、风格、配色、坐标、单位、朝向）必须在派代理前写进共享文件**；每个代理只拿到简报，没有你的对话。
- git worktree —— https://git-scm.com/docs/git-worktree：「Manage multiple working trees attached to the same repository.」每个代理一个 worktree 时，最后要合并分支；不用 worktree 时就靠「每个代理只写自己的文件」。

由此得出的做法（技能的核心）：
1. `site-plan.json` 是唯一真相来源（单位米、Y 轴向上、原点、北向、配色、风格、每栋建筑的脚印/高度/锚点）。代理**只读不写**，要改就回报给主代理改。
2. 每区一个包围盒 + 一个负责代理 + 自己的文件（`zones/<zone_id>.js` 或 `.py`）；共用代码（材质库、工具函数）由主代理先写好，代理只读。
3. 接口契约：每区导出一个函数 `buildZone(ctx) → THREE.Group`（或 bpy 里一个 collection），根在 site 坐标，地面 y=0（或 plan 给的 ground_y）；跨区的东西（桥、路、水）明确归一个区，另一区只留接口点。
4. 派代理前先跑 `check_site_plan.py`，不过关不派。
5. 集成由主代理做：加载全部区 → 再跑检查（包围盒对照） → 整体截图。

## 2. 程序化建筑（仓库已有技能）

读了 `docs/skill-batches/city-40-2026-10-18.md` 和这些 SKILL.md 的结构：
- `threejs-procedural-buildings-and-cities`：「Treat architecture as a compiler」——先出可序列化、可验证的计划，再出几何；每个元素有稳定 ID、owner、support 和 clearance；「Place the landmark first, then solve access, support, and clearance before repeated detail.」→ 与本技能的「先地标、后细节」一致，本技能是它上面的「多代理分工层」。
- `threejs-procedural-geometry`：剖面扫掠、拱、框；InstancedMesh/BatchedMesh 选择。
- `threejs-object-sculptor`：参考图驱动的单件物体（灯笼、塔顶相轮这种）；先看证据、标明假设。
- `threejs-procedural-vegetation`：樱花树和地被；`threejs-water-optics`：池塘；`threejs-sky-atmosphere-and-haze`：天空雾气；`threejs-visual-validation`：先声明可证伪的主张再验证，「Validate claims, not polished frames」。
- Blender 路线：`floorplan-to-blender`（布局 JSON → 校验 → bpy 建造 → 检查悬空）、`parametric-facade`（Geometry Nodes，检查不悬空）、`archviz-cinematic`（镜头）。
- three.js API（InstancedMesh(geometry, material, count)、setMatrixAt、instanceMatrix.needsUpdate、ExtrudeGeometry、LatheGeometry、TubeGeometry）：https://threejs.org/docs/ 页面是 JS 渲染，WebFetch 只拿到目录 → API 名称凭已知资料，**未逐页验证**；以项目安装的 three 版本为准。

## 3. 和参考照片对比

- SSIM —— https://en.wikipedia.org/wiki/Structural_similarity_index_measure：需要「corresponding locations in two images」的对齐参考图；有研究认为它的表现「much closer to that of the MSE」。→ 渲染图和真实照片相机、光照、材质都不同，像素对齐指标几乎没有意义。
- 搜索结果（arxiv 2305.08840《Attacking Perceptual Similarity Metrics》、appliedAI 的 perceptual metrics 文章 https://tfl.appliedai.de/blog/perceptual-metrics/）：SSIM/MSE 对错位、缩放敏感；LPIPS 容忍度高但也会被骗；没有找到专门评「照片 vs 3D 渲染」的指标。（摘要，未逐篇读）
- 结论：用**同机位截图 + 并排对照 + 逐项清单**（比例、轮廓、层数、颜色区块、构件有没有、接地、遮挡），由看图的代理逐项打分并给证据；数字指标最多只当「有没有变」的回归检查（同机位、同代码前后两版），不当「像不像照片」的分数。
- Playwright 截图 —— https://playwright.dev/docs/screenshots：`page.screenshot({ path, fullPage })`；元素截图 `locator.screenshot()`。three.js 页面用固定相机参数 + `preserveDrawingBuffer` 或 `canvas.toDataURL()`（后者凭经验，未验证）。

## 4. 日本寺院比例（举例用，只引可靠来源）

- 塔 tō —— JAANUS https://projects.mcah.columbia.edu/jaanus/node/575
  - 法隆寺五重塔：各层 3×3 间（6.42 m 见方），第五层 2×2 间；裳阶 10.85 m 见方。
  - 羽黑山五重塔 3×3 间（5.02 m），「each story slightly smaller than the one below」；室生寺五重塔 3×3 间仅 2.44 m（特小）。
  - 当麻寺东塔一层 3×3 间（5.23 m），二三层 2×2 间。
- 石塔条目（搜索摘要）：五重塔每层只略收，九重、十三重收得明显。
- 法隆寺五重塔高约 32.45 m（Wikipedia https://en.wikipedia.org/wiki/Japanese_pagoda、Structurae；另一工程论文写 32.55 m）。屋顶「10:9:8:7:6」比例来自 MLIT 解说的二手转述，**未验证**，只能当经验起点。
- 2024《Journal of Asian Architecture and Building Engineering》研究（DOAJ https://doaj.org/article/d0ad29dd28424bc9941c794aa89924e7，摘要）：东亚木塔斗拱尺寸从第一层到第五层递减（未读全文）。
- MLIT 多语言解说（https://www.mlit.go.jp/tagengo-db/common/001545932.docx，寺名未写）：五重塔实际只有一层可用，「The other four tiers are layers of bracket complexes and eaves」——上层不用做室内。
- 相轮 sōrin —— https://projects.mcah.columbia.edu/jaanus/record/sorin：自下而上 露盘、覆钵、九轮、水烟、龙车、宝珠。
- 斗拱 —— JAANUS sonae / tokyō（https://aisf.or.jp/~jaanus/deta/s/sonae.htm、https://aisf.or.jp/~jaanus/deta/t/tokyou.htm，搜索摘要）：kumimono = tokyō，由肘木（hijiki）、大斗（daito）、卷斗（makito）组成，放在柱上。
- 鸟居 —— https://aisf.or.jp/~jaanus/deta/t/torii.htm 与 myōjin torii 条目：两柱（hashira）+ 笠木（kasagi）+ 岛木（shimaki）+ 贯（nuki，约低一个柱径）；明神鸟居笠木两端上翘，柱向内倾（uchikorobi），贯伸出柱外约 1/5 长度并用楔固定，中间额束，柱脚亀腹或方石基础。（鸟居多属神社；寺院也有，但做「寺院」场景时要和用户确认要不要放。）
- 太鼓桥 / 反桥 —— https://projects.mcah.columbia.edu/jaanus/record/taikobashi：石或木造的拱桥；住吉大社反桥（MLIT https://www.mlit.go.jp/tagengo-db/common/001565814.pdf，摘要）。
- 枯山水 —— https://aisf.or.jp/%7Ejaanus/deta/k/karesansui.htm：只用石、砂（砾）和少量植物表现山水，耙纹表示水；从一个坐着的视点观看；禅寺偏爱。nippon.com https://www.nippon.com/en/guide-to-japan/cs00063/karesansui-japan%E2%80%99s-dry-landscape-gardens.html：供观赏不供行走。
- 石灯笼的构件比例没找到可靠来源 → 技能里写「未验证，按参考照片」。

## 5. 「特写 → 往外拉」镜头

- 搜索到的多是 Morphic（AI 视频公司）术语页 https://morphic.com/resources/shots/pull-back-shot、https://morphic.com/ai-glossary/dolly-out：pull back / dolly out 是相机实际后退，透视会变化（和 zoom out 不同）；慢拉显得沉思、常用于收尾；快拉制造「原来这么大」的揭示。厂商措辞，**当行话参考，不当标准**。
- 仓库 `archviz-cinematic`：2–4 个关键帧、缓入缓出、roll=0、慢；镜头数值是经验值。本技能的镜头表沿用它的规则，补上「起点物件、终点构图、拉出距离、会穿过什么（不能穿墙穿树）」。

## 6. 没做到的

- 没找到原 Threads 帖子与视频；作者工具链未验证。
- 没在浏览器或 Blender 里实测本技能的建造流程；只测了 `check_site_plan.py`。
