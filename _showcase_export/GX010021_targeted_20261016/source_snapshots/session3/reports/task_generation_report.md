# GX010021 Pilot 候选任务生成报告

日期：2026-10-09（Asia/Shanghai）。生成时输出位于 `golden_episode/GX010021/` 下，本轮目录整理后分别归位到 `reports/track_feasibility.md`、`tasks/pilot_task_candidates.json`、`reports/annotation_gaps.md`、`reports/task_generation_report.md`。全部Candidate，未经人工独立核验，不发布Gold/正式分数。

## 数量和适配结论

共 **8个候选实例**：T1 4个（T1.1×1、T1.2×2、T1.3×1）；T2 3个（T2.1/T2.2/T2.3各1）；T3 1个（T3.1局部规则负例）。**T3正错误=0、T3.2/T3.3=0、可直接执行=0、Gold=0**。8不是8个独立统计样本，全部来自同一个Episode；不能用于显著性/排名结论。

| ID | 原设计子任务 | 媒体检查点/私有监测窗（秒） | 内容 | 成熟度 |
|---|---|---:|---|---|
| GX010021-T1-001 | T1.1 | 239.3 | 第一轮电动搅拌已结束并放置打蛋器 | Candidate / 不可硬评分 |
| GX010021-T1-002 | T1.2 | 433.3 | 第二次取出后黄油仍见固态块 | Candidate / 不可硬评分 |
| GX010021-T1-003 | T1.3 | 631.3 | 补粉后的干粉表层转为光滑面糊 | Candidate / 不可硬评分 |
| GX010021-T1-004 | T1.2 | 692.3 | 烤模已入烤箱而预热完成状态未知 | Candidate / 不可硬评分 |
| GX010021-T2-001 | T2.1 | 200.3 | 首次搅拌开始时加奶事实与半杯前置条件的区分 | Candidate / 不可硬评分 |
| GX010021-T2-002 | T2.2 | 641.3 | 倒糊入模时材料替代许可与实际处理状态 | Candidate / 不可硬评分 |
| GX010021-T2-003 | T2.3 | 692.3 | 已入烤箱面糊的牛奶与两种加粉路径 | Candidate / 不可硬评分 |
| GX010021-T3-001 | T3.1 | 560.2–579.2 | 局部负例候选：已获许可的用油替代不应被误报为遗漏垫纸 | Candidate / 不可硬评分 |

T1三类均有宏观事实素材。T2包含实际状态前置区分、上下文许可范围与跨阶段来源路径，未生成仅问最终糖量/简单次数的核心Recall题。T2-001跨度较短且unknown仍待可观测性裁定；T2-003最适合优先检验历史增益。T3负例不能替代正异常、及时干预或恢复评测，三个Track的完整可执行Pilot尚未成立。

## 来源与覆盖

- 已读V1.0 §4–6/§9–12及全部整合事件、对象状态、证据与复核条目；查阅原55条annotations和历史修订/交叉核验报告。没有访问外部数据或重新观察视频。
- 直接/经reference_facts间接覆盖 **13/56个事件**、**11/22个对象引用记录**、**11/55条原文本**、**36/162条唯一证据**。
- 事件集合：E020, E022, E023, E027, E028, E031, E032, E042, E049, E051, E052, E053, E055。
- 原文本集合：R01, R02, R18, R19, R32, R39, R40, R41, R42, R43, R45。已包含加奶指令和烤模许可链；R01/R02仅作温度要求/自述，R32/R45等经原fact不确定性证据继承也不成为动作完成真值。
- 证据种类覆盖：`{"reported_visual_observation": 21, "model_inference": 3, "ego_mc_text": 11, "inherited_candidate_text": 1}`。这些类别来自原数据，不重新分级；V1仍只是AI报告声称可见，V2/T/TEXT不升格为视觉真值。
- 时间覆盖为代表性检查点，不能宣称连续全程覆盖；T1/T2最晚692.3s未用未来R55(692.608s)或E056。原尾部缺口保留。

## 字段与在线协议

复用任务类型、trigger、原Event/Object/State/Review ID、原时间结构和证据注册表。T2保留V1.0所需 `query_time/question/answer_type/gold_answer/required_evidence_sets/reasoning_relation/earliest_answerable_time/dependency_span/visibility_regime/evidence_quality`；由于无Gold，gold_answer全部null，候选参考另存candidate_answer。任务包格式标0.1草案，不扩展原schema.json或宣称最终执行Schema已冻结。

`reference_facts`逐字段复制事实/状态/文本并附JSON Pointer；证据保留历史报告文件/行、媒体时段、kind/grade。源文件不在本包重写。evidence_refs是Evaluator私有V-/T-引用，Agent输出只能引用已公开的observation/指令，再由Evaluator映射。整个JSON文件不能作为参评Agent输入。

静态T1/T2所有选用字段和证据末界均≤检查点。Event ID全记录的末界可晚于检查点，但其链接是私有语境：T2-001的E027只用199.2s开始帧；T2-002的E053只用633.2–641.2s开始倒糊。禁止因完整事件标题/末态字段泄漏后续信息。参考unknown不代表实际状态必然不可观测，PG05需裁决。

T2问题仅在query_time释放，在同一主执行状态的隔离分支回答，答案/问题/工具结果均不回写。运行必须分别审计media/availability/wall time；当前availability manifest=null，单点转写时间不冒充整句结束/实际送达。三个Track不重置Agent。

T3没有逐次提问、规则或答案提示。560.2–579.2s只是Evaluator私有窗口，逐时禁止读未来，不能在560.2s喂完整窗口证据。只约束“没纸/没剩余黄油”两类误报，其余错误未标；所有Error时间null。规则候选为对话中的局部许可，effective_from=null，公开/生效核验前不可执行。

## 静态校验结果与边界

**PASS；517项断言**。检查唯一任务ID、有效Event/Object/Review引用、原fact/state值与证据等级一致、JSON Pointer来源、原文件/行存在、证据和状态时间不晚于截止、T2跨度复算及Probe隔离字段、T3负例时间语义、候选答案关键约束。

| 检查类别 | 断言数 |
|---|---:|
| task_ids | 1 |
| candidate_status | 8 |
| time_bounds | 8 |
| event_refs | 20 |
| object_refs | 27 |
| reference_consistency | 67 |
| causal_references | 137 |
| evidence_consistency | 39 |
| source_paths | 39 |
| source_lines | 26 |
| review_refs | 9 |
| candidate_rules | 14 |
| probe_time | 6 |
| evidence_sets | 6 |
| dependency_span | 3 |
| probe_isolation | 3 |
| negative_semantics | 1 |
| continuous_monitoring | 1 |
| feedback_boundary | 1 |
| answer_consistency | 5 |
| input_integrity | 18 |
| json_pointers | 78 |

关键答案复核：E042未沿用“完全融化”；预热完成未知；内壁油膜未知；牛奶半杯不能由早期1/4标签确定；面粉仅两处可见入混合容器，E031量取不重复算加入；没有恢复E057/E058或补造E054插入/放置动作。

原文件完整性：本轮生成前后对 **18个原有文件**逐一SHA-256一致（含原视频、设计文档、JSON、历史报告、脚本、归档及已有缓存）。另从磁盘读回JSON验证可解析。没有运行会写回merge_report/validation_results的原validate.py命令。

PASS范围仅为静态结构/引用/候选逻辑与文件完整性。没有核验视频真实性、话段公开时刻、最小证据充分性、近期窗口必要性、运行隔离或实际延迟；没有计算Benchmark分数。可执行任务和Gold数均保持0。

## 无法可靠生成与下一步

不生成已预热350°F/完全融化的确定前置真值；糖最终用量单句Recall不算T2核心；修订临界时刻的前后配对需先补公开/生效时间；T2.4按V1默认关闭。不生成鸡蛋加三枚/归盒恢复、小碗容量违例、糖不足定量违例、加粉后暂停违序、遗漏烘焙纸、微波15秒超时或禁止补粉等正异常。无可靠T3.2及时干预和T3.3恢复任务。

下一步先独立核验关键来源链、烤模许可作用范围、牛奶杯量可观测性及时间公开层；随后校准T1时点/容差，做T2最小证据删除与B0/No-video诊断，再确认最终执行字段和运行隔离。T3若当前Episode核验后仍缺真实正错误/恢复，按V1.0 §9.3增加针对性样例，而不改变评测定义。本轮未开发Evaluator/Harness、未重标注、未运行Pilot或Baseline。

## 读取来源哈希（相对项目根）

| 来源（整理后路径；SHA-256 为整理前原文件快照，内容未变） | SHA-256 |
|---|---|
| `docs/Long_Horizon_Streaming_Agent_Benchmark_Overall_Design_v1.0 (1).md` | `260908d8bab250d53bc27b13da48e74ffa22f9d7aa24f88470396f0361007cb0` |
| `golden_episode/GX010021/annotations/events.json` | `9b614e7188f21f72fca37c08bc58208a655f4169a2fc60bed747df71f3af4632` |
| `golden_episode/GX010021/annotations/objects.json` | `27dafe0574b50af461404402b0b4a5ab807df3b61f56b120575c38bab0ed9c1c` |
| `golden_episode/GX010021/annotations/review_queue.json` | `749bc8c26349e48b6cadbd10678277865eba07a0a7d86751a5f55bfd7a24436a` |
| `golden_episode/GX010021/annotations/schema.json` | `764d613e676007016d3e267b436cb0c6ae2a99742b6bf8630e34b25d80a14802` |
| `golden_episode/GX010021/reports/merge_report.md` | `91573bb13b7eb33fdaef4436f5a639142208373e29733501cb62f3601fc54a8f` |
| `golden_episode/GX010021/reports/validation_results.json` | `4cbd67918d4b98a34a60d75a7f304e141c52a863430e6079595af69fa152d17d` |
| `golden_episode/GX010021/source/annotations.json` | `88183e371dac0948378b723aa4c2ca102a2597770ed518805d52f180cd780527` |
| `golden_episode/GX010021/annotation_reports/candidate_events_v1.md` | `d902836c5f22515682189559348f052853a7fa5c6aac2f8ebd779e41b88a43c4` |
| `golden_episode/GX010021/annotation_reports/verification_report.md` | `76128353fc3168eac4f358a0d29067c3f614bbe3640caac8c040f51eae4a63d5` |
| `golden_episode/GX010021/annotation_reports/consistency_revision.md` | `4d37d9b5d40374b1a32cb95cbacdccc5b26766b82eb00cf81451ad7228a0e2e7` |
| `golden_episode/GX010021/annotation_reports/crosscheck_report.md` | `5d0cab2dcf558cbd0ce92061a9bd91f9fdef7aa55c935a447208be9452d58026` |
| `golden_episode/GX010021/annotation_reports/README.md` | `72b76996ea365a5fbee780b396f45efa8340d2567e7c4aec999a3f27b2fc89c1` |
| `golden_episode/GX010021/source/GX010021.MP4` | `fe4a11550bf2aea09a39ce1e72dba4633adc8c8b6a540e9894696e8b2ed1c8f9` |
