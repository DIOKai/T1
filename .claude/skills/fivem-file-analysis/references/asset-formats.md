# 模型格式与导入/导出

以 [Cfx Exploring and Exporting GTAV Assets](https://docs.fivem.net/docs/assets-manual/beginner-series/part-2/)、[Sollumz 文档](https://docs.sollumz.org/) 及 [创建首个资产](https://docs.sollumz.org/getting-started/creating-your-first-asset.md) 核对实际工具版本。

YFT/YDR/YDD/YTD 等通常是二进制资产。文本编辑器显示乱码、XML 导入失败或过旧工具不支持，不等于 Escrow 加密。分别记录工具版本、操作、错误、文件来源与目标 Legacy/Enhanced。文件名和扩展名只是一条线索，不是内部格式验证。

旧 CodeWalker/Sollumz 视频示范 XML 交换；当前工具还可能支持直接二进制工作流，不能将旧菜单位置或“永远先转 XML”当成统一要求。导出只在新目录做，保持原档 1:1；如果确需格式转换，记录输入输出映射，不要求转换前后哈希相同。

预览/导入成功也不等于游戏兼容。之后核对引用、材质、碰撞、骨骼、LOD 及实际游戏加载；仅做文件识别时不要顺手重压纹理、减面、删 mipmap 或改 meta。工具缺失、加密、损坏与版本不兼容分别列证据，不能只凭一个打不开的截图确定原因。

对受保护的文件不能把普通格式转换教程当成解密证明；查看可读配置、作者提供的可编辑原档或接口文档可能足够完成用户真正要的修改。
