# 覆盖范围与开放问题

## 已核实的当前口径

- V1：56 事件；22 对象/引用记录（15 基线对象 + 7 后增引用）；115 状态条目；14 个开放复核项。
- V2：59 事件、28 对象/观察组、138 状态、13 观察步骤、24 关系、192 证据定位、7 个 L5 候选；0 confirmed errors、0 gold records。
- Session3：12 定义、9 保留、3 UNSUITABLE；4 PILOT_CANDIDATE、5 NEEDS_EVIDENCE、3 UNSUITABLE；Gold=0。
- Session4A：12/12 张既有真实帧已复制，未新抽帧。

## 与历史锚点不一致

历史提示中的 V2 “38 状态、3 步骤、4 关系、92 证据”与当前权威文件不一致。当前 `objects.json#/states` 是 138，其中 manifest 明列 15 模型状态、115 历史状态和 8 快照状态；`procedure.json#/observed_steps` 为 13；`relations.json#/records` 为 24；`evidence_index.json#/records` 为 192。本包不修改源数据，只在 `stage_metrics.csv` 标出统计口径。

历史提示中的 V1 “4 待复核项”也不等于当前 `review_queue.json` 的 14 个 open items；4 可能来自更窄的旧摘要口径，当前文件没有足够证据把 14 改成 4。

## 历史校验状态

现存 `reports/validation_results.json` 的原始结果为 `passed=false`，唯一列出的 error 是 `Input SHA256 changed: annotation_reports/README.md`。本包把这项历史失败原样保留在 `source_snapshots/v1/reports/validation_results.json`；它与本次导出包的 JSON、ID、时间、媒体、秘密扫描和 ZIP 验收全部通过不是同一层校验，不能相互覆盖。

## G01–G11 开放缺口摘要

- G01–G03：T1 原帧独立裁决、首次可观察边界、晚期光滑终态仍缺。
- G04：无音轨，指令/反馈的 availability/effective_from 为空。
- G05–G08：量具身份、许可语境、粉料持续性及历史必要性实验未完成。
- G09–G10：可信异常正例与真实纠正/恢复链缺失，因此 Track3 不能报 Recall/F1，也不能造 Gold。
- G11：第三枚蛋的破损、入料和最终去向未定。

## 四案例可视化充分性

- T1-002：足以展示双时点“固液共存”和因果边界；不足以展示持续状态、固体比例或最终融化。
- T2-003：足以展示 6 条候选关系边和 7 个证据定位；不足以确认物理量具身份、质量守恒、体积、完全转移和历史必要性。
- T3-001：足以展示“允许替代导致单一路径报警不可靠”；不足以建立正式正常 GT 或在线规则生效时刻。
- T3-002：足以展示证据不足；Session4A 没有直接绑定帧，且缺可证偏差、纠正、恢复与报警起点，因此不补造异常正例。
