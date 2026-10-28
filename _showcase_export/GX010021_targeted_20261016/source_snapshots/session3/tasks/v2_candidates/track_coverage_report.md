# GX010021 Session 3：Track覆盖报告

日期：2026-10-11（Asia/Shanghai）。本报告区分可用候选、证据待补候选和剔除记录；不把存在JSON定义算作能力已覆盖。

|Track|保留候选|PILOT_CANDIDATE|NEEDS_EVIDENCE|UNSUITABLE记录|Gold|
|---|---:|---:|---:|---:|---:|
|T1 Online Procedural State Understanding|4|3|1|0|0|
|T2 Long-Horizon Procedural Dependency Reasoning|3|1|2|1|0|
|T3 Continual Monitoring & Timely Intervention|2|0|2|2|0|
|合计|9|4|5|3|0|

## 子任务机制覆盖

|子任务|定义与支持|实际覆盖限制|
|---|---|---|
|T1.1 Step Progress Tracking|T1-001，200.3/239.3秒读取同一轨迹的in_progress/completed|开始与完成是动作段候选；无取消/撤销/补做Gold，也未证明长程Drift|
|T1.2 Object & Environment State Tracking|T1-002，431.2308/445.211433固液共存；T1-003，680.212867烤模内容/主容器残留|共3个对象状态检查点、4个字段判断；不外推遮挡/连续区间，不评分比例/全量转移|
|T1.3 State Transition Tracking|T1-004，603.2粉表面与630.2光滑的候选转移包络|NEEDS_EVIDENCE；首个可见变化、持续身份与终态核验缺失，δ_state和延迟不填|
|T2.1 Historical Precondition Verification|T2-001，规范候选与奶两段转移、量具标签局限|NEEDS_EVIDENCE；语句提供前置关系候选，非temporal_precedes必然依赖；量值unknown尚未裁决|
|T2.2 Instruction Revision Reasoning|T2-002，垫纸→剩余黄油→油的范围/条件链|NEEDS_EVIDENCE；当前许可可能由单句/当前完整规范直接给出；不能做未核验有效时间配对|
|T2.3 Historical Evidence Integration|T2-003，奶/粉不同入料路径→主容器→烤模|PILOT_CANDIDATE，可调试多段证据与路径接口；身份连续性与历史必要性未证实|
|T3.1 Online Anomaly Detection|T3-001用油限定负例，T3-002分段再加热潜在正常负例|两个NEEDS_EVIDENCE；可信正例0，不能评价发现异常；T3-003为剔除记录|
|T3.2 Evidence-aware Timely Intervention|没有可评分候选|没有成立错误、detectable_from、外部价值deadline；不生成虚构时间任务|
|T3.3 Continuous Recovery Monitoring|T3-004仅记录不适用恢复定义|没有真实纠正/解除或纠正后第二错误；不能算恢复覆盖|
|T2.4 Delayed Consequence & Recovery|不启用|总体设计V1.0默认不启用，不扩展Track范围|

T1共6个候选状态/转移读取时刻：2个进度、2个相态、1个入模内容、1个待证转移。T2保留3个Probe定义（200.3、641.3、680.212867秒），只有材料链允许候选诊断。T3两条负例定义共享一次完整Episode的自主报警流，评分范围私有；再加热候选尚无可评分正常区间。

## 第一轮Pilot建议

优先使用T1-002与T1-003调试公开视频、状态输出、原帧PTS、未知处理和私有参考边界；随后使用T1-001调试同一动作段状态的连续维护和只读快照。T2-003适合调试隔离Probe、路径输出与公开观察证据映射；只报告候选字段/证据一致性，不能据此宣布通过历史必要性。当前T3可纳入同一Episode持续报警trace采集与接口校验，但不生成质量分。4个PILOT_CANDIDATE共用一个不重置Episode；T2必须快照分支，T1读取状态不能反向改变主状态。

## Track 2历史必要性假设

|Probe|候选证据与假设|捷径及最小性风险|跨度语义|
|---|---|---|---|
|T2-001|奶盒→量具→主容器与此前指令共同判断实际要求；去掉量取历史可能丢掉量值局限依据|奶已加入可能单段足够；unknown可能不看片即可猜；早期标签并非已证必要证据|来源标签跨度65.552秒；合法必要历史跨度null，因为规则公开未定|
|T2-002|对象/用途/条件需上下文消解，“Yes”单句未必足够|R43可直接给油许可；完整当前规范可能包含范围；538–556对话可能仍在近期窗口|来源标签跨度102.602秒；合法必要历史跨度null，因为规则公开未定|
|T2-003|680秒当前画面不能直接还原奶的153.2–161.2与粉的270.2–291.2转移；逐段移除应损害具体路径或证据覆盖|长近期窗口可能含595秒直接补粉；常识可猜材料；持续身份候选可能导致默认unknown|候选证据定位跨度527.012867秒；不是已证明历史必要性，earliest_answerable_time仅候选当前锚点|

最小充分集合全部标为CANDIDATE_MINIMAL_UNVERIFIED或INSUFFICIENT。T2-001单个集合包含规则、传递与量值局限候选，尚不足支持当时有效前置要求评分；T2-002集合服务范围/条件/当前事实，不能把“油许可”一字段需要的证据误说为全链都必要；T2-003七段是待验证的整体候选集合，当前锚点与路径证据需在移除实验中分别核查冗余。required_evidence_sets通过covers_fields和applies_at_media_time明确范围；同一检查点/Probe且同一字段范围的多个集合才视为可替代最小集合。T2三道保留Probe各只有一个候选集合；T1多个集合分别对应检查点。

后续Baseline阶段才执行：同一模型与相近调用预算的Recent-only窗口扫描；No-video/Instruction-only；完整历史与逐段移除的证据覆盖比较。窗口、预算与匹配参数在Dev上冻结。须同时看具体Episode路线和证据，不能仅用材料名准确率证明长程。保持真实历史，不伪造自然对照。当前所有history_necessity均未实测，Recent-only Gap没有数值或预设符号。

## 下一阶段接口准备度

输入接口已经以public_input_contracts定义initialize/observation/probe/instruction，输出以public_output_contracts定义state_update/state_snapshot、probe_answer和alarm（raise/update/resolve）。任务级payload_schema、私有trigger、reference_items、证据注册表、来源路径/JSON Pointer/哈希与状态门禁已齐备，足以开始最小Runner/Evaluator的候选诊断链路。

仍未准备好完整G1硬评分：指导/反馈合法发布表为空，音轨不存在；原帧检查点要确保实际采样到该PTS，否则应记缺观察而非强行评分；视频窗、采样、超时、预算、δ_state、证据IoU/报警容差仍TBD。必须实现三时钟映射、公开观察ID到私有定位的映射、禁止读取原文件未来部分、Probe隔离与完整trace审计，并在后续阶段实测。此处只是接口定义和静态数据校验，未开发这些组件。
