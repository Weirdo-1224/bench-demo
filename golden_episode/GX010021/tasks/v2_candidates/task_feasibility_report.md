# GX010021 Session 3：任务有效性筛选

日期：2026-10-11（Asia/Shanghai）。最高依据为 [Benchmark Overall Design V1.0](../../../../docs/Long_Horizon_Streaming_Agent_Benchmark_Overall_Design_v1.0%20%281%29.md)，尤其§3.1、§4、§5、§6.4、§7。所有事实和答案均为 CANDIDATE / NOT_REVIEWED；Gold=0。未调用视频模型，未重新分析全片。

共保存12条任务定义：9条候选（4 PILOT_CANDIDATE、5 NEEDS_EVIDENCE）和3条 UNSUITABLE 剔除记录。任务状态是可用性分类，不能替代标注成熟度。PILOT_CANDIDATE只允许候选诊断评分，所有 hard_score_eligible=false。

|任务 ID（统一前缀 GX010021-V2-）|子任务|状态|触发/媒体秒|
|---|---|---|---|
|T1-001|T1.1|PILOT_CANDIDATE|200.3 / 239.3|
|T1-002|T1.2|PILOT_CANDIDATE|431.2308 / 445.211433|
|T1-003|T1.2|PILOT_CANDIDATE|680.212867|
|T1-004|T1.3|NEEDS_EVIDENCE|630.2|
|T2-001|T2.1|NEEDS_EVIDENCE|200.3|
|T2-002|T2.2|NEEDS_EVIDENCE|641.3|
|T2-003|T2.3|PILOT_CANDIDATE|680.212867|
|T2-004|T2.2|UNSUITABLE|200.3|
|T3-001|T3.1|NEEDS_EVIDENCE|完整Episode 0–696.929567；私有局部评分范围|
|T3-002|T3.1|NEEDS_EVIDENCE|完整Episode 0–696.929567；私有局部评分范围|
|T3-003|T3.1|UNSUITABLE|完整Episode 0–696.929567；私有局部评分范围|
|T3-004|T3.3|UNSUITABLE|完整Episode 0–696.929567；私有局部评分范围|

## GX010021-V2-T1-001 — 首轮搅拌的进行与动作段完成

**判断：PILOT_CANDIDATE**。

- **能力定义**：符合T1.1，读取主轨迹状态，不用问答触发。
- **事实与证据**：起止锚点来自V2保留的历史视觉定位；模型止225与历史止235有边界分歧。
- **客观评分**：两个检查点可候选枚举评分；没有真实首次可见完成时刻，Update Delay关闭。
- **未来信息及捷径**：200.3只用199.2锚点，不使用198–225整段模型定位；完成时239.3引用均已结束。
- **能力必要性**：第一检查点近期即可答；第二检查点要求维护已完成动作段，但不能证明长程可靠性。
- **定向缺口**：G02（见 [evidence_gaps.md](evidence_gaps.md)）。

候选参考（私有，非Gold）：

```json
{
  "checkpoints": [
    {
      "at": 200.3,
      "first_mixing_progress": "in_progress"
    },
    {
      "at": 239.3,
      "first_mixing_progress": "completed"
    }
  ],
  "completion_definition": "仅本轮搅拌动作段结束：已进入液面，随后提离并放置；不评价均匀程度或全部规范完成",
  "cancelled": "NOT_ASSERTED"
}
```

必要证据集合：

- progress-begin：H1-V-E027-01（搅拌棒进入液面）。集合状态 CANDIDATE_MINIMAL_UNVERIFIED；最小充分性未验证。
- progress-stop：H1-V-E027-01（已开始）；H1-V-E027-03（棒提离）；H1-V-E028-01（打蛋器放置）。集合状态 CANDIDATE_MINIMAL_UNVERIFIED；最小充分性未验证。

评分字段：first_mixing_progress@200.3；first_mixing_progress@239.3。输出unknown/uncertain分别记录，未裁决字段不进入硬评分分母。

## GX010021-V2-T1-002 — 玻璃容器内黄色材料的局部固液状态

**判断：PILOT_CANDIDATE**。

- **能力定义**：符合对象可观察属性跟踪。
- **事实与证据**：两张已校验PTS的原帧；完全融化模型主张与之冲突，优先限定直接可见属性。
- **客观评分**：visible_phase可按枚举候选评分，比例和最终相态不进入准确率分母。
- **未来信息及捷径**：不使用V2-V19的完全融化断言，也不以445秒帧评分431秒。
- **能力必要性**：近期视觉足以回答局部属性；用于调试未知处理，两个点不证明中间持续状态。
- **定向缺口**：G01、G02（见 [evidence_gaps.md](evidence_gaps.md)）。

候选参考（私有，非Gold）：

```json
{
  "checkpoints": [
    {
      "at": 431.2308,
      "visible_phase": "liquid_and_solid"
    },
    {
      "at": 445.211433,
      "visible_phase": "liquid_and_solid"
    }
  ],
  "solid_fraction": "unknown",
  "final_phase_at_pour": "unknown"
}
```

必要证据集合：

- phase-first：LC-431-2（第一次检查点固液共存）。集合状态 CANDIDATE_MINIMAL_UNVERIFIED；最小充分性未验证。
- phase-second：LC-445-2（第二检查点仍见固态材料）。集合状态 CANDIDATE_MINIMAL_UNVERIFIED；最小充分性未验证。

评分字段：visible_phase@431.2308；visible_phase@445.211433。输出unknown/uncertain分别记录，未裁决字段不进入硬评分分母。

## GX010021-V2-T1-003 — 入模后烤模内容与主容器残留

**判断：PILOT_CANDIDATE**。

- **能力定义**：符合对象内容状态，避免把刮净动作等同清空。
- **事实与证据**：已有局部原帧直接候选支持面糊和残留。
- **客观评分**：两个可见字段可枚举评分；实际转移比例不评分。
- **未来信息及捷径**：单帧不推断放工具/合盖事件，680秒不提前读取入炉后画面。
- **能力必要性**：近期可答，作为T1接口与对象区分调试；没有长程必要性主张。
- **定向缺口**：G01（见 [evidence_gaps.md](evidence_gaps.md)）。

候选参考（私有，非Gold）：

```json
{
  "pan_contents": "batter_visible",
  "main_container_residue": "visible",
  "transferred_fraction": "unknown"
}
```

必要证据集合：

- pan-residue：LC-680-2（烤模面糊与主容器残留）。集合状态 CANDIDATE_MINIMAL_UNVERIFIED；最小充分性未验证。

评分字段：pan_contents@680.212867；main_container_residue@680.212867。输出unknown/uncertain分别记录，未裁决字段不进入硬评分分母。

## GX010021-V2-T1-004 — 晚期粉状表层到光滑表面的状态转移

**判断：NEEDS_EVIDENCE**。

- **能力定义**：符合T1.3，评测状态变化而非搅拌动作识别。
- **事实与证据**：光滑终态只有历史报告；局部610.2096只支持棒在容器内。
- **客观评分**：缺首次可观察变化、身份持续性和边界复核，转移F1/Delay不可硬算。
- **未来信息及捷径**：不将605–631搅拌段整段当转移时刻，不用610帧虚构光滑终态。
- **能力必要性**：需要前后状态记录；是否具长程稳定性不能由27秒包络判定。
- **定向缺口**：G02、G03（见 [evidence_gaps.md](evidence_gaps.md)）。

候选参考（私有，非Gold）：

```json
{
  "before": "powder_on_surface",
  "after": "smooth_surface",
  "transition_bracket": {
    "earliest": 603.2,
    "latest": 630.2
  },
  "first_observable_time": null,
  "bracket_semantics": "由已有两种状态观察端点推导的粗包络，不是连续动作真值",
  "surface_transition": {
    "before": "powder_on_surface",
    "after": "smooth_surface"
  }
}
```

必要证据集合：

- surface-transition：H1-V-E051-02（603.2粉状表层）；H1-V-E052-02（630.2光滑表面）。集合状态 CANDIDATE_MINIMAL_UNVERIFIED；最小充分性未验证。

评分字段：surface_transition@630.2。输出unknown/uncertain分别记录，未裁决字段不进入硬评分分母。

## GX010021-V2-T2-001 — 首轮搅拌时核查加奶前置要求

**判断：NEEDS_EVIDENCE**。

Probe题面：当前搅拌正在进行。此前关于加奶和搅拌的要求是否已经由实际操作满足？请区分进入容器与用量这两个条件，给出结论、历史证据和不能确定的部分。

- **能力定义**：规范明文顺序可作为前置要求候选，不依赖模型时序关系。
- **事实与证据**：视觉加奶链有候选；规则公开与容量/同一性缺失。
- **客观评分**：可定义decision和事实字段，但暂不评分；unknown仍需可观察性裁决。
- **未来信息及捷径**：只用199.2开始锚点；近期搅拌外观无法确定奶量，题面也未给量值。
- **能力必要性**：奶是否加入可能只需单个转移证据；完整量值判断是否需要历史尚未证明。
- **定向缺口**：G04、G05、G08（见 [evidence_gaps.md](evidence_gaps.md)）。

候选参考（私有，非Gold）：

```json
{
  "decision": "unknown",
  "milk_entered_container": "observed",
  "half_cup_satisfied": "unknown",
  "qualification": "不由单次量取或1/4 CUP标签断言不足半杯；不由加奶发生推导定量满足"
}
```

必要证据集合：

- milk-precondition-and-volume-limit：SRC-R18（半杯要求）；H1-V-E022-01（实际量取）；H1-V-E023-01（实际加入）；H1-V-E027-01（当前开始锚点）；H1-V-E020-02（早期1/4 CUP标签）。集合状态 INSUFFICIENT；最小充分性未验证。

评分字段：decision@200.3；milk_entered_container@200.3。输出unknown/uncertain分别记录，未裁决字段不进入硬评分分母。

历史判断：在搅拌画面中无法辨认早期盒杯转移和实际量取；移除量取历史应降低证据覆盖，但unknown可能成为默认捷径。dependency_span_sec=null，source_label_span_sec=65.552。有规则的两题和剔除题只记录来源定位跨度，不把标签时间当已公开必要历史。

## GX010021-V2-T2-002 — 入模时核查烤模处理指令的修订范围

**判断：NEEDS_EVIDENCE**。

Probe题面：当前面糊正在进入烤模。根据此前指导对话，本次烤模处理应遵循哪些有效要求？说明替代方案、适用对象与条件，并区分实际可见操作和无法确认的结果。

- **能力定义**：符合规则覆盖和条件适用；没有临界时刻修订前后配对。
- **事实与证据**：文本语境支持限定许可候选，原片不能验证说话时段。
- **客观评分**：规则生效时间未定，641.3只是候选Probe时间；不能把条件答案当当时有效Gold。
- **未来信息及捷径**：当前锚点用633.2–641.2，排除633–678全段模型证据；全对话不在题面提供。
- **能力必要性**：若近期可见许可/当前规范已显式含范围，历史未必必要；须做当前指令/单句消融。
- **定向缺口**：G04、G06、G08（见 [evidence_gaps.md](evidence_gaps.md)）。

候选参考（私有，非Gold）：

```json
{
  "effective_rule": "unknown_until_release_verified",
  "conditional_reference": {
    "choice": "oil_permitted",
    "scope": "this_pan_lining_only",
    "conditions": [
      "speaker_claim_no_parchment",
      "speaker_claim_no_leftover_butter"
    ],
    "inner_wall_coverage": "unknown",
    "superseded_options": [
      "parchment_option",
      "leftover_butter_option"
    ]
  }
}
```

必要证据集合：

- pan-rule-context：SRC-R39（原垫纸要求）；SRC-R40（无纸自述条件）；SRC-R41（剩余黄油方案及范围）；SRC-R42（无剩余黄油自述及用油提议）；SRC-R43（许可）；H1-V-E049-01（模底液体观察）；H1-V-E053-01（当前入模锚点）。集合状态 INSUFFICIENT；最小充分性未验证。

评分字段：conditional_reference.choice@641.3；conditional_reference.scope@641.3。输出unknown/uncertain分别记录，未裁决字段不进入硬评分分母。

历史判断：仅Yes句不能稳定消解对象用途；删R41/R42应损害范围/条件字段，保留当前有效完整规范可能消除此增益。dependency_span_sec=null，source_label_span_sec=102.602。有规则的两题和剔除题只记录来源定位跨度，不把标签时间当已公开必要历史。

## GX010021-V2-T2-003 — 入模后奶和粉的材料传递证据整合

**判断：PILOT_CANDIDATE**。

Probe题面：观察当前烤模中的混合物。请根据此前实际可见操作，说明奶和粉如何进入混合过程、经由哪些容器，以及它们与当前烤模内容的候选联系。区分量取与真正入料，指出数量和身份不能确认的地方。

- **能力定义**：符合T2.3跨阶段对象传递整合；不是必然依赖/仅回忆材料列表。
- **事实与证据**：链节点均有既有V2或保留历史定位；晚期原帧只佐证阶段，完整路径与持续身份仍候选。
- **客观评分**：可以调试结构化路径和证据覆盖；仅候选评分，不硬评分身份/数量/质量守恒。
- **未来信息及捷径**：问题不提示两条粉路径；680.212867之后的入炉证据不使用；不把V2-R9先后关系升级依赖。
- **能力必要性**：近期面糊外观通常不能还原153–291秒路径，是可检验假设；当前物品/菜谱常识仍可能猜材料，要同时看路线和证据。
- **定向缺口**：G05、G07、G08（见 [evidence_gaps.md](evidence_gaps.md)）。

候选参考（私有，非Gold）：

```json
{
  "milk_route": [
    "milk_carton",
    "measuring_utensil_observation",
    "main_container"
  ],
  "flour_routes": [
    [
      "flour_bag",
      "measuring_utensil_observation",
      "main_container"
    ],
    [
      "flour_bag",
      "main_container"
    ]
  ],
  "downstream_route": [
    "main_container",
    "baking_pan"
  ],
  "observed_flour_entry_segments": 2,
  "measuring_only_segment_counts_as_entry": false,
  "physical_utensil_identity": "unknown",
  "material_continuity": "candidate_not_verified",
  "total_volume": "unknown",
  "complete_transfer": "unknown"
}
```

必要证据集合：

- material-lineage：H1-V-E022-01（奶盒到量具）；H1-V-E023-01（奶从量具到主容器）；H1-V-E031-01（粉袋到量具）；H1-V-E032-01（粉从量具到主容器）；H1-V-E051-01（晚期袋到主容器候选直接路径）；V2-V24（主容器到烤模）；LC-680-2（当前烤模内容锚点）。集合状态 CANDIDATE_MINIMAL_UNVERIFIED；最小充分性未验证。

评分字段：milk_route@680.212867；flour_routes@680.212867；downstream_route@680.212867。输出unknown/uncertain分别记录，未裁决字段不进入硬评分分母。

历史判断：保持680秒画面与题面相同，近期窗口不能直接恢复早期奶的两段转移和第一条粉路径；移除任一核心段应降低路径或证据覆盖，不预设答案准确率正差。dependency_span_sec=527.012867，source_label_span_sec=527.012867。有规则的两题和剔除题只记录来源定位跨度，不把标签时间当已公开必要历史。

## GX010021-V2-T2-004 — 只问当前糖量的修订单句回忆

**判断：UNSUITABLE**。

Probe题面：当前糖量目标是多少？

- **能力定义**：单句规则Recall不满足T2核心多事实/规则关系要求。
- **事实与证据**：文本有糖量修订候选，但实际用量及公开时间缺失。
- **客观评分**：即使补公开时间也不能解决任务机制不足。
- **未来信息及捷径**：题目可由当前有效规则或单句直接作答。
- **能力必要性**：没有多证据历史必要性；列为剔除记录，不能为覆盖凑数。
- **定向缺口**：G04、G08（见 [evidence_gaps.md](evidence_gaps.md)）。

候选参考答案为null；此定义不得执行或评分。

必要证据集合：

- single-sugar-rule：SRC-R16（单句可回答当前目标）。集合状态 INSUFFICIENT；最小充分性未验证。

历史判断：不成立：本定义是单句Recall，应重设计后另建任务。dependency_span_sec=null，source_label_span_sec=72.732。有规则的两题和剔除题只记录来源定位跨度，不把标签时间当已公开必要历史。

## GX010021-V2-T3-001 — 许可用油处理烤模的限定负例

**判断：NEEDS_EVIDENCE**。

- **能力定义**：主形式为全Episode自主监测；负例只能检查限定误报，不能替代T3正例能力。
- **事实与证据**：L5-06正常候选有文本许可与视觉定位，但公开时间缺失。
- **客观评分**：限定负例定义已明确；当前不能开启候选报警评分或全片FA/h。
- **未来信息及捷径**：排除V2-E25所引未来V2-V24，不以Success当正常真值；不向Agent发负例窗口或silence答案。
- **能力必要性**：连续报警轨迹可审计误报；始终沉默系统也可通过负例，无法证明发现/及时/恢复。
- **定向缺口**：G04、G06、G09（见 [evidence_gaps.md](evidence_gaps.md)）。

候选参考（私有，非Gold）：

```json
{
  "expected_behavior": "silence_for_scoped_permitted_substitution",
  "scope": [
    "missing_parchment_only",
    "not_using_leftover_butter_only"
  ],
  "other_anomalies": "NOT_LABELED",
  "inner_wall_coverage": "unknown"
}
```

必要证据集合：

- oil-negative：SRC-R39（原垫纸要求）；SRC-R40（无纸自述）；SRC-R41（剩余黄油建议）；SRC-R42（无黄油并提议油）；SRC-R43（限定许可）；H1-V-E049-01（模底油候选）；H1-V-E049-02（倾转烤模候选）。集合状态 INSUFFICIENT；最小充分性未验证。

持续执行：没有逐题输入、没有窗口重启。normal_intervals=[{"start_time":560.2,"end_time":579.2,"status":"CANDIDATE_SUBSET_OF_L5_06_NOT_NORMAL_FOR_ALL_CLASSES","evidence_ids":["H1-V-E049-01","H1-V-E049-02"]}]；正异常、检测时刻、截止点、反馈公开时刻和恢复时刻均未构造，全部null或空集合。

## GX010021-V2-T3-002 — 分段黄油再加热的潜在正常负例

**判断：NEEDS_EVIDENCE**。

- **能力定义**：全Episode持续监测的正常流程研究候选；非问答。
- **事实与证据**：L5-07没有候选正常区间；V2定位只支持动作候选。
- **客观评分**：无经核验正常窗口与规则时间，暂不评分；不硬填405–410正常真值。
- **未来信息及捷径**：SRC-R31是反馈身份，不能视作自主检测证据；不造15秒实际加热结论。
- **能力必要性**：可用于持续误报控制，无法测纠错恢复；需要额外正例。
- **定向缺口**：G04、G09、G10（见 [evidence_gaps.md](evidence_gaps.md)）。

候选参考（私有，非Gold）：

```json
{
  "expected_behavior": "do_not_label_reheat_alone_as_error",
  "normal_interval": null,
  "heating_duration": "unknown",
  "recovery_event": "NOT_ASSERTED"
}
```

必要证据集合：

- reheat-negative：SRC-R30（分段加热检查规范候选）；SRC-R31（进一步加热反馈候选）；V2-V17（取出部分融化材料）；V2-V18（再加热操作）。集合状态 INSUFFICIENT；最小充分性未验证。

持续执行：没有逐题输入、没有窗口重启。normal_intervals=[]；正异常、检测时刻、截止点、反馈公开时刻和恢复时刻均未构造，全部null或空集合。

## GX010021-V2-T3-003 — 把取蛋或反馈直接当三蛋入料错误

**判断：UNSUITABLE**。

- **能力定义**：形式可持续监测但原错误定义没有成立。
- **事实与证据**：第三枚破损/入料与规范公开时间不明。
- **客观评分**：没有可评分异常正例，候选答案为null。
- **未来信息及捷径**：反馈标签/模型三蛋主张不能成为error_onset或detectable_from。
- **能力必要性**：错误事实未成立，不能测检测能力。
- **定向缺口**：G04、G09、G11（见 [evidence_gaps.md](evidence_gaps.md)）。

候选参考答案为null；此定义不得执行或评分。

必要证据集合：

- egg-error-rejected：LC-76-2（只见两个蛋黄）；LC-83-2（手持蛋但完整性/去向未知）；SRC-R10（反馈文本仅作审计背景）。集合状态 INSUFFICIENT；最小充分性未验证。

持续执行：没有逐题输入、没有窗口重启。normal_intervals=[]；正异常、检测时刻、截止点、反馈公开时刻和恢复时刻均未构造，全部null或空集合。

## GX010021-V2-T3-004 — 把正常再加热当错误恢复与解除

**判断：UNSUITABLE**。

- **能力定义**：有持续形式，但恢复要求已确认偏差和纠正；本定义不符合T3.3事实前提。
- **事实与证据**：没有成立错误、纠正完成或后续第二错误。
- **客观评分**：resolved_at保持null，不能评解除延迟。
- **未来信息及捷径**：不把再次加热或模型完全融化当恢复；不造deadline。
- **能力必要性**：继续观看正常加热不等于错误恢复能力。
- **定向缺口**：G09、G10（见 [evidence_gaps.md](evidence_gaps.md)）。

候选参考答案为null；此定义不得执行或评分。

必要证据集合：

- recovery-rejected：V2-V17（部分融化取出）；V2-V18（进一步加热）；LC-431-2（后续仍有固块）。集合状态 INSUFFICIENT；最小充分性未验证。

持续执行：没有逐题输入、没有窗口重启。normal_intervals=[]；正异常、检测时刻、截止点、反馈公开时刻和恢复时刻均未构造，全部null或空集合。

## 候选评分规则与边界

T1的状态字段按指定检查点读取主轨迹输出；进度以动作段开始/结束为定义，不以Success或规范完成代替。确定值与unknown/uncertain分开统计，未知字段不强制猜测。可候选比较字段一致率，但没有审定区间、首次可观察时刻或δ_state时，不计算硬Transition F1、Update Delay或Drift。

T2材料路径按payload_schema公开的通用节点词表输出：单条路径节点有序，多条路径集合无序；量具为观察组，不能要求Agent复现私有标注ID。按私有reference_items比较候选路径字段；证据需用Runner公开observation_id及媒体时段，Evaluator再映射到私有证据集合。必要证据覆盖与额外无关片段需分开统计；IoU阈值与容差待Dev冻结，不伪造数值。诊断分不能当长程增益或Gold正确率。

T3仅能在限定类别和经核验的正常范围审计误报：用油负例只涉及“单因没有垫纸/没有使用剩余黄油”而报警，再加热负例只涉及“单因分段再加热”而报警。其他问题NOT_LABELED。按incident_id聚合raise/update/resolve，一次错误的重复报警不能重复计数。当前两个负例都禁用评分；补规则时刻和正常范围后也不能凭局部负例报全片FA/h、Recall、F1、Timely Recall或Recovery Tracking。始终沉默会通过纯负例，必须补正例才能评价T3核心能力。

## L5七条数据审计

|L5|类型|结论|
|---|---|---|
|L5-01 small_bowl_feedback|未确认偏差/反馈|缺容量规则与提前可检测证据；换容器不是已审定纠正，未生成正例|
|L5-02 extra_egg_feedback|未确认偏差/反馈|取蛋不等于加入；第三枚破损/去向未知，T3-003剔除|
|L5-03 sugar_amount_feedback|未确认偏差/反馈|实际量未知且可能获修订许可；不构造糖过量错误|
|L5-04 butter_reheat|未确认偏差/反馈|部分融化/再加热可能属正常分段流程，不构造恢复|
|L5-05 late_flour_addition|未确认偏差/反馈|“不必加”不等于“禁止加”；稀稠与用量未知，不构造违规|
|L5-06 permitted_oil_normal_candidate|限定正常候选|生成T3-001，规则时刻未定；正常子区间560.2–579.2来自既有定位，与原560–581候选范围相容|
|L5-07 reheat_normal_candidate|正常流程候选|生成T3-002但不填正常区间；原L5区间为null，事件405–410不自动变成整段正常真值|

## 对旧8个Pilot定义的处理

旧T1-001搅拌完成保留并增加开始检查点；旧T1-002相态改成两个原帧快照；旧T1-003光滑转移降为NEEDS_EVIDENCE；旧T1-004入炉/门关闭因末段边界与未来证据混淆不迁移，另用680.212867原帧入模内容定义T1-003。旧T2三题分别对应奶前置、烤模修订与材料链；前两题受指导公开时间门禁，材料链删去入炉末段与不必要奶量要求，固定680秒当前锚点。旧T3用油负例保留持续形式并保持待证据状态，新增已有L5再加热正常候选。未修改旧任务或V1/V2标注。
