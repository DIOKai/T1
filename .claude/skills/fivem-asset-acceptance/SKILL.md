---
name: fivem-asset-acceptance
description: Review staged FiveM vehicle, prop, ped or map assets for packaging, source preservation, collision, LOD, texture and in-game acceptance evidence. Use before delivery or after conversion; binary file presence alone cannot certify an asset.
---

# FiveM Asset Acceptance

确认类别、Legacy/Enhanced 目标、game build、资源名、源文件和交付目录。此 Skill 做交付验收，补充已有车辆/人物/MLO 制作 Skill，不擅自重新制作或优化模型。

## 验收

1. 先记源文件清单/哈希和目标平台。只在交付副本检查；原有 ytd/yft/ydr 等按任务要求 1:1 保留。发现尺寸、贴图或几何问题先报告，不自动压缩、减面、删 mipmap 或改原档。
2. 按 [package-and-provenance.md](references/package-and-provenance.md) 核对 manifest、引用、大小写、名称冲突、依赖与资产来源。二进制不可读部分列未验证；不能因为扩展名正确、XML 可解析就判可用。
3. 按 [visual-and-runtime.md](references/visual-and-runtime.md) 检查材质、背面、碰撞、骨骼、LOD 和比例。Blender/CodeWalker 的预览与游戏验收分开记录。任何 Blender 修改、导出、格式转换、资源重启/上服都需要该动作的任务授权。
4. 在实际目标构建和测试服检查加载、接近/远离、碰撞与多人表现，并保留日志和证据。Qbox 登记/商店/库存属于玩法接入，不能代替底层资产验证。

## 输出

分别列已通过、失败和未验证项，带路径、工具/版本、目标构建及证据位置。给静态通过而游戏未测的包明确写“游戏内未验证”。视频学习、模型来源或文件扫描都不能单独证明已完成转换和验收。
