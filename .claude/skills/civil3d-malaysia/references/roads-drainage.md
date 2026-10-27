# Civil 3D 道路、排水与图纸

## Alignment → Profile → Corridor

1. 使用核验后的 EG/OGL、控制线及道路设计依据。创建或审查 Alignment 的起点、方向、stationing/chainage、station equations、曲线和缓和曲线。左右 offset 始终与 alignment 增桩方向对应。
2. 确认左侧通行、分隔带/路肩布置与项目典型横断面，特别检查从右侧通行教学样板复制来的 Assembly。不要依靠“镜像后看起来对”判断连接、坡向和超高。
3. 在 Alignment Properties 的 Design Criteria 中核对设计速度、criteria file、table 和 design check set 的真实来源。根据经核验的 JKR/项目台账建立检查；内置 AASHTO 条件不能当成 JKR。
4. 从 EG 建立 Surface Profile；另建 Layout Profile 作为设计纵断。检查交叉口、桥涵/出入口、垂直曲线、纵坡与视距条件，不把现状 Profile 当成设计 Profile。
5. Assembly/Subassembly 的宽度、层厚、横坡、路肩、边坡与排水构造来自获批断面；核对各 subassembly 支持的 target 与 superelevation 参数。超高不能只在表里存在却没被实际横断面采用。
6. 建 Corridor，明确 baseline、profile、assembly、regions、频率和所有 surface/width/elevation targets。检查区域起止、target 丢失、急弯、过渡、交叉口、加宽与 daylight 接驳；采样频率按几何变化与项目需要设置，不规定一个万能间距。
7. 用所需 link/feature line codes 建 Corridor Surface，核对实际代码，不假定每个自定义构件都带 Top/Datum。加入合适边界，检查长三角形、跨中分带的虚假面、空洞和重叠；重建后再抽查。
8. 建 Sample Line Group，核对采样的 EG、走廊/设计面与材料表。平面、纵断和横断必须采用同一修订；数量使用的 formation 面需与图纸含义一致。

Civil 3D 的 Corridor Surface 可与走廊保持动态关系；导出的 detached surface 不应当作仍会自动更新。不要把走廊输出曲面反过来用作该走廊的目标，造成循环依赖。

## 雨水网络不是仅画一组管

从 MSMA/项目依据确认汇水范围、设计事件和水文/水力方法。把排水几何与容量核验分开：Pipe Rules 可检查布置条件，不能单凭“无规则警告”宣称满足 MSMA。

建模前列明：catchment 与分区来源、IDF/设计雨型资料及适用地点/版本、ARI、径流与时间参数的依据、排放点和尾水、既有设施/公用管线、允许积水/溢流与维护条件。不自动采用美国 NOAA、英国雨型或一个统一的“马来西亚重现期”。

在实际版本中选择合适的 gravity pipe network / channel / pond 工作流：

- 检查 Parts Catalog、Parts List、材料、尺寸和 mm/m 单位。目录中有某尺寸不代表符合当地采购/设计条件。
- 确认 flow direction、reference surface、结构 rim、连接 invert、坡度/cover、manhole/drop 与 outfall；在 profile view 查看，不只看平面。
- 从 polyline/alignment 建网时，检查节点数量与原对象保留选项；不要在仍被其他设计对象引用时删除源线。
- 对有交叉的管网做几何干涉检查，并检查入口、旁通、出口、明沟接驳和洪水逃生路径；几何不冲突不等于水力合格。
- 选用项目接受且实际可用的分析方法，记录输入、软件/引擎版本和边界条件；分析后核对关键节点/流量、HGL、回水、超载与溢流结果。遇到不支持的 MSMA 方法，保留 Civil 3D 几何，明确外部计算接口，不谎称软件已完成该项核验。

Civil 3D 2027/2027.1 的 Drainage Tools 与旧教程的 SSA/Hydraflow 流程可能不同。核实当前版本、授权、云端分析的数据上传和费用条件，再选择工作流；技能本身不授权上传工程数据或购买服务。

## 放样、图纸与交付

放样表注明 alignment 方向、桩号/断链、offset 正负、目标标高界面、E/N 顺序和基准。检查曲线/区域边界等关键点，不凭均匀间距覆盖全部重要位置。

出图前核对 Plan/Profile/Section 的单位、水平/垂直比例、band set、标签对象、revision、参照文件和打印样式。以项目/PBT 的图签和提交要求为准，不复制国外工程审批声明。

接收方使用旧版 Civil 3D 时，先确认智能对象兼容性；普通 DWG Save As 或 Object Enabler 不能保证对象可编辑。必要时另外提供交换格式与明确的损失说明，并做往返抽查。
