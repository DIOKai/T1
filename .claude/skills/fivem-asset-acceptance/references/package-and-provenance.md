# 包装与来源

对照 [Cfx Resource Manifest](https://docs.fivem.net/docs/scripting-reference/resource-manifest/) 检查实际资源类别所需的 data_file、files、依赖与加载入口；不是所有 stream 文件都需要逐个写进 files，不套用万能车辆 manifest。

核对引用的相对路径与大小写、YMAP/YTYP/archetype 名称、车辆 modelName 和相关 meta 关联，以及跨资源同名覆盖。先列清单再操作；不要为“清理”移除未知文件。xml 导出和游戏二进制不同；改名也不是格式转换。Legacy/Enhanced 兼容按目标工具链验证。

保留输入、输出和转换工具/版本/选项。若任务是 1:1 复制模型/贴图，比较源/目标哈希；合法的格式转换则记录来源到输出映射与变化原因，不能宣称转换后哈希仍应一致。

来源和许可证逐项记录，工具开源不代表通过工具导入的模型也开源。只提供下载链接或标免费而无明确授权的资源，不称可再分发。仅审查不下载、重打包或上传资源。

二进制文件只能通过适当工具、导入/导出和游戏验证确认内部结构。沿用已有类别检查器时先阅读其参数/副作用，结果属于该检查器覆盖范围，不提升为全资产认证。

来源：[Sollumz 官方文档](https://docs.sollumz.org/)、[CodeWalker 源码](https://github.com/dexyfex/CodeWalker)、[Enhanced 资产转换](https://docs.sollumz.org/tutorials/asset-conversion-for-gtav-enhanced.md)。核对日期 2026-10-17；执行时匹配实际安装版本。Enhanced 教程同时包含单机 OpenRPF/ASI 加载步骤，不等同于 FiveM 资源部署，不据此自动安装玩家插件。
