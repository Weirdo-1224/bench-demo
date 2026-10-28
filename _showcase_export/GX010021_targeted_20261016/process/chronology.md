# GX010021 真实工作链重建

本页重建的是现有文件所记录的历史，不是新设计的自动标注流程。整个链条由人工分阶段组织并调用多模态模型辅助；截至本包生成时，没有端到端自动标注 Agent，也没有经独立裁决的正式 Gold Task GT。

## 1. V1：四轮候选标注与结构化整合

1. 第一轮 `candidate_events_v1.md` 从视频抽样帧形成 E001–E056、O01–O15 等候选；输入是 GX010021 视频，输出是事件、对象与待复核线索。
2. 第二轮 `verification_report.md` 以视觉证据复核候选，给出 SUPPORTED / CONTRADICTED / UNCERTAIN，但该报告自身仍有时间表示和统计不一致。
3. 第三轮 `consistency_revision.md` 修正时间换算、统计和去重：最终口径为 45 个原始主张受支持、1 个被否定（E042 的“完全融化”）、10 个不确定；E057 并入 E054，E058 并入 E044/O10；加入混合容器的粉料段统一为 2。
4. 第四轮 `crosscheck_report.md` 将 55 条原始 `annotations.json` 文本作为辅助线索交叉核验。Instruction/Feedback 不是视频真值，也不是可直接给在线 Agent 的信息；E054 的更晚口径只保留“盖回粉色罐盖”。
5. `annotations/v1_candidate/` 将上述历史整合为 56 个事件、22 个对象/引用记录、115 个状态条目和 14 个开放复核项。数据状态仍是 CANDIDATE / NOT_REVIEWED。

## 2. V2：两轮全视频分析、结构化整合和局部原帧核验

1. `annotation_manifest.json` 记录两次独立全视频模型 pass；模型记录 45 条，去重后 39 条。模型请求/返回信息以 manifest 原字段为准。
2. 程序随后做统一结构化、去重和 V1/V2 对照。当前文件的统一口径是：59 事件候选、28 对象或观察组、138 状态（15 模型状态 + 115 历史状态 + 8 快照状态）、13 观察步骤、24 关系、192 证据定位、7 个 L5 候选。
3. `crosscheck.json` 对 56 个 V1 事件逐项分类：V1_ONLY 20、BOTH_OBSERVED 28、CONFLICT 8。它不是一一映射，也没有确认新的物理动作。
4. Session 2 的 8 张局部原帧用于 PTS 与局部语义检查；它们只核验各自快照，不等于对全片逐帧人工审定。V2 仍是 CANDIDATE / NOT_REVIEWED，confirmed_errors=0，gold_records=0。

## 3. Session 3：三 Track 候选任务实例化

`tasks/v2_candidates/task_candidates.json` 保存 12 条设计定义：9 条保留候选、3 条 UNSUITABLE；状态为 4 条 PILOT_CANDIDATE、5 条 NEEDS_EVIDENCE、3 条 UNSUITABLE。按保留候选计，T1=4、T2=3、T3=2。正式 Gold=0，硬评分任务=0，T3 已确认异常正例=0。

任务定义把候选事实、在线输入契约、离线 evaluator 参考和证据缺口分开。`PILOT_CANDIDATE` 只表示可用于诊断性试点，不能翻译为“可正式评测”。长时间跨度也没有经过 Recent-only / No-video / Instruction-only 或逐段移除实验，因此不能直接声称“历史必要性”成立。

## 4. Session 4A：真实帧展示素材

`showcase/showcase_manifest.json` 记录 12 张已存在的真实视频帧及 PTS、哈希、来源。此次导出逐张从原路径做字节一致复制，没有重跑模型，也没有新抽帧。展示帧只服务于人工讲解，不能假装是 Runner 在对应在线时刻已经收到的观测。

## 5. 因果与权限边界

- 431.2308 秒的 T1 检查只允许使用该时刻及以前实际发布给 Runner 的信息；445.211433 秒帧不能倒灌给 431 秒。
- 原始视频无音轨；原 `annotations.json` 的话语时间戳没有可验证的在线 availability/effective_from，因此相关指令/反馈默认不公开给 Agent。
- 四个案例中的答案均是 candidate answer；`adjudicated_gt` 保持 null。
