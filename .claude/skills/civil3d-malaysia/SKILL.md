---
name: civil3d-malaysia
description: "Plan, teach, automate, and review Autodesk Civil 3D workflows for Malaysian projects: survey points, TIN surfaces, earthworks, road alignments/profiles/corridors, drainage networks, and drawing delivery. Use Malaysian project criteria and JKR/JPS/JUPEM evidence; do not substitute European or US design defaults."
---

# Civil 3D — 马来西亚项目

给 Claude Code 与 OpenAI Codex 共用。用中文解释，保留 Civil 3D 的英文对象、菜单和字段名，方便用户对照英文界面。专注 Autodesk Civil 3D；不要把用户指定的软件替换成 FreeCAD。

## 先确定这次要做的事

- 教学：用小型示例解释一个流程，示例参数标为教学假设，不冒充 JKR/MSMA 标准。
- 建模或审查：确认图纸、对象、范围和交付物后，只处理授权范围。保留原始测量数据和源 DWG，先在副本试做。
- 自动化：先检查当前实际连接的工具和 Civil 3D 版本。读 [automation.md](references/automation.md)；本技能不是 MCP 服务，也没有附带可直接控制 Civil 3D 的连接器。

用户已明确要求使用本技能或执行本次操作时，不重复询问；否则按 T1 的技能使用规则说明用途并取得同意。安装第三方插件、改全局设置、运行修改图纸的代码或上传项目数据，需要有对应授权；“研究技能”不等于“改正在打开的图纸”。

## 马来西亚依据优先

先读 [malaysia-basis.md](references/malaysia-basis.md)。确认州/联邦直辖区、地方政府 PBT、道路/排水主管机关、项目采用文件及版本。只问影响当前操作的缺失项，不让简单教学先填完整工程表。

1. 道路依据项目采用的 JKR Arahan Teknik (Jalan)、地方/州主管机关要求及获批设计条件；排水依据适用的 JPS/DID MSMA 和项目/主管机关条件。
2. 不默认套用 EU/Eurocode、UK DMRB、UK rainfall、美国 AASHTO/NOAA 参数。Civil 3D 的 Metric 模板、无警告的 Design Check、国外 Country Kit 均不能证明符合马来西亚要求。
3. 对每个用于判断合格的数值，记录“数值、单位、适用条件、文件版本、条款/表格、核验状态”。缺资料就标“未核验”，继续不依赖该数值的整理/建模工作；不要编造最小半径、坡度、ARI、雨强、管径或土方系数。
4. 马来西亚采纳的 MS EN 与直接套用 EU/其他国家国家附件不同。若项目明确要求 MS EN，使用该马来西亚采纳文件和适用国家附件；不能因为“不要 EU”就擅自排除项目要求，也不能因此引入欧洲默认数值。结构设计超出本技能范围。
5. 图纸看起来正确、脚本通过、Civil 3D 没报错，都不是工程签核。

## 按任务读取

| 当前任务 | 读取 |
|---|---|
| 坐标、点文件、OGL/EG、TIN、平台、边坡、Cut/Fill | [survey-earthworks.md](references/survey-earthworks.md) |
| Alignment、Profile、Assembly、Corridor、断面、排水 | [roads-drainage.md](references/roads-drainage.md) |
| Dynamo、.NET、AutoLISP、MCP 或程序生成 | [automation.md](references/automation.md) |
| 学习资料、依据与版本复核 | [sources-and-learning.md](references/sources-and-learning.md) |

## Civil 3D 共用工作约定

记录 Civil 3D 年版与补丁、图纸单位、坐标与高程基准、模板、源文件和对象关系。地形/道路通常采用 m、m²、m³，设计速度 km/h；管材目录可能用 mm。检查实际单位，不直接缩放整张图“修好”。

从 Toolspace 的 Prospector/Settings 检查实际对象。区分 Civil 3D 智能对象、AutoCAD 线条、代理对象和外部参照；不要把“有图形”当成“有可编辑模型”。调整上游对象后，检查受影响的 Surface、Corridor、Data Reference、Profile、Section 和数量是否已更新。

需要批量核对输入资料是否齐备时，可复制 [project-context.example.json](assets/project-context.example.json) 到项目工作区，按实际范围填写后运行：

```text
python <本技能目录>/scripts/audit_context.py <项目工作区>/project-context.json
```

脚本只读 JSON 并向 stdout 输出缺项/格式问题，不联网、不读写 DWG、不计算设计值。退出码 0 只表示所选范围的资料字段齐备，绝不表示符合 JKR/MSMA 或可以施工。格式详见 [context-format.md](references/context-format.md)。

## 交付与核验

按请求交付可编辑 DWG/数据、平纵横断图、土方或放样表；保存版本、对象名、计算边界、参数来源和异常清单。交付前重开输出文件，抽查控制点/标高、引用、图层、比例、单位和图纸可读性。交付 LandXML 时核对导入后的对象数、坐标、关键标高及未被保留的样式/关系，不声称它是 DWG 的无损替代。

报告明确区分：已实际执行并验证、仅依据文档拟定、等待项目标准/专业人员核验。适合工程报批或施工的成果由负责项目的合资格专业人员审核。

与已有技能重叠时：Civil 3D 操作以本技能为主；`civil-survey-qc` 可补点文件只读检查，`civil-as-built-check` 可补设计/竣工对比，`quantity-surveyor` 可补 BOQ；它们不能替代本项目的马来西亚计量条款。
