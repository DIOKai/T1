---
name: fivem-performance-profile
description: Diagnose FiveM client or server performance using reproducible resmon/profiler evidence, comparable captures and behavior checks. Use for hitches, frame spikes or slow resources; not generic Windows FPS tweaks or automatic server tuning.
---

# FiveM Performance Profile

先区分客户端帧时间、服务器 hitch、数据库/API 延迟、网络和资产 streaming。记录目标构建、资源版本、硬件、玩家数量和触发场景；不能仅凭报错名称或一个 idle resmon 数字确定原因。

## 证据流程

1. 优先读取已有采样、日志和代码。在已授权的测试环境安排可复现步骤，按 [capture-and-interpret.md](references/capture-and-interpret.md) 捕捉问题发生时的 profile。没有服务器/游戏权限时提供采样步骤，不虚构已执行。
2. 用 resmon 缩小资源范围，再用 profile 对齐进程、线程、资源、文件/行与尖峰时刻。CPU 区段、端到端等待、GPU/贴图和网络指标不是同一种耗时，不能重复累加嵌套区段。
3. 形成可验证假设：热循环、昂贵 native、事件风暴、实体增长、NUI、查询或 streaming。每次做范围明确的改动，保留需要每帧执行的行为和网络/所有权语义，避免统一增加 Wait 或盲目缓存。
4. 按 [comparison-and-regression.md](references/comparison-and-regression.md) 在可比条件重测；保留优化前后证据和功能回归。没有可比采样就只报告候选改善，不承诺 FPS、毫秒预算或玩家容量。

采样会有开销；范围、持续时间和输出位置要明确。正式服操作、停用/重启资源、改 convar 或启动浏览器遵守对应任务授权，不因加载本 Skill 自动执行。

交付问题条件、定位证据、假设、补丁、前后数据、功能回归和未验证边界。不要用删功能、关校验或忽略 hitch 达到“优化”。
