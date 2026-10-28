# 证据可追溯性审计

| 案例 | 任务源 | 结构化事实源 | 视频/帧源 | 可回溯性 | 关键边界 |
|---|---|---|---|---|---|
| T1-002 | task_candidates.json#/tasks/1 | objects.json#/states/133-134 | LC-431-2、LC-445-2；均有 PTS/SHA256 | PASS | 不能把 445s 倒灌到 431s；两帧非持续区间 |
| T2-003 | task_candidates.json#/tasks/6 | relations.json#/records/10,16-20 | 7 个 evidence bindings；相关 Session4A 帧 | PASS_WITH_CANDIDATE_LIMIT | 关系均未审定；历史必要性 untested |
| T3-001 | task_candidates.json#/tasks/8 | procedure.json#/records/38-42；evidence_index.json#/records/89-90 | Session4A 许可/用油展示帧 | PASS_WITH_AVAILABILITY_GAP | 辅助文本不是在线已发布规则 |
| T3-002 | task_candidates.json#/tasks/9 | procedure.json#/records/29-30；evidence_index.json#/records/16-17 | 无直接 Session4A 绑定帧 | PARTIAL | 无异常正例、纠正/恢复或报警起点 |

所有案例 `candidate_gt` 都直接来自源任务的 `evaluator_private.candidate_answer`；`adjudicated_gt` 均为 null。帧的语义状态仍为 CANDIDATE/UNCONFIRMED，只有文件哈希与 PTS 映射完成技术核验。
