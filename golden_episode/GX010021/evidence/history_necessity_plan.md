# T2 历史必要性实验方案（配置阶段，未执行）

日期：2026-10-09，Asia/Shanghai。仅覆盖现有 `GX010021-T2-002` 与 `GX010021-T2-003`，保持原问题、检查点、答案字段和Track定义。实验结果、分数与历史必要性结论均为空；本轮没有实现Runner/Evaluator，没有调用模型作答。

本文件含私有证据定位及实验掩码，**仅供内部实验组织者**。不要把本文件、manifest、历史报告、候选答案、裁决表、对象图或私有证据ID提供给被评测Agent。盲审者应只收到其任务的清单与视频。

## 执行前门禁

当前可准备视频及文本诊断，尚不能按原G1协议运行完整实验：源MP4无音频流；原始对话只有单点 `text_timestamps`，没有话段结束或实际送达日志；规则 `effective_from` 与真实 `availability_time` 仍未核验。配置状态为 `PLANNED_NOT_EXECUTED`，G1启动门禁为 `BLOCKED_UNTIL_RELEASE_TIMES_AND_MEDIA_REGIME_VERIFIED`。

独立核验后，先冻结可评分事实、可判定性、必要证据集合和任务级最早可回答时间，再冻结真实信息公开表。每条对话至少记录 `source_record_id / utterance_start / utterance_end / availability_time / channel / effective_from / scope`，无证据的字段保留null。不得把点标签、下一条标签或剪辑结束当作话段结束或公开时刻；不得为了运行实验人为指定延迟。对于实际话语真实性与文本语义分别记录证据基础。

若无法取得原音轨或可信的真实公开记录，原G1实验继续暂缓；可以以后另行预注册“无音轨、外部文字指令”的诊断profile，但须有可核查的真实文字发布记录，不把该profile混入原G1结果。本轮没有建立任何模拟送达时间或执行该诊断。

## 固定时间边界和公共信息契约

| 任务 | query_time / observation_cutoff（秒） | 候选最早可回答包络（未核验） | 主Recent-only窗口，W=30秒 | W=10 / 60 / 120秒窗口起点 |
|---|---:|---|---|---|
| GX010021-T2-002 | 641.300 | 633.200–641.200 | 611.300–641.300 | 631.300 / 581.300 / 521.300 |
| GX010021-T2-003 | 692.300 | 687.200–692.000 | 662.300–692.300 | 682.300 / 632.300 / 572.300 |

源帧可见性按帧PTS裁剪；截至query_time之后没有任何源帧或晚到文字可见。裁切精度使用 `clips/time_mapping.csv` 的整数PTS与time_base。最后一帧的显示持续时间可以跨界不足一帧，但该帧本身的源PTS必须小于截止。不得拿整段文件播放长度代替请求观察截止。

问题及 `answer_type` 只在 `query_time` 公开，逐字使用原任务的这两字段；本轮不把候选标题、参考事实、私有ID、earliest_answerable_time或答案性提示加入题面。T1状态、其他Probe问题或任何候选答案都不能成为这些T2条件的输入。

所有条件共享一个预注册的“当前指令”接口。建议主诊断接口采用运行系统本来持有的**最近已实际送达的原始Instruction原文**作为当前指令，不改写、不汇总规则链，不从私有标注替Agent选择有效规则。Recent-only另外收到窗口内实际送达的其他原始对话。源点标签定位的候选当前Instruction分别是R52（630.612秒）和R54（686.478秒），**仅为定位，不确认在query_time前已送达**；实际选择必须按公开表，若不满足则回退到更早已公开的原指令。

这是对“当前指令”的拟议实验接口，须在执行前与真实系统公开契约一起冻结。如果真实公开接口持有多个仍有效的规则，所有条件必须如实接收同一组当时公开的原文，不能为增加Full-history优势而删掉Recent-only的合法当前指令。若该接口已经合法复述了完整替代链，应单独标记语言捷径，并允许无历史条件答对。不能用离线整理的“当前用油已许可”结论补成输入。候选当前指令的选择代码、私有注释与必要证据列表均不得可见。

## 四类条件

| 条件 | 可见视频/原音频 | 可见文字/指令 | 历史状态与工具范围 | 目的 |
|---|---|---|---|---|
| Full-history | 从0至t_q按因果顺序送达的全部合法观察；源音轨缺失须先解决G1门禁 | 只含真实availability≤t_q的原对话，按原时刻送达；共享当前指令接口 | 可以访问已经公开的过去观察和自己的记忆，不能访问未来或私有参考 | 给出同模型下完整合法历史的诊断参照，不是神谕 |
| Recent-only | 仅[t_q−W,t_q)帧及同窗合法音频 | 该窗口内已送达的对话，加共享当前指令；没有窗口外对话摘要 | 丢弃窗口前所有记忆、缓存、检索索引和工具结果；工具只能访问本条件输入 | 检验是否可由最近画面/原指令解决 |
| Instruction-only | 不含视频、帧、缩略图或音频感知 | 截至t_q真实已公开的完整原对话，包含Instruction、Clarification及上下文自述；Success/Feedback按选定visibility profile一致控制 | 仅能访问条件内文字及自身生成的文字状态 | 检验语言和菜谱捷径；不把这类文本自述当视觉事实 |
| Evidence Ablation | 从Full-history出发遮蔽预注册的特定源区间；其余合法视频保持 | 同时遮蔽被删除证据的原文字、音频和其他副本；共享当前指令若包含同事实，记录残余证据而不偷偷删改接口 | 必须从缺失该证据的历史重新构建记忆，不能在完整历史已写入记忆后仅删媒体文件 | 检验证据非冗余性及替代来源；删除不预设性能下降 |

单次完整Episode运行中，T2问题使用只读隔离分支，回答后丢弃问题、答案、工具痕迹和分支记忆，主轨迹不被Probe污染。各Track继续共享同次主轨迹；Recent-only的历史限制属于诊断条件，应单列其受限主轨迹或可证明等价的无历史分支，不能声称仍是未受限持续Agent。Instruction-only与Ablation同样使用各自输入生成的状态，不借用Full-history缓存。隔离实现和合规性属于后续阶段，本轮不开发。

主W=30秒；W=10、60、120为敏感性诊断。T2-002的120秒窗口已覆盖538.698秒等候选早期对话，可能包含完整历史链，应报告证据落入比例，不把这一窗口的结果算作远距证据已被移除。

## T2-002删除配置

| 掩码ID | 定位来源 | 删除单位及边界 | 保留内容 | 比较输出字段 |
|---|---|---|---|---|
| D02-R39 | T-R39，源R39点538.698 | R39整句真实话段音频及实际公开文本；区间起止须核验后填写 | 其他对话及视觉 | effective_choice / applicable_scope / context_conditions |
| D02-R40 | T-R40，R40点544.398 | 同上，仅R40 | 其他对话及视觉 | context_conditions |
| D02-R41 | T-R41，R41点546.378 | 同上，仅R41 | 其他对话及视觉 | scope、替代关系的解释及证据 |
| D02-R42 | T-R42，R42点552.478 | 同上，仅R42 | 其他对话及视觉 | context_conditions / scope |
| D02-R43 | T-R43，R43点556.368 | 同上，仅R43 | 其他对话及视觉 | effective_choice |
| D02-DIALOGUE | R39–R43 | 组合删除上述已核验整句话段和所有真实文字副本；不补造下一条标签作为终点 | 倒瓶、持模和当前转移画面 | 许可与视觉状态分离 |
| D02-ENTRY | V-E049-01 | 视频[558,564)秒为预注册候选遮罩，源音频同时间遮罩；相关文字若直接披露该实际动作，另列并删除 | 后续姿态、对话和当前锚点 | factual_state的进入动作 |
| D02-POSE | V-E049-02 | 视频/音频[563,581)秒；相关动作复述一并删除 | 进入、对话和当前锚点 | factual_state中的姿态及inner_wall_coverage |
| D02-PREP | V-E049-01/02 | [558,581)视频/音频及同事实文字 | 完整合法对话和当前锚点 | 规范许可与实际操作的区分 |
| D02-BRIDGE | G05 | [581,632)视频/音频及同事实副本 | 两端操作和原对话 | 烤模身份及不确定性、依据质量 |
| D02-CURRENT | V-E053-01 | [632,641.3)视频/音频及同事实复述 | 先前合法历史 | 当前锚点必要性；仅诊断，不更改原题 |

真实话段区间目前均为null，因此对话删除条件不能运行。视觉掩码不代表动作精确边界；独立核验之后核对范围是否遗漏同一动作其他帧。删除时不得保留已缓存关键帧、字幕、音频转写或summary中的该事实。原题自身若披露当前动作，应记录题面残余提示，不改写原题以制造退化。

## T2-003删除配置

| 掩码ID | 私有定位 | 候选遮罩（原媒体秒） | 待比较字段 |
|---|---|---|---|
| D03-MILK-UP | V-E022-01 | [152,158) | milk_path上游边、证据及不确定性 |
| D03-MILK-DOWN | V-E023-01 | [158,166) | milk_path下游边 |
| D03-MILK-CHAIN | 上述二者 | [152,166)及直接披露该路径的合法文字副本 | 奶路径是否能被其他来源恢复 |
| D03-FLOUR-UP | V-E031-01 | [269,283) | flour_paths上游边，量取与入容器的区分 |
| D03-FLOUR-DOWN | V-E032-01 | [283,293) | 首段供粉到混合容器边 |
| D03-FLOUR-LATE | V-E051-01/02 | [594,605)及同事实文字（如已实际送达的R49） | 后段供粉路径、可见加入计数 |
| D03-TRANSFER | V-E053-01/02 | [632,679) | downstream_path转移边；不能只删初段却保留后续刮取 |
| D03-OVEN | V-E055-01 | [687,692.3) | 当前去向；题面残余提示须单列 |
| D03-CUP-BRIDGE | G01/G03 | [156.2,159.2)与[281.2,287.2)，分别运行再组合 | 局部杯连续身份及校准弃权 |
| D03-MIXTURE-BRIDGE-A | G02 | [161.2,269) | 奶加入后到首段供粉的材料延续 |
| D03-MIXTURE-BRIDGE-B | G04 | [293,594) | 长时对象/材料延续、不能凭ID或首尾默认连续 |
| D03-MIXTURE-BRIDGE-C | G06 | [605,632) | 后段混合至开始转移的延续 |
| D03-PAN-BRIDGE | G07 | [641.3,687) | 接料烤模至入炉连续性；记录端点与保留刮取是否仍充分 |

所有上述掩码须同时删除相关音频/文字/已有摘要/帧副本，但不删除仅提出目标量值的指令来伪造不同规则。对于“我要再加粉”这类操作自述，如允许保留，会成为替代证据；主删除配置移除同事实自述，另做“只删视觉”的副诊断并标明残余文字。mask的ID、私有V-/T-引用、对象ID和删除理由均不提供给Agent。

固定时间轴，遮罩可用无语义黑/灰画面和静音（若源音频存在），并仅告知条件有不可用观察。不能拼接缩短历史或移动后续指令时间。对未遮罩的视频维持同一采样频率/分辨率，对被遮罩段不提供原缩略图。掩码范围重叠允许单删和组合，但不要把高度相关删除变体当独立统计样本。

## 待冻结的机器可读配置

以下JSON为计划参数，不是运行器，不含预设答案。`null`门禁字段由独立审核填充后才能执行。

```json
{
  "plan_status": "PLANNED_NOT_EXECUTED",
  "run_enabled": false,
  "episode_id": "GX010021",
  "visibility_regime": "G1_PENDING_SOURCE_AUDIO_AND_RELEASE_AUDIT",
  "availability_manifest": null,
  "source_audio_status": "ABSENT_IN_SOURCE",
  "verified_reference_decisions": null,
  "verified_minimal_evidence_sets": null,
  "query_release": "original question and answer_type only, at query_time",
  "future_access": false,
  "private_reference_access": false,
  "tasks": [
    {"task_id": "GX010021-T2-002", "query_time": 641.3, "cutoff": 641.3, "full_history": [0,641.3], "recent_primary": [611.3,641.3]},
    {"task_id": "GX010021-T2-003", "query_time": 692.3, "cutoff": 692.3, "full_history": [0,692.3], "recent_primary": [662.3,692.3]}
  ],
  "conditions": ["Full-history", "Recent-only", "Instruction-only", "Evidence Ablation"],
  "recent_window_seconds": {"primary": 30, "sensitivity": [10,60,120]},
  "public_current_instruction_contract": "freeze actual runtime contract; raw delivered instructions only; no private rule synthesis",
  "speech_span_end_policy": "verified from independent source only; never inferred from point or next record",
  "text_release_policy": "actual availability <= query cutoff; completion and delivery audited separately",
  "feedback_policy": "same declared visibility regime across conditions, only actually delivered records",
  "ablation_policy": "replay masked history before creating memory; remove multimodal duplicate facts; preserve clock",
  "source_frame_rate": "30000/1001",
  "sampling_hz_for_experiment": null,
  "model_id": null,
  "model_version": null,
  "temperature": null,
  "random_seeds": null,
  "repeats_per_condition": null,
  "budget": {"context_tokens": null,"max_model_calls": null,"max_tool_calls": null,"query_timeout_sec": null},
  "probe_isolation": {"required": true,"write_back": false,"verified": false},
  "scores": null,
  "history_necessity_verdict": null
}
```

## 比较指标与解释边界

固定同一模型/版本、解码参数、问题、输出字段、查询预算和输入采样策略；Full-history可以消耗更多历史观察成本，要实测记录帧数、有效视频时长、上下文token、调用数、检索、内存/GPU时间、真实回答延迟和成本。报告同查询预算的主对照及成本接近的副对照，不能把更多输入成本藏起来。随机重复数、seed和温度按模型支持情况执行前冻结，本轮不填未经试验的数值。

核验后比较：任务整体与分字段准确性；证据对必要转移边/规则来源的覆盖率；无关或未来证据比例；unsupported assertion比例；正确表达不确定性的比例及过度弃权；回答延迟与资源开销。T2-002分别看许可选择、用途范围、自述条件、可见处理动作和表面结果，不由一句yes命中判全题正确；T2-003分别看奶路径、两类供粉路径、下游连接、量取/真正入料区分、杯身份与数量的不确定性，不由命中某个次数判路径重建成立。

`Recent-only Gap = quality(Full-history) − quality(Recent-only)`；`Instruction shortcut score = quality(Instruction-only)`；`Ablation effect = quality(Full-history) − quality(Ablation)`，同时报告证据质量与弃权变化，不能只看结论正误。可替代证据未删尽时，零退化不能证明该证据从不重要；删除后恰当弃权也不能简单当性能失败。评分真值、匹配容差和阈值必须在独立裁决/开发校准后冻结，现阶段均未确定。

只对一个Episode的两个相关Probe做描述性诊断，不能计算有可靠独立样本依据的显著性或排行榜。T2-002单题不支持整组Revision Consistency；不新增未来修订Probe，也不在规则话段尚未结束前借用事后解释。若Recent-only或Instruction-only能够稳定且以合法证据给出完整答案，应记录历史必要性尚未成立，并交后续任务门禁处理；本轮不改变任务或预设降级结论。

## 因果审计与停止条件

后续实验的每次输入记录源媒体时刻、实际availability和wall time；音频话语结束、文字送达与规则生效单独审计。692.608秒R55在T2-003截止692.3之后，必须排除；T2-002不得接收641.3之后的E053刮取/容器终态；提前出现的Feedback/Success也只能按当时真实可见性提供，不把后来反馈倒灌给先前窗口。禁止外部答案库、私有JSON/报告、证据包索引泄漏对象路径或candidate_answer。

本轮停止在材料与配置交付。所有事实裁决PENDING、所有实验NOT_EXECUTED、历史必要性NOT_ESTABLISHED。未执行或未满足公开时间门禁不是事实答案的unknown，也不构成已通过长程门禁。
