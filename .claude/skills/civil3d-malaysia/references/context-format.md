# project-context.json：只检查元数据

`scripts/audit_context.py` 使用 Python 标准库，只读传入文件，输出 JSON 报告。支持 UTF-8/UTF-8 BOM；不读取路径字段指向的任何文件。拒绝重复 JSON 键、NaN/Infinity 和不正确的字段类型。用 `python -m unittest discover -s tests -v` 在本技能目录运行离线测试。

这是元数据缺项检查器，不解析 DWG、标准原文、坐标系合法性或数值合理性。`metadata-complete` 表示下述字段存在且格式符合约定；可能仍缺少实际设计所需参数。由填写者声明的 evidence 字段也不代表工具验证过文件。

必填字段：

- `project.name`, `project.state`, `project.authority`：非空文字；`project.country` 固定 `MY`。
- `scope`：非空、不重复列表，取 `survey`, `earthworks`, `road`, `drainage`, `automation`。
- `drawing.release`, `drawing.build`, `drawing.template`：实际版本、补丁/构建、模板或现有图纸配置来源。`drawing.linear_unit` 固定 `m`，表示本工作流的模型坐标单位；mm 原图应先核实并建立单位方案，不直接缩放。
- `survey.horizontal_reference`, `survey.vertical_reference`, `survey.control_evidence`：基准（含适用投影/分区/realization）、竖向基准、控制证据定位。仅做自动化/教学且不涉及地理量时，也应明确写明为何不适用，不能伪填坐标系。
- `criteria`：数组。每条有唯一 `id`、属于本次 scope 的 `scope`、有限数值 `value`（不能用布尔值）、非空 `unit`, `applicability`, `source`, `edition`, `clause`；`evidence_status` 必须为 `reviewed`。
- 每个已选的 `earthworks`/`road`/`drainage` 范围至少一条 criteria，便于发现完全没有依据的范围；**一条绝不代表覆盖该范围全部设计条件**。survey/automation 可以空数组。无需此表的简单教学不必运行检查器。
- 每条 criterion 的 `basis_jurisdiction` 固定 `MY`，意思是已确认马来西亚项目的采用依据。原始参考若来自国外，另填 `external_reference`，并填写 `malaysian_adoption_evidence` 说明本项目为何允许采用；不接受静默以 EU/US 默认条件替代。

示例文件的 `null` 是刻意保留的待填项，运行应得到 `incomplete`（退出 1）。脚本拒绝常用占位文字 `TBD/unknown/unverified/待确认/未核验` 等，但不可能识别所有伪造或语义上不完整的文本。输出仍须人工审阅。

退出码：`0` 元数据格式检查通过，`1` 缺项/字段问题，`2` 文件或 JSON 解析失败。所有报告含 `engineering_compliance_checked: false`。不得把该字段删掉后将报告包装成 JKR/MSMA 合格证。
