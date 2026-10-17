# 采样与解释

[Cfx Profiler 文档](https://docs.fivem.net/docs/scripting-manual/debugging/using-profiler/) 是命令依据；核对客户端/服务器实际版本。常见流程：

```text
profiler record 500
profiler status
profiler saveJSON new-capture.json
```

500 是官方入门示例的帧数，不是秒，也不是适合所有问题的固定时长。先等待完成；保存位置由实际运行环境决定，使用新的文件名。profiler view 可打开浏览器，服务器侧可能需要手动访问链接；不把它当纯终端读取。

记录采样侧（server/client）、开始时间、构建/资源修订、复现动作、玩家/实体负载与时长。Chrome DevTools Performance 可载入导出的 profile，格式先辨认再解析；不能假设所有 JSON 都是同一 traceEvents 模式。异步等待与 CPU 执行分开，重复计数的嵌套事件不直接求和。

resmon 的资源耗时是筛查线索；低均值可能掩盖尖峰，资源 CPU 低也不能排除贴图/GPU 或数据库等待。源码定位需对应采样时版本；文件/行标记不代表那一行就是全部因果证据。

采样中可能包含资源名、路径或用户相关信息；本地分析仅取需要的数据，不自动传到遥测或云分析服务。
