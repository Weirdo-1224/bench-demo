# GX010021 V2 Candidate Tasks — Session 3

日期：2026-10-11（Asia/Shanghai）。本目录已从既有V2统一候选转化为任务定义，遵循 [Benchmark Overall Design V1.0](../../../../docs/Long_Horizon_Streaming_Agent_Benchmark_Overall_Design_v1.0%20%281%29.md)。**全部CANDIDATE / NOT_REVIEWED；Gold=0；不构成已冻结的Benchmark Schema。**

保留9条候选任务：T1 4、T2 3、T3 2；另保存3条UNSUITABLE剔除记录用于说明无效任务定义。4条PILOT_CANDIDATE仅用于候选链路调试，5条NEEDS_EVIDENCE禁用评分。Session 3已经结束，此处没有Runner、Evaluator或Baseline实现。

## 文件与入口

|文件|用途|
|---|---|
|[task_schema.json](task_schema.json)|Draft 2020-12统一任务包结构，包含可复用$defs、成熟度与Track门禁；schema_version=gx010021-task-candidate-v0.1|
|[task_candidates.json](task_candidates.json)|12条定义、公开输入/输出契约、私有参考字段、证据注册表、来源哈希、缺口与统计|
|[task_feasibility_report.md](task_feasibility_report.md)|逐题能力、证据、评分、泄漏/捷径与L5审计，含旧8题迁移解释|
|[track_coverage_report.md](track_coverage_report.md)|实际机制覆盖、首轮Pilot顺序、历史必要性假设及后续接口准备度|
|[evidence_gaps.md](evidence_gaps.md)|11个OPEN定向缺口及优先级；不补造事实|
|[validate.py](validate.py)|仅验证静态任务包，含内存负向检查，不执行Agent/媒体分析或评分|
|[validation_report.json](validation_report.json)|最近静态校验、拒绝用例、包/Schema哈希与语义/运行未核验标记|

## 读取与验证

使用现有Python 3.11+和jsonschema（仓库已有依赖），从仓库根目录执行：

```powershell
python golden_episode/GX010021/tasks/v2_candidates/validate.py --self-test --write-report
```

也可从任意当前目录用脚本绝对路径运行，ROOT按脚本位置计算。省略--write-report可只读校验；--self-test对内存副本注入无效状态，不改源输入。只执行jsonschema能验证形状，必须再执行validate.py才能验证有限/范围时间、跨文件ID/JSON Pointer、引用原值、未来截止、字段/证据一致性、源/媒体/原帧SHA-256和统计。本次结果：1786项静态检查通过，32/32负向用例被拒绝；461个既有设计/标注/来源/旧任务文件的前后哈希一致，Git变更仅在本目录。校验结论不代表视频语义已确认。

完整校验需要本地原MP4及被引用的Session 2局部原帧/来源文件；runs通常被Git忽略，缺文件会明确失败，不能用不存在证据假装PASS。

## 公开输入与私有参考的边界

整个task_candidates.json及本目录报告都是Evaluator/数据审核侧资料，**绝不能作为Agent输入**。agent_public定义允许投送内容的契约，不意味着可以在Episode开始时发布每题对象。后续Runner按下列白名单投送：

1. initialize只给公开episode_id、存在的模态、统一protocol_config与通用输出契约；不给tasks列表、标题、状态、检查点/评分窗口、未来问题、源标注、完整规范、答案或证据注册表。
2. observation只给Runner生成的observation_id、媒体时段、实际availability_time_ms及受权限限制的content_ref；Agent可访问已公开历史，不能直接读完整source视频或Evaluator目录。不得把私有V2-/H1-/LC-/SRC-标注ID作为公开证据ID。
3. T1沿主执行输出state_update，Evaluator在私有STATE_CHECKPOINT只读取得state_snapshot；不逐题追问、不改变主状态。Evaluator从完整payload投影对应任务字段后验证任务payload_schema；候选参考只用于明确检查点，不沿未核验有效区间持续评分。
4. T2到私有query_time才投送question与payload_schema，冻结当时可见媒体截止并在快照/分支回答；分支丢弃，不回写主记忆。问题、答案和额外检索成本须保留trace。
5. T3共用完整0–696.929567秒Episode自主监测，允许沉默，输出alarm/raise/update/resolve；不投送逐事件问题或正常区间提示，不按负例窗口重启。后续Evaluator只在已核验的类别/范围比较报警。

record_refs仅是私有溯源上下文，完整事件可能包含查询后信息；不能递归展开成在线证据。required_evidence_sets明确可评分的证据、作用、检查时刻和covers_fields，引用范围必须截止于对应触发时间。证据集合最小充分性全部未实验确认。Agent证据输出必须引用公开observation_id和媒体时段，再由Evaluator映射私有证据；不能要求Agent猜私有ID。

## 三种时间与输出契约

媒体秒来自原MP4。availability_time_ms是Runner发布观察/指令的运行时钟，emission_wall_time_ms是实际输出墙钟；二者单位虽同为毫秒，语义和时钟映射需显式记录，不能与媒体秒直接比较。request_visible_media_cutoff记录请求开始时已公开视频的位置，media_time记录该状态/响应的媒体位置；模型完成后不能以新收到的未来信息补回答原Probe。输出evidence_refs包含observation_id和start_time/end_time，每段须已在请求截止前公开。静态校验只保证定义中的媒体截止，不声称验证实际发布日志。

Schema还提供通用error_event字段定义（onset/detectable/deadline/feedback/resolved及证据），但本Episode的error_events被约束为空，防止无证正例进入候选。未来有正例时需另版本显式解除Episode门禁，不能向当前包偷偷添事件。

公开JSON输入契约见public_input_contracts：initialize、observation、probe、instruction。输出契约见public_output_contracts：state、probe、alarm。alarm支持episode_id、media_time、request_visible_media_cutoff、availability_time_ms、emission_wall_time_ms、incident_id、decision、category、message、confidence、evidence_refs。media_time对应V1.0报警示例的video_time语义；采用统一字段名不改变原设计三时钟。

## 成熟度、参数和指导限制

PILOT_CANDIDATE只开放CANDIDATE_DIAGNOSTIC_ONLY；NEEDS_EVIDENCE和UNSUITABLE全部DISABLED。gold_answer=null、semantic_truth_verified=false、hard_score_eligible=false；源模型置信度和结构PASS不提升成熟度。所有参数（视频窗、抽帧、预算、Probe超时、δ_state、证据IoU和报警容差）保持TBD，后续Dev校准后冻结。候选时间精度继承历史/模型近似或原帧PTS，不伪造精确开始/结束时刻。

原片无音轨。指导/反馈标签不表示话语开始、结束、公开或生效时间；guidance_release_schedule与feedback_release_schedule均null，当前所有文本输入禁用。三个T1 Pilot与T2材料链可以在单列VIDEO_ONLY_DIAGNOSTIC条件调试；不能与尚未就绪的G1主设置混算。含规范的T2.1/T2.2与T3负例均标G1_BLOCKED_MISSING_GUIDANCE_TIMING。若以后显式设计转写释放策略，要单列诊断条件，不能冒充真实原话公开时间。

T3可信正例=0，正常区间也不是全类已确认正常；error_onset/detectable_from/deadline/feedback_given_at/resolved_at均没有填值。T3-001只有560.2–579.2秒限定负例候选；T3-002原L5正常区间为null，继续保留空集合。没有有效全片分母，不报告全片FA/h、Recall/F1、Timely Recall、检测延迟或恢复指标。

## 首轮Pilot与后续阶段

建议顺序：T1-002固液快照、T1-003入模内容/残留、T1-001步骤进度、T2-003材料路径隔离Probe。T2材料链最早候选历史153.2秒到查询680.212867秒跨度527.012867秒，仅是待检验假设；近期画面、题面、常识和完整当前规范的捷径需Baseline阶段排查。源规则任务的dependency_span_sec保持null，另记source_label_span_sec用于审计。

最小Runner/Evaluator所需媒体标识、输入/输出形状、触发形式、候选字段、私有证据与评分门禁已经明确。后续仍须实现因果访问/发布日志、三时钟映射、快照隔离、公开证据映射和参数校准，补规则公开证据及T3真实错误/恢复/正常分母。本轮到此停止，不自动开发或执行后续阶段。
