# 上下文与覆盖

qbx-lint/qbx-lua-ls 共用 CfxLua 分析，并读取资源 manifest 理解加载和客户端/服务端上下文。普通 Lua 解析器可能不认识 Cfx 扩展；语法通过也不能验证某个 export 在运行时存在。

检查输入是否确实被分析：当前上游默认跳过 node_modules、.git、[builders]，不跟随目录链接且跳过隐藏目录；配置 exclude 与 ignore_diagnostics 也会影响结果。前者可使文件不进入分析，后者可能仅抑制报告。不要以扫描一个仓库技能目录代替扫描实际资源。

qbxlint.toml 搜索从第一个输入向上进行；不同资源配置不应不加区分地合并一轮。配置导入、动态 exports、运行时加载、缺失依赖、escrow/二进制或 JS/C# 需要报告覆盖限制。内置 native 数据不等于实时 API；拿当前 Cfx/Qbox 文档和目标资源版本核对。

[Cfx manifest](https://docs.fivem.net/docs/scripting-reference/resource-manifest/) 已将 lua54 开关标为弃用，现代 Lua 资源默认使用 5.4。不要因旧教程缺少 lua54 'yes' 就认定当前资源无法运行，也不顺手改所有旧 manifest。

最低验收记录：版本、路径、配置、退出码、诊断/跳过项；语法错误、缺工具、配置错误和无输入分别记录。运行时验证与安全审查另报，不从 lint 结果推断。
