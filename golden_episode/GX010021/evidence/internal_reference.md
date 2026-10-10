# GX010021 内部参考（禁止向盲审者或被评测Agent提供）

本文件保留候选事实、原引用及历史AI判断。全部候选，未经本轮视频事实裁决，Gold=0。盲审者只使用allowlist中本任务的材料，不能打开本文件或evidence_manifest.json。

## 准备结论与限制

- 原媒体无音轨；标注中55条对话无法由本MP4听证。T2-002可开展视频动作与文本语义分层复核，但真实对话及公开时间审核条件不足。
- 原始对话单点time不等于话段结束、availability或effective_from。所有真实时刻仍为null。
- 提取[0,692.3)全部源帧，按任务分段并设置截止；没有提取692.608秒R55及尾部作为任务证据。源余段[692.3,696.929567)不属本轮任务合法输入，历史尾部缺口696.2–696.929567无须为这些任务补裁决。
- 所有片段原帧解码MD5与来源逐帧一致。此校验只证明媒体技术完整性，不判断动作、身份、材料或Ground Truth。

## 路径修复与引用边界

上游reference_facts的`../../annotations.json#/texts/...`为整理前遗留定位，当前实际唯一源为`golden_episode/GX010021/source/annotations.json`；`events.json`和`objects.json`实际在`annotations/`。保留原字符串并通过artifact解析其JSON Pointer，本包不创建副本、不写回上游。任务media_ref的`../../source/GX010021.MP4`从tasks文件目录直接解释也不能找到实际文件；本包按Episode根规范化到现有source路径。

## 历史冲突（全部为历史主张）

| 项目 | 历史分歧与后续修订 | 本包处理 |
|---|---|---|
| E027/E028 | 初稿E027为200–234秒；后轮改为199–235秒。E028对象状态仍234–239秒，与约235.2秒提离及236.2–238.2秒放置重叠。 | 保留原引用；提取194–239.3秒连续过程；不裁定精确结束/完成时刻。 |
| E049 | 初稿声称内壁沾油且起点566秒；后轮改为560–581秒；只报告倒油/旋转，内壁油膜仍UNCERTAIN。 | 分开核验进入、姿态、表面结果，不用R45 Success证实覆盖。 |
| 时间转换 | 第二轮将MM:SS去冒号误写成绝对秒，如920.2→560.2、995.2→595.2、1033.2→633.2；第三轮纠正。 | 使用结构化time与更正后的绝对秒，原字符串只存内部。 |
| E031/E032/E051 | 曾把量取/倒入/袋直倒混为三次加入；第三轮撤销，候选为E032与E051两处可见入混合容器，未排除隐藏加入。 | 盲审问题不提供次数，要求自行列出直接可见事件。 |
| O05身份/量值 | 原稿将杯组和搅拌/刮糊黑工具当同一件；整合层分离O16/O17未知同一性。早段1/4 CUP不证明奶杯或粉杯规格，half cup/one cup是指令。 | 局部转移杯身份与跨阶段身份分别审核，不增加体积评分。 |
| T2-002规则 | R39→R41→R43只是待审局部替代链，supersedes/effective_from未核实；R40/R42为自述。 | 原文仅作为必要文本上下文；实际话语/可见性缺口单列。 |
| T2-003持续性 | O01/O08/O12/O15相同候选ID不能证明间隙身份；原任务只列首尾时段。 | 补齐中间全部帧，审计7类间隙；视觉身份仍PENDING。 |
| E053完整记录 | 633–679秒包含刮取/末态；T2-002截止641.3，只允许初段；T2-003可用后续。 | C13在641.3切分；C14仅供T2-003，不能发给T2-002审核或Agent。 |
| 黄油/预热 | 早轮“完全融化”和“已预热”被后续降级/修正。 | 桥接视频中的这些操作仅为连续性背景，不借此新增任务/规则或裁决。 |

## 原子事实与上游引用

### GX010021-T1-001

原候选答案（未核验）：
```json
{
  "step": "第一轮电动搅拌",
  "factual_progress": "completed",
  "mixer_location": "左侧台面",
  "completion_basis": "已发生搅拌、搅拌棒提离并放置；仅动作段完成，不等于全部食材/规范完成"
}
```

完整任务定义（内部原样快照）：
```json
{
  "task_id": "GX010021-T1-001",
  "episode_id": "GX010021",
  "track": "T1",
  "task_type": "T1.1",
  "title": "第一轮电动搅拌已结束并放置打蛋器",
  "data_status": "CANDIDATE",
  "human_review": "NOT_REVIEWED",
  "hard_scoring_eligible": false,
  "execution_ready": false,
  "design_refs": [
    "4.1",
    "5.1",
    "6.3"
  ],
  "trigger": {
    "mode": "state_snapshot",
    "media_time": 239.3,
    "scheduling_status": "CANDIDATE_CHECKPOINT"
  },
  "observation_cutoff": 239.3,
  "reference_event_ids": [
    "E027",
    "E028"
  ],
  "reference_object_ids": [
    "O01",
    "O07",
    "O15"
  ],
  "reference_facts": [
    {
      "artifact": "objects",
      "object_id": "O07",
      "state_id": "O07.S02",
      "source_ref": "objects.json#/objects/6/state_history/1",
      "event_id": "E027",
      "time": {
        "start_sec": 199,
        "end_sec": 235,
        "start_hms": "00:03:19.000",
        "end_hms": "00:03:55.000"
      },
      "kind": "observation",
      "field": "mixing_round",
      "before": null,
      "after": 1,
      "status": "REPORTED_SUPPORTED",
      "evidence_ids": [
        "V-E027-01",
        "V-E027-02",
        "V-E027-03"
      ],
      "use": "CANDIDATE_REFERENCE_ONLY"
    },
    {
      "artifact": "objects",
      "object_id": "O07",
      "state_id": "O07.S05",
      "source_ref": "objects.json#/objects/6/state_history/2",
      "event_id": "E028",
      "time": {
        "start_sec": 234.0,
        "end_sec": 239.0,
        "start_hms": "00:03:54.000",
        "end_hms": "00:03:59.000"
      },
      "kind": "transition",
      "field": "location",
      "before": null,
      "after": "提离混合容器并置左台面",
      "status": "REPORTED_SUPPORTED",
      "evidence_ids": [
        "V-E028-01"
      ],
      "use": "CANDIDATE_REFERENCE_ONLY"
    },
    {
      "artifact": "objects",
      "object_id": "O01",
      "state_id": "O01.S06",
      "source_ref": "objects.json#/objects/0/state_history/5",
      "event_id": "E027",
      "time": {
        "start_sec": 199,
        "end_sec": 235,
        "start_hms": "00:03:19.000",
        "end_hms": "00:03:55.000"
      },
      "kind": "transition",
      "field": "contents",
      "before": "蛋/糖/奶分层",
      "after": "淡黄均匀液",
      "status": "REPORTED_SUPPORTED",
      "evidence_ids": [
        "V-E027-01",
        "V-E027-02",
        "V-E027-03"
      ],
      "use": "CANDIDATE_REFERENCE_ONLY"
    }
  ],
  "evidence_refs": [
    {
      "evidence_id": "V-E027-01",
      "registry_ref": "events.json#/evidence/34",
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 56,
        "section": "B"
      },
      "time": {
        "start_sec": 199.2,
        "end_sec": 199.2,
        "start_hms": "00:03:19.200",
        "end_hms": "00:03:19.200"
      },
      "kind": "reported_visual_observation",
      "grade": "V1",
      "description": "搅拌棒进入液面",
      "role": "首次搅拌开始",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 199.2,
          "end_sec": 199.2,
          "start_hms": "00:03:19.200",
          "end_hms": "00:03:19.200"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    },
    {
      "evidence_id": "V-E027-02",
      "registry_ref": "events.json#/evidence/35",
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 56,
        "section": "B"
      },
      "time": {
        "start_sec": 200.2,
        "end_sec": 234.2,
        "start_hms": "00:03:20.200",
        "end_hms": "00:03:54.200"
      },
      "kind": "reported_visual_observation",
      "grade": "V1",
      "description": "搅拌、混合液渐均匀",
      "role": "搅拌过程",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 200.2,
          "end_sec": 234.2,
          "start_hms": "00:03:20.200",
          "end_hms": "00:03:54.200"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    },
    {
      "evidence_id": "V-E027-03",
      "registry_ref": "events.json#/evidence/36",
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 56,
        "section": "B"
      },
      "time": {
        "start_sec": 235.2,
        "end_sec": 235.2,
        "start_hms": "00:03:55.200",
        "end_hms": "00:03:55.200"
      },
      "kind": "reported_visual_observation",
      "grade": "V1",
      "description": "搅拌棒提离",
      "role": "搅拌棒提离",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 235.2,
          "end_sec": 235.2,
          "start_hms": "00:03:55.200",
          "end_hms": "00:03:55.200"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    },
    {
      "evidence_id": "V-E028-01",
      "registry_ref": "events.json#/evidence/37",
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 57,
        "section": "B"
      },
      "time": {
        "start_sec": 236.2,
        "end_sec": 238.2,
        "start_hms": "00:03:56.200",
        "end_hms": "00:03:58.200"
      },
      "kind": "reported_visual_observation",
      "grade": "V1",
      "description": "打蛋器置左侧台面",
      "role": "置于左侧台面",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 236.2,
          "end_sec": 238.2,
          "start_hms": "00:03:56.200",
          "end_hms": "00:03:58.200"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    }
  ],
  "normative_rules": [],
  "candidate_answer": {
    "step": "第一轮电动搅拌",
    "factual_progress": "completed",
    "mixer_location": "左侧台面",
    "completion_basis": "已发生搅拌、搅拌棒提离并放置；仅动作段完成，不等于全部食材/规范完成"
  },
  "gold_answer": null,
  "scorable_conditions": [
    "独立核验搅拌和提离/放置，按固定检查点读状态。",
    "动作段completed、器具位置可分别评分；不把R25 Success或后续食材加入当完成证据。",
    "Update Delay需首次可观察完成时刻；当前不能算精确延迟。"
  ],
  "pending_verification": [
    "核验199.2–238.2s动作及O01/O07连续身份。",
    "确认用于T1.1的动作段边界/完成条件，不把Ego-MC步骤清单擅自变为固定SOP。"
  ],
  "existing_review_queue_ids": [],
  "evidence_quality": {
    "status": "NOT_INDEPENDENTLY_VERIFIED",
    "directly_observed_in_this_round": false,
    "visual_source": "ARCHIVED_AI_REPORTS_ONLY",
    "numeric_confidence": null,
    "annotation_disagreements": "继承字段不确定性与历史修订；未做人类一致性测量。"
  },
  "visibility_regime": "G1",
  "causal_constraints": {
    "max_media_time": 239.3,
    "require_availability_time_check": true,
    "evaluator_reference_visible_to_agent": false,
    "event_id_link_is_not_full_record_access": true,
    "unknown_requires_observability_adjudication": true
  },
  "protocol_tbd": [
    "输入窗口/采样与实际availability_time",
    "运行预算/超时",
    "最终输出Schema/证据匹配阈值",
    "T1状态类别映射、Checkpoint间隔、δ_state"
  ],
  "agent_facing_input": {
    "kind": "read_only_state_snapshot",
    "media_time": 239.3,
    "note": "不把候选状态/事件ID/题面提示写入主Agent；只按统一接口读取状态。"
  },
  "output_contract": {
    "output_types": [
      "state_update",
      "state_snapshot"
    ],
    "allow_states": [
      "completed",
      "ongoing",
      "unknown",
      "uncertain"
    ],
    "required_clock_fields": [
      "media_time",
      "emission_wall_time",
      "request_observation_cutoff"
    ]
  }
}
```

#### GX010021-T1-001-F01

中性核验问题：199–235秒期间，器具与容器内材料之间发生了什么动作？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "objects",
    "object_id": "O07",
    "state_id": "O07.S02",
    "source_ref": "objects.json#/objects/6/state_history/1",
    "event_id": "E027",
    "time": {
      "start_sec": 199,
      "end_sec": 235,
      "start_hms": "00:03:19.000",
      "end_hms": "00:03:55.000"
    },
    "kind": "observation",
    "field": "mixing_round",
    "before": null,
    "after": 1,
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E027-01",
      "V-E027-02",
      "V-E027-03"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O01",
    "state_id": "O01.S06",
    "source_ref": "objects.json#/objects/0/state_history/5",
    "event_id": "E027",
    "time": {
      "start_sec": 199,
      "end_sec": 235,
      "start_hms": "00:03:19.000",
      "end_hms": "00:03:55.000"
    },
    "kind": "transition",
    "field": "contents",
    "before": "蛋/糖/奶分层",
    "after": "淡黄均匀液",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E027-01",
      "V-E027-02",
      "V-E027-03"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E027-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 56,
      "section": "B"
    },
    "description": "搅拌棒进入液面",
    "grade": "V1",
    "time": {
      "start_sec": 199.2,
      "end_sec": 199.2,
      "start_hms": "00:03:19.200",
      "end_hms": "00:03:19.200"
    },
    "original_text": "结束时间由 3:54 修至约 3:55；开始由 3:20 修至约 3:19"
  },
  {
    "id": "V-E027-02",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 56,
      "section": "B"
    },
    "description": "搅拌、混合液渐均匀",
    "grade": "V1",
    "time": {
      "start_sec": 200.2,
      "end_sec": 234.2,
      "start_hms": "00:03:20.200",
      "end_hms": "00:03:54.200"
    },
    "original_text": "结束时间由 3:54 修至约 3:55；开始由 3:20 修至约 3:19"
  }
]
```

#### GX010021-T1-001-F02

中性核验问题：器具工作端何时、以何种方式离开容器内材料？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "objects",
    "object_id": "O07",
    "state_id": "O07.S02",
    "source_ref": "objects.json#/objects/6/state_history/1",
    "event_id": "E027",
    "time": {
      "start_sec": 199,
      "end_sec": 235,
      "start_hms": "00:03:19.000",
      "end_hms": "00:03:55.000"
    },
    "kind": "observation",
    "field": "mixing_round",
    "before": null,
    "after": 1,
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E027-01",
      "V-E027-02",
      "V-E027-03"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O01",
    "state_id": "O01.S06",
    "source_ref": "objects.json#/objects/0/state_history/5",
    "event_id": "E027",
    "time": {
      "start_sec": 199,
      "end_sec": 235,
      "start_hms": "00:03:19.000",
      "end_hms": "00:03:55.000"
    },
    "kind": "transition",
    "field": "contents",
    "before": "蛋/糖/奶分层",
    "after": "淡黄均匀液",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E027-01",
      "V-E027-02",
      "V-E027-03"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E027-03",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 56,
      "section": "B"
    },
    "description": "搅拌棒提离",
    "grade": "V1",
    "time": {
      "start_sec": 235.2,
      "end_sec": 235.2,
      "start_hms": "00:03:55.200",
      "end_hms": "00:03:55.200"
    },
    "original_text": "结束时间由 3:54 修至约 3:55；开始由 3:20 修至约 3:19"
  }
]
```

#### GX010021-T1-001-F03

中性核验问题：截至239.3秒，器具位于哪里，是否仍由手持或接触容器？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "objects",
    "object_id": "O07",
    "state_id": "O07.S05",
    "source_ref": "objects.json#/objects/6/state_history/2",
    "event_id": "E028",
    "time": {
      "start_sec": 234.0,
      "end_sec": 239.0,
      "start_hms": "00:03:54.000",
      "end_hms": "00:03:59.000"
    },
    "kind": "transition",
    "field": "location",
    "before": null,
    "after": "提离混合容器并置左台面",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E028-01"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E028-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 57,
      "section": "B"
    },
    "description": "打蛋器置左侧台面",
    "grade": "V1",
    "time": {
      "start_sec": 236.2,
      "end_sec": 238.2,
      "start_hms": "00:03:56.200",
      "end_hms": "00:03:58.200"
    },
    "original_text": "无需修改"
  }
]
```

#### GX010021-T1-001-F04

中性核验问题：该动作段开始前，容器内材料呈现哪些可见外观特征？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "objects",
    "object_id": "O07",
    "state_id": "O07.S02",
    "source_ref": "objects.json#/objects/6/state_history/1",
    "event_id": "E027",
    "time": {
      "start_sec": 199,
      "end_sec": 235,
      "start_hms": "00:03:19.000",
      "end_hms": "00:03:55.000"
    },
    "kind": "observation",
    "field": "mixing_round",
    "before": null,
    "after": 1,
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E027-01",
      "V-E027-02",
      "V-E027-03"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O01",
    "state_id": "O01.S06",
    "source_ref": "objects.json#/objects/0/state_history/5",
    "event_id": "E027",
    "time": {
      "start_sec": 199,
      "end_sec": 235,
      "start_hms": "00:03:19.000",
      "end_hms": "00:03:55.000"
    },
    "kind": "transition",
    "field": "contents",
    "before": "蛋/糖/奶分层",
    "after": "淡黄均匀液",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E027-01",
      "V-E027-02",
      "V-E027-03"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E027-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 56,
      "section": "B"
    },
    "description": "搅拌棒进入液面",
    "grade": "V1",
    "time": {
      "start_sec": 199.2,
      "end_sec": 199.2,
      "start_hms": "00:03:19.200",
      "end_hms": "00:03:19.200"
    },
    "original_text": "结束时间由 3:54 修至约 3:55；开始由 3:20 修至约 3:19"
  }
]
```

#### GX010021-T1-001-F05

中性核验问题：该动作段结束前，容器内材料呈现哪些可见外观特征？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "objects",
    "object_id": "O07",
    "state_id": "O07.S02",
    "source_ref": "objects.json#/objects/6/state_history/1",
    "event_id": "E027",
    "time": {
      "start_sec": 199,
      "end_sec": 235,
      "start_hms": "00:03:19.000",
      "end_hms": "00:03:55.000"
    },
    "kind": "observation",
    "field": "mixing_round",
    "before": null,
    "after": 1,
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E027-01",
      "V-E027-02",
      "V-E027-03"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O01",
    "state_id": "O01.S06",
    "source_ref": "objects.json#/objects/0/state_history/5",
    "event_id": "E027",
    "time": {
      "start_sec": 199,
      "end_sec": 235,
      "start_hms": "00:03:19.000",
      "end_hms": "00:03:55.000"
    },
    "kind": "transition",
    "field": "contents",
    "before": "蛋/糖/奶分层",
    "after": "淡黄均匀液",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E027-01",
      "V-E027-02",
      "V-E027-03"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E027-02",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 56,
      "section": "B"
    },
    "description": "搅拌、混合液渐均匀",
    "grade": "V1",
    "time": {
      "start_sec": 200.2,
      "end_sec": 234.2,
      "start_hms": "00:03:20.200",
      "end_hms": "00:03:54.200"
    },
    "original_text": "结束时间由 3:54 修至约 3:55；开始由 3:20 修至约 3:19"
  },
  {
    "id": "V-E027-03",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 56,
      "section": "B"
    },
    "description": "搅拌棒提离",
    "grade": "V1",
    "time": {
      "start_sec": 235.2,
      "end_sec": 235.2,
      "start_hms": "00:03:55.200",
      "end_hms": "00:03:55.200"
    },
    "original_text": "结束时间由 3:54 修至约 3:55；开始由 3:20 修至约 3:19"
  }
]
```

#### GX010021-T1-001-F06

中性核验问题：194–239.3秒前后涉及的混合容器能否连续识别为同一物体？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "objects",
    "object_id": "O07",
    "state_id": "O07.S02",
    "source_ref": "objects.json#/objects/6/state_history/1",
    "event_id": "E027",
    "time": {
      "start_sec": 199,
      "end_sec": 235,
      "start_hms": "00:03:19.000",
      "end_hms": "00:03:55.000"
    },
    "kind": "observation",
    "field": "mixing_round",
    "before": null,
    "after": 1,
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E027-01",
      "V-E027-02",
      "V-E027-03"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O07",
    "state_id": "O07.S05",
    "source_ref": "objects.json#/objects/6/state_history/2",
    "event_id": "E028",
    "time": {
      "start_sec": 234.0,
      "end_sec": 239.0,
      "start_hms": "00:03:54.000",
      "end_hms": "00:03:59.000"
    },
    "kind": "transition",
    "field": "location",
    "before": null,
    "after": "提离混合容器并置左台面",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E028-01"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O01",
    "state_id": "O01.S06",
    "source_ref": "objects.json#/objects/0/state_history/5",
    "event_id": "E027",
    "time": {
      "start_sec": 199,
      "end_sec": 235,
      "start_hms": "00:03:19.000",
      "end_hms": "00:03:55.000"
    },
    "kind": "transition",
    "field": "contents",
    "before": "蛋/糖/奶分层",
    "after": "淡黄均匀液",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E027-01",
      "V-E027-02",
      "V-E027-03"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E027-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 56,
      "section": "B"
    },
    "description": "搅拌棒进入液面",
    "grade": "V1",
    "time": {
      "start_sec": 199.2,
      "end_sec": 199.2,
      "start_hms": "00:03:19.200",
      "end_hms": "00:03:19.200"
    },
    "original_text": "结束时间由 3:54 修至约 3:55；开始由 3:20 修至约 3:19"
  },
  {
    "id": "V-E028-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 57,
      "section": "B"
    },
    "description": "打蛋器置左侧台面",
    "grade": "V1",
    "time": {
      "start_sec": 236.2,
      "end_sec": 238.2,
      "start_hms": "00:03:56.200",
      "end_hms": "00:03:58.200"
    },
    "original_text": "无需修改"
  }
]
```

#### GX010021-T1-001-F07

中性核验问题：动作段与其后放置动作中的器具能否连续识别为同一物体？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "objects",
    "object_id": "O07",
    "state_id": "O07.S02",
    "source_ref": "objects.json#/objects/6/state_history/1",
    "event_id": "E027",
    "time": {
      "start_sec": 199,
      "end_sec": 235,
      "start_hms": "00:03:19.000",
      "end_hms": "00:03:55.000"
    },
    "kind": "observation",
    "field": "mixing_round",
    "before": null,
    "after": 1,
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E027-01",
      "V-E027-02",
      "V-E027-03"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O07",
    "state_id": "O07.S05",
    "source_ref": "objects.json#/objects/6/state_history/2",
    "event_id": "E028",
    "time": {
      "start_sec": 234.0,
      "end_sec": 239.0,
      "start_hms": "00:03:54.000",
      "end_hms": "00:03:59.000"
    },
    "kind": "transition",
    "field": "location",
    "before": null,
    "after": "提离混合容器并置左台面",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E028-01"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O01",
    "state_id": "O01.S06",
    "source_ref": "objects.json#/objects/0/state_history/5",
    "event_id": "E027",
    "time": {
      "start_sec": 199,
      "end_sec": 235,
      "start_hms": "00:03:19.000",
      "end_hms": "00:03:55.000"
    },
    "kind": "transition",
    "field": "contents",
    "before": "蛋/糖/奶分层",
    "after": "淡黄均匀液",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E027-01",
      "V-E027-02",
      "V-E027-03"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E027-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 56,
      "section": "B"
    },
    "description": "搅拌棒进入液面",
    "grade": "V1",
    "time": {
      "start_sec": 199.2,
      "end_sec": 199.2,
      "start_hms": "00:03:19.200",
      "end_hms": "00:03:19.200"
    },
    "original_text": "结束时间由 3:54 修至约 3:55；开始由 3:20 修至约 3:19"
  },
  {
    "id": "V-E027-03",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 56,
      "section": "B"
    },
    "description": "搅拌棒提离",
    "grade": "V1",
    "time": {
      "start_sec": 235.2,
      "end_sec": 235.2,
      "start_hms": "00:03:55.200",
      "end_hms": "00:03:55.200"
    },
    "original_text": "结束时间由 3:54 修至约 3:55；开始由 3:20 修至约 3:19"
  },
  {
    "id": "V-E028-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 57,
      "section": "B"
    },
    "description": "打蛋器置左侧台面",
    "grade": "V1",
    "time": {
      "start_sec": 236.2,
      "end_sec": 238.2,
      "start_hms": "00:03:56.200",
      "end_hms": "00:03:58.200"
    },
    "original_text": "无需修改"
  }
]
```

#### GX010021-T1-001-F08

中性核验问题：截至239.3秒，在可见历史中这个器具的同类动作段次序是什么？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "objects",
    "object_id": "O07",
    "state_id": "O07.S02",
    "source_ref": "objects.json#/objects/6/state_history/1",
    "event_id": "E027",
    "time": {
      "start_sec": 199,
      "end_sec": 235,
      "start_hms": "00:03:19.000",
      "end_hms": "00:03:55.000"
    },
    "kind": "observation",
    "field": "mixing_round",
    "before": null,
    "after": 1,
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E027-01",
      "V-E027-02",
      "V-E027-03"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O01",
    "state_id": "O01.S06",
    "source_ref": "objects.json#/objects/0/state_history/5",
    "event_id": "E027",
    "time": {
      "start_sec": 199,
      "end_sec": 235,
      "start_hms": "00:03:19.000",
      "end_hms": "00:03:55.000"
    },
    "kind": "transition",
    "field": "contents",
    "before": "蛋/糖/奶分层",
    "after": "淡黄均匀液",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E027-01",
      "V-E027-02",
      "V-E027-03"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E027-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 56,
      "section": "B"
    },
    "description": "搅拌棒进入液面",
    "grade": "V1",
    "time": {
      "start_sec": 199.2,
      "end_sec": 199.2,
      "start_hms": "00:03:19.200",
      "end_hms": "00:03:19.200"
    },
    "original_text": "结束时间由 3:54 修至约 3:55；开始由 3:20 修至约 3:19"
  },
  {
    "id": "V-E027-02",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 56,
      "section": "B"
    },
    "description": "搅拌、混合液渐均匀",
    "grade": "V1",
    "time": {
      "start_sec": 200.2,
      "end_sec": 234.2,
      "start_hms": "00:03:20.200",
      "end_hms": "00:03:54.200"
    },
    "original_text": "结束时间由 3:54 修至约 3:55；开始由 3:20 修至约 3:19"
  }
]
```

### GX010021-T2-002

原候选答案（未核验）：
```json
{
  "effective_choice": "oil_permitted_for_this_pan_preparation",
  "applicable_scope": "本次烤模处理；不等于可用油替代面糊内黄油",
  "context_conditions": [
    "没有烘焙纸：操作者自述",
    "没有剩余黄油：操作者自述"
  ],
  "candidate_revision_chain": [
    "R39",
    "R41",
    "R43"
  ],
  "factual_state": "模底见油且已倾斜旋转",
  "inner_wall_coverage": "unknown",
  "rationale": "R43的yes需用R41/R42消解对象与用途；许可不等于内壁涂覆完成。"
}
```

完整任务定义（内部原样快照）：
```json
{
  "task_id": "GX010021-T2-002",
  "episode_id": "GX010021",
  "track": "T2",
  "task_type": "T2.2",
  "title": "倒糊入模时材料替代许可与实际处理状态",
  "data_status": "CANDIDATE",
  "human_review": "NOT_REVIEWED",
  "hard_scoring_eligible": false,
  "execution_ready": false,
  "design_refs": [
    "4.2",
    "5.4",
    "6.2"
  ],
  "trigger": {
    "mode": "query_snapshot",
    "media_time": 641.3,
    "scheduling_status": "CANDIDATE_CHECKPOINT"
  },
  "observation_cutoff": 641.3,
  "reference_event_ids": [
    "E049",
    "E053"
  ],
  "reference_object_ids": [
    "O12",
    "O13",
    "O15"
  ],
  "reference_facts": [
    {
      "artifact": "annotations",
      "record_id": "R39",
      "source_ref": "../../annotations.json#/texts/38",
      "source_index": 38,
      "text": "Use a parchment paper to line the baking tray.",
      "text_type": "Instruction-Clarification",
      "time": {
        "start_sec": 538.698,
        "end_sec": 538.698,
        "start_hms": "00:08:58.698",
        "end_hms": "00:08:58.698"
      },
      "evidence_ids": [
        "T-R39"
      ],
      "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
    },
    {
      "artifact": "annotations",
      "record_id": "R40",
      "source_ref": "../../annotations.json#/texts/39",
      "source_index": 39,
      "text": "I don't have a parchment paper.",
      "text_type": "User-Comment",
      "time": {
        "start_sec": 544.398,
        "end_sec": 544.398,
        "start_hms": "00:09:04.398",
        "end_hms": "00:09:04.398"
      },
      "evidence_ids": [
        "T-R40"
      ],
      "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
    },
    {
      "artifact": "annotations",
      "record_id": "R41",
      "source_ref": "../../annotations.json#/texts/40",
      "source_index": 40,
      "text": "You can then use some of the leftover butter from the melt to line up the tray.",
      "text_type": "Instruction-Clarification",
      "time": {
        "start_sec": 546.378,
        "end_sec": 546.378,
        "start_hms": "00:09:06.378",
        "end_hms": "00:09:06.378"
      },
      "evidence_ids": [
        "T-R41"
      ],
      "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
    },
    {
      "artifact": "annotations",
      "record_id": "R42",
      "source_ref": "../../annotations.json#/texts/41",
      "source_index": 41,
      "text": "I don't have any leftover butter, should I use oil instead?",
      "text_type": "User-Question",
      "time": {
        "start_sec": 552.478,
        "end_sec": 552.478,
        "start_hms": "00:09:12.478",
        "end_hms": "00:09:12.478"
      },
      "evidence_ids": [
        "T-R42"
      ],
      "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
    },
    {
      "artifact": "annotations",
      "record_id": "R43",
      "source_ref": "../../annotations.json#/texts/42",
      "source_index": 42,
      "text": "Yes, you can use oil.",
      "text_type": "Instruction-Clarification",
      "time": {
        "start_sec": 556.368,
        "end_sec": 556.368,
        "start_hms": "00:09:16.368",
        "end_hms": "00:09:16.368"
      },
      "evidence_ids": [
        "T-R43"
      ],
      "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
    },
    {
      "artifact": "events",
      "event_id": "E049",
      "source_ref": "events.json#/events/48/facts/1",
      "field": "inner_wall_oil_film",
      "value": null,
      "status": "UNCERTAIN",
      "evidence_ids": [
        "V-E049-01",
        "V-E049-02",
        "I-E049-01",
        "T-R43",
        "T-R45"
      ],
      "reason": "模底见油、倾斜旋转不证明内壁油膜或覆盖程度；R45评价不升级事实。",
      "use": "CANDIDATE_REFERENCE_ONLY"
    },
    {
      "artifact": "objects",
      "object_id": "O12",
      "state_id": "O12.S01",
      "source_ref": "objects.json#/objects/11/state_history/0",
      "event_id": "E049",
      "time": {
        "start_sec": 560,
        "end_sec": 581,
        "start_hms": "00:09:20.000",
        "end_hms": "00:09:41.000"
      },
      "kind": "transition",
      "field": "oil_at_bottom",
      "before": null,
      "after": "模底见少量油；烤模被倾斜旋转",
      "status": "REPORTED_SUPPORTED",
      "evidence_ids": [
        "V-E049-01",
        "V-E049-02"
      ],
      "use": "CANDIDATE_REFERENCE_ONLY"
    },
    {
      "artifact": "objects",
      "object_id": "O12",
      "state_id": "O12.S02",
      "source_ref": "objects.json#/objects/11/state_history/1",
      "event_id": "E049",
      "time": {
        "start_sec": 560,
        "end_sec": 581,
        "start_hms": "00:09:20.000",
        "end_hms": "00:09:41.000"
      },
      "kind": "transition",
      "field": "inner_wall_oil_film",
      "before": null,
      "after": null,
      "status": "UNCERTAIN",
      "evidence_ids": [
        "V-E049-01",
        "V-E049-02",
        "I-E049-01",
        "T-R43",
        "T-R45"
      ],
      "use": "CANDIDATE_REFERENCE_ONLY"
    }
  ],
  "evidence_refs": [
    {
      "evidence_id": "T-R39",
      "registry_ref": "events.json#/evidence/115",
      "source": {
        "path": "source/annotations.json",
        "section": "texts[38]"
      },
      "time": {
        "start_sec": 538.698,
        "end_sec": 538.698,
        "start_hms": "00:08:58.698",
        "end_hms": "00:08:58.698"
      },
      "kind": "ego_mc_text",
      "grade": "TEXT",
      "description": "原始Ego-MC线索，非视觉事实。",
      "role": "最初烤模处理建议",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 538.698,
          "end_sec": 538.698,
          "start_hms": "00:08:58.698",
          "end_hms": "00:08:58.698"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    },
    {
      "evidence_id": "T-R40",
      "registry_ref": "events.json#/evidence/116",
      "source": {
        "path": "source/annotations.json",
        "section": "texts[39]"
      },
      "time": {
        "start_sec": 544.398,
        "end_sec": 544.398,
        "start_hms": "00:09:04.398",
        "end_hms": "00:09:04.398"
      },
      "kind": "ego_mc_text",
      "grade": "TEXT",
      "description": "原始Ego-MC线索，非视觉事实。",
      "role": "没有烘焙纸的自述条件",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 544.398,
          "end_sec": 544.398,
          "start_hms": "00:09:04.398",
          "end_hms": "00:09:04.398"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    },
    {
      "evidence_id": "T-R41",
      "registry_ref": "events.json#/evidence/117",
      "source": {
        "path": "source/annotations.json",
        "section": "texts[40]"
      },
      "time": {
        "start_sec": 546.378,
        "end_sec": 546.378,
        "start_hms": "00:09:06.378",
        "end_hms": "00:09:06.378"
      },
      "kind": "ego_mc_text",
      "grade": "TEXT",
      "description": "原始Ego-MC线索，非视觉事实。",
      "role": "剩余黄油替代建议及作用范围",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 546.378,
          "end_sec": 546.378,
          "start_hms": "00:09:06.378",
          "end_hms": "00:09:06.378"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    },
    {
      "evidence_id": "T-R42",
      "registry_ref": "events.json#/evidence/118",
      "source": {
        "path": "source/annotations.json",
        "section": "texts[41]"
      },
      "time": {
        "start_sec": 552.478,
        "end_sec": 552.478,
        "start_hms": "00:09:12.478",
        "end_hms": "00:09:12.478"
      },
      "kind": "ego_mc_text",
      "grade": "TEXT",
      "description": "原始Ego-MC线索，非视觉事实。",
      "role": "没有剩余黄油并提议用油的自述条件",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 552.478,
          "end_sec": 552.478,
          "start_hms": "00:09:12.478",
          "end_hms": "00:09:12.478"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    },
    {
      "evidence_id": "T-R43",
      "registry_ref": "events.json#/evidence/119",
      "source": {
        "path": "source/annotations.json",
        "section": "texts[42]"
      },
      "time": {
        "start_sec": 556.368,
        "end_sec": 556.368,
        "start_hms": "00:09:16.368",
        "end_hms": "00:09:16.368"
      },
      "kind": "ego_mc_text",
      "grade": "TEXT",
      "description": "原始Ego-MC线索，非视觉事实。",
      "role": "指导者许可",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 556.368,
          "end_sec": 556.368,
          "start_hms": "00:09:16.368",
          "end_hms": "00:09:16.368"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    },
    {
      "evidence_id": "V-E049-01",
      "registry_ref": "events.json#/evidence/64",
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 78,
        "section": "B"
      },
      "time": {
        "start_sec": 560.2,
        "end_sec": 562.2,
        "start_hms": "00:09:20.200",
        "end_hms": "00:09:22.200"
      },
      "kind": "reported_visual_observation",
      "grade": "V1",
      "description": "油流/油滴进入模底",
      "role": "模底实际见油",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 560.2,
          "end_sec": 562.2,
          "start_hms": "00:09:20.200",
          "end_hms": "00:09:22.200"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    },
    {
      "evidence_id": "V-E049-02",
      "registry_ref": "events.json#/evidence/65",
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 78,
        "section": "B"
      },
      "time": {
        "start_sec": 567.2,
        "end_sec": 579.2,
        "start_hms": "00:09:27.200",
        "end_hms": "00:09:39.200"
      },
      "kind": "reported_visual_observation",
      "grade": "V1",
      "description": "持模倾斜旋转，内壁油膜不可辨",
      "role": "烤模倾斜旋转；内壁油膜不可辨",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 567.2,
          "end_sec": 579.2,
          "start_hms": "00:09:27.200",
          "end_hms": "00:09:39.200"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    },
    {
      "evidence_id": "V-E053-01",
      "registry_ref": "events.json#/evidence/71",
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 82,
        "section": "B"
      },
      "time": {
        "start_sec": 633.2,
        "end_sec": 641.2,
        "start_hms": "00:10:33.200",
        "end_hms": "00:10:41.200"
      },
      "kind": "reported_visual_observation",
      "grade": "V1",
      "description": "混合容器面糊倾入烤模",
      "role": "当前倒糊入模锚点；不含后续刮净",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 633.2,
          "end_sec": 641.2,
          "start_hms": "00:10:33.200",
          "end_hms": "00:10:41.200"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    }
  ],
  "normative_rules": [
    {
      "rule_id": "GX010021-RULE-CAND-R39",
      "status": "CANDIDATE",
      "record_id": "R39",
      "evidence_ids": [
        "T-R39"
      ],
      "statement": "Use a parchment paper to line the baking tray.",
      "issued_at": 538.698,
      "effective_from": null,
      "candidate_effective_not_before": 538.698,
      "scope": "本次烤模处理",
      "condition": "先提出烘焙纸",
      "supersedes": null,
      "supersedes_status": "NOT_ASSERTED",
      "release_note": "点时间戳不是整段话结束/Runner公开时间；effective_from需独立核验，当前不可执行。"
    },
    {
      "rule_id": "GX010021-RULE-CAND-R41",
      "status": "CANDIDATE",
      "record_id": "R41",
      "evidence_ids": [
        "T-R41"
      ],
      "statement": "You can then use some of the leftover butter from the melt to line up the tray.",
      "issued_at": 546.378,
      "effective_from": null,
      "candidate_effective_not_before": 546.378,
      "scope": "本次烤模处理",
      "condition": "R40称没有烘焙纸后，建议用融化剩余黄油",
      "supersedes": "GX010021-RULE-CAND-R39",
      "supersedes_status": "PENDING_CONTEXT_REVIEW",
      "release_note": "点时间戳不是整段话结束/Runner公开时间；effective_from需独立核验，当前不可执行。"
    },
    {
      "rule_id": "GX010021-RULE-CAND-R43",
      "status": "CANDIDATE",
      "record_id": "R43",
      "evidence_ids": [
        "T-R43"
      ],
      "statement": "Yes, you can use oil.",
      "issued_at": 556.368,
      "effective_from": null,
      "candidate_effective_not_before": 556.368,
      "scope": "本次烤模处理",
      "condition": "R42称无剩余黄油并提议用油；yes的对象与作用须依赖上下文",
      "supersedes": "GX010021-RULE-CAND-R41",
      "supersedes_status": "PENDING_CONTEXT_REVIEW",
      "release_note": "点时间戳不是整段话结束/Runner公开时间；effective_from需独立核验，当前不可执行。"
    }
  ],
  "candidate_answer": {
    "effective_choice": "oil_permitted_for_this_pan_preparation",
    "applicable_scope": "本次烤模处理；不等于可用油替代面糊内黄油",
    "context_conditions": [
      "没有烘焙纸：操作者自述",
      "没有剩余黄油：操作者自述"
    ],
    "candidate_revision_chain": [
      "R39",
      "R41",
      "R43"
    ],
    "factual_state": "模底见油且已倾斜旋转",
    "inner_wall_coverage": "unknown",
    "rationale": "R43的yes需用R41/R42消解对象与用途；许可不等于内壁涂覆完成。"
  },
  "gold_answer": null,
  "scorable_conditions": [
    "上下文独立核验后评分当前允许用油与用途范围，不能只匹配R43的yes。",
    "R40/R42是对话条件自述，不作为物资库存定量事实；局部替代不扩展为全菜谱规则。",
    "证据覆盖原方案、条件、替代/许可和烤模实际观察；内壁状态按可判定性裁决。",
    "Revision Consistency仍缺修订前配对Probe，此单题不能算整组修订一致率。"
  ],
  "pending_verification": [
    "核验R39→R41→R43是否为该烤模的局部替代、条件和生效/公开时刻。",
    "核验560.2–579.2s倒油/旋转与633.2–641.2s同一烤模开始接收面糊。",
    "R43独句存在语言省略，仍须做Current-only/Instruction-only审核；若当前有效指令已经整理出全链，则可能没有历史增益。"
  ],
  "existing_review_queue_ids": [
    "RQ03"
  ],
  "evidence_quality": {
    "status": "NOT_INDEPENDENTLY_VERIFIED",
    "directly_observed_in_this_round": false,
    "visual_source": "ARCHIVED_AI_REPORTS_ONLY",
    "numeric_confidence": null,
    "annotation_disagreements": "继承字段不确定性与历史修订；未做人类一致性测量。"
  },
  "visibility_regime": "G1",
  "causal_constraints": {
    "max_media_time": 641.3,
    "require_availability_time_check": true,
    "evaluator_reference_visible_to_agent": false,
    "event_id_link_is_not_full_record_access": true,
    "unknown_requires_observability_adjudication": true
  },
  "protocol_tbd": [
    "输入窗口/采样与实际availability_time",
    "运行预算/超时",
    "最终输出Schema/证据匹配阈值",
    "近期窗口长度/B0成本控制",
    "Evidence Score容差/无关片段惩罚/最小集裁决"
  ],
  "earliest_answerable_time": {
    "start_sec": 633.2,
    "end_sec": 641.2,
    "start_hms": "00:10:33.200",
    "end_hms": "00:10:41.200"
  },
  "earliest_answerable_time_status": "CANDIDATE_ENVELOPE_NOT_VERIFIED_FIRST_TIME",
  "question": "面糊正在倒入此前准备的烤模。结合此前指导者与操作者关于处理烤模的问答，此时采用食用油是否得到允许，许可适用于什么对象和用途、依赖哪些对话条件？请同时区分已观察到的烤模处理动作与仍无法确认的处理结果。",
  "answer_type": {
    "fields": [
      "effective_choice",
      "applicable_scope",
      "context_conditions",
      "factual_state",
      "inner_wall_coverage",
      "evidence_refs",
      "uncertainty"
    ],
    "allow_unknown": true
  },
  "required_evidence_sets": [
    [
      {
        "evidence_id": "T-R39",
        "registry_ref": "events.json#/evidence/115",
        "source": {
          "path": "source/annotations.json",
          "section": "texts[38]"
        },
        "time": {
          "start_sec": 538.698,
          "end_sec": 538.698,
          "start_hms": "00:08:58.698",
          "end_hms": "00:08:58.698"
        },
        "kind": "ego_mc_text",
        "grade": "TEXT",
        "description": "原始Ego-MC线索，非视觉事实。",
        "role": "最初烤模处理建议",
        "media_ref": {
          "path": "../../source/GX010021.MP4",
          "time": {
            "start_sec": 538.698,
            "end_sec": 538.698,
            "start_hms": "00:08:58.698",
            "end_hms": "00:08:58.698"
          }
        },
        "availability_time": null,
        "human_review": "NOT_REVIEWED"
      },
      {
        "evidence_id": "T-R40",
        "registry_ref": "events.json#/evidence/116",
        "source": {
          "path": "source/annotations.json",
          "section": "texts[39]"
        },
        "time": {
          "start_sec": 544.398,
          "end_sec": 544.398,
          "start_hms": "00:09:04.398",
          "end_hms": "00:09:04.398"
        },
        "kind": "ego_mc_text",
        "grade": "TEXT",
        "description": "原始Ego-MC线索，非视觉事实。",
        "role": "没有烘焙纸的自述条件",
        "media_ref": {
          "path": "../../source/GX010021.MP4",
          "time": {
            "start_sec": 544.398,
            "end_sec": 544.398,
            "start_hms": "00:09:04.398",
            "end_hms": "00:09:04.398"
          }
        },
        "availability_time": null,
        "human_review": "NOT_REVIEWED"
      },
      {
        "evidence_id": "T-R41",
        "registry_ref": "events.json#/evidence/117",
        "source": {
          "path": "source/annotations.json",
          "section": "texts[40]"
        },
        "time": {
          "start_sec": 546.378,
          "end_sec": 546.378,
          "start_hms": "00:09:06.378",
          "end_hms": "00:09:06.378"
        },
        "kind": "ego_mc_text",
        "grade": "TEXT",
        "description": "原始Ego-MC线索，非视觉事实。",
        "role": "剩余黄油替代建议及作用范围",
        "media_ref": {
          "path": "../../source/GX010021.MP4",
          "time": {
            "start_sec": 546.378,
            "end_sec": 546.378,
            "start_hms": "00:09:06.378",
            "end_hms": "00:09:06.378"
          }
        },
        "availability_time": null,
        "human_review": "NOT_REVIEWED"
      },
      {
        "evidence_id": "T-R42",
        "registry_ref": "events.json#/evidence/118",
        "source": {
          "path": "source/annotations.json",
          "section": "texts[41]"
        },
        "time": {
          "start_sec": 552.478,
          "end_sec": 552.478,
          "start_hms": "00:09:12.478",
          "end_hms": "00:09:12.478"
        },
        "kind": "ego_mc_text",
        "grade": "TEXT",
        "description": "原始Ego-MC线索，非视觉事实。",
        "role": "没有剩余黄油并提议用油的自述条件",
        "media_ref": {
          "path": "../../source/GX010021.MP4",
          "time": {
            "start_sec": 552.478,
            "end_sec": 552.478,
            "start_hms": "00:09:12.478",
            "end_hms": "00:09:12.478"
          }
        },
        "availability_time": null,
        "human_review": "NOT_REVIEWED"
      },
      {
        "evidence_id": "T-R43",
        "registry_ref": "events.json#/evidence/119",
        "source": {
          "path": "source/annotations.json",
          "section": "texts[42]"
        },
        "time": {
          "start_sec": 556.368,
          "end_sec": 556.368,
          "start_hms": "00:09:16.368",
          "end_hms": "00:09:16.368"
        },
        "kind": "ego_mc_text",
        "grade": "TEXT",
        "description": "原始Ego-MC线索，非视觉事实。",
        "role": "指导者许可",
        "media_ref": {
          "path": "../../source/GX010021.MP4",
          "time": {
            "start_sec": 556.368,
            "end_sec": 556.368,
            "start_hms": "00:09:16.368",
            "end_hms": "00:09:16.368"
          }
        },
        "availability_time": null,
        "human_review": "NOT_REVIEWED"
      },
      {
        "evidence_id": "V-E049-01",
        "registry_ref": "events.json#/evidence/64",
        "source": {
          "path": "annotation_reports/verification_report.md",
          "line": 78,
          "section": "B"
        },
        "time": {
          "start_sec": 560.2,
          "end_sec": 562.2,
          "start_hms": "00:09:20.200",
          "end_hms": "00:09:22.200"
        },
        "kind": "reported_visual_observation",
        "grade": "V1",
        "description": "油流/油滴进入模底",
        "role": "模底实际见油",
        "media_ref": {
          "path": "../../source/GX010021.MP4",
          "time": {
            "start_sec": 560.2,
            "end_sec": 562.2,
            "start_hms": "00:09:20.200",
            "end_hms": "00:09:22.200"
          }
        },
        "availability_time": null,
        "human_review": "NOT_REVIEWED"
      },
      {
        "evidence_id": "V-E049-02",
        "registry_ref": "events.json#/evidence/65",
        "source": {
          "path": "annotation_reports/verification_report.md",
          "line": 78,
          "section": "B"
        },
        "time": {
          "start_sec": 567.2,
          "end_sec": 579.2,
          "start_hms": "00:09:27.200",
          "end_hms": "00:09:39.200"
        },
        "kind": "reported_visual_observation",
        "grade": "V1",
        "description": "持模倾斜旋转，内壁油膜不可辨",
        "role": "烤模倾斜旋转；内壁油膜不可辨",
        "media_ref": {
          "path": "../../source/GX010021.MP4",
          "time": {
            "start_sec": 567.2,
            "end_sec": 579.2,
            "start_hms": "00:09:27.200",
            "end_hms": "00:09:39.200"
          }
        },
        "availability_time": null,
        "human_review": "NOT_REVIEWED"
      }
    ]
  ],
  "reasoning_relation": [
    "局部规则替代（待核验）",
    "条件适用",
    "省略许可的作用范围消解",
    "许可与事实状态分离"
  ],
  "history_necessity": {
    "status": "PENDING_RECENT_ONLY_AND_NO_VIDEO_AUDIT",
    "long_horizon_claim": "NOT_ESTABLISHED",
    "recall_only": false,
    "nonredundant_evidence": "原建议/自述条件/替代/许可/实际处理状态；最小性仍须删除片段审核。",
    "shortcut_risk": "如果合法当前指令完整复述替代链，须降级或剔除。"
  },
  "current_process_evidence_ids": [
    "V-E053-01"
  ],
  "query_time": 641.3,
  "dependency_span": 102.602,
  "dependency_span_unit": "seconds",
  "dependency_span_basis": {
    "earliest_required_evidence_start": 538.698,
    "note": "仅描述候选证据跨度，不等于通过长程必要性门禁。"
  },
  "required_evidence_sets_status": "PROPOSED_MINIMAL_SUFFICIENT; 独立审核与片段删除实验前不声明已最小充分",
  "probe_isolation": {
    "required": true,
    "write_back_to_main_agent": false,
    "method": "冻结t_q主执行状态，复制到只读分支，回答后丢弃分支；主状态继续",
    "fallback": "预先声明并验证等价隔离策略及额外成本",
    "verified": false
  },
  "agent_facing_input": {
    "interface": "query_snapshot(query, at_media_time, isolated=true)",
    "expose_only_at_query_time": [
      "question",
      "answer_type"
    ],
    "private_fields": "其余均为Evaluator私有，不作为Agent输入",
    "answer_evidence_refs": "Agent引用已公开observation/指令；私有V-/T-证据ID仅由Evaluator映射"
  }
}
```

#### GX010021-T2-002-F01

中性核验问题：源对话记录R39的说话者、字面内容与视频实际话语是否一致？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "annotations",
    "record_id": "R39",
    "source_ref": "../../annotations.json#/texts/38",
    "source_index": 38,
    "text": "Use a parchment paper to line the baking tray.",
    "text_type": "Instruction-Clarification",
    "time": {
      "start_sec": 538.698,
      "end_sec": 538.698,
      "start_hms": "00:08:58.698",
      "end_hms": "00:08:58.698"
    },
    "evidence_ids": [
      "T-R39"
    ],
    "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "T-R39",
    "kind": "ego_mc_text",
    "source": {
      "path": "source/annotations.json",
      "section": "texts[38]"
    },
    "description": "原始Ego-MC线索，非视觉事实。",
    "grade": "TEXT",
    "time": {
      "start_sec": 538.698,
      "end_sec": 538.698,
      "start_hms": "00:08:58.698",
      "end_hms": "00:08:58.698"
    },
    "original_text": "Use a parchment paper to line the baking tray."
  }
]
```

#### GX010021-T2-002-F02

中性核验问题：源对话记录R40的说话者、字面内容与视频实际话语是否一致？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "annotations",
    "record_id": "R40",
    "source_ref": "../../annotations.json#/texts/39",
    "source_index": 39,
    "text": "I don't have a parchment paper.",
    "text_type": "User-Comment",
    "time": {
      "start_sec": 544.398,
      "end_sec": 544.398,
      "start_hms": "00:09:04.398",
      "end_hms": "00:09:04.398"
    },
    "evidence_ids": [
      "T-R40"
    ],
    "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "T-R40",
    "kind": "ego_mc_text",
    "source": {
      "path": "source/annotations.json",
      "section": "texts[39]"
    },
    "description": "原始Ego-MC线索，非视觉事实。",
    "grade": "TEXT",
    "time": {
      "start_sec": 544.398,
      "end_sec": 544.398,
      "start_hms": "00:09:04.398",
      "end_hms": "00:09:04.398"
    },
    "original_text": "I don't have a parchment paper."
  }
]
```

#### GX010021-T2-002-F03

中性核验问题：源对话记录R41的说话者、字面内容与视频实际话语是否一致？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "annotations",
    "record_id": "R41",
    "source_ref": "../../annotations.json#/texts/40",
    "source_index": 40,
    "text": "You can then use some of the leftover butter from the melt to line up the tray.",
    "text_type": "Instruction-Clarification",
    "time": {
      "start_sec": 546.378,
      "end_sec": 546.378,
      "start_hms": "00:09:06.378",
      "end_hms": "00:09:06.378"
    },
    "evidence_ids": [
      "T-R41"
    ],
    "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "T-R41",
    "kind": "ego_mc_text",
    "source": {
      "path": "source/annotations.json",
      "section": "texts[40]"
    },
    "description": "原始Ego-MC线索，非视觉事实。",
    "grade": "TEXT",
    "time": {
      "start_sec": 546.378,
      "end_sec": 546.378,
      "start_hms": "00:09:06.378",
      "end_hms": "00:09:06.378"
    },
    "original_text": "You can then use some of the leftover butter from the melt to line up the tray."
  }
]
```

#### GX010021-T2-002-F04

中性核验问题：源对话记录R42的说话者、字面内容与视频实际话语是否一致？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "annotations",
    "record_id": "R42",
    "source_ref": "../../annotations.json#/texts/41",
    "source_index": 41,
    "text": "I don't have any leftover butter, should I use oil instead?",
    "text_type": "User-Question",
    "time": {
      "start_sec": 552.478,
      "end_sec": 552.478,
      "start_hms": "00:09:12.478",
      "end_hms": "00:09:12.478"
    },
    "evidence_ids": [
      "T-R42"
    ],
    "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "T-R42",
    "kind": "ego_mc_text",
    "source": {
      "path": "source/annotations.json",
      "section": "texts[41]"
    },
    "description": "原始Ego-MC线索，非视觉事实。",
    "grade": "TEXT",
    "time": {
      "start_sec": 552.478,
      "end_sec": 552.478,
      "start_hms": "00:09:12.478",
      "end_hms": "00:09:12.478"
    },
    "original_text": "I don't have any leftover butter, should I use oil instead?"
  }
]
```

#### GX010021-T2-002-F05

中性核验问题：源对话记录R43的说话者、字面内容与视频实际话语是否一致？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "annotations",
    "record_id": "R43",
    "source_ref": "../../annotations.json#/texts/42",
    "source_index": 42,
    "text": "Yes, you can use oil.",
    "text_type": "Instruction-Clarification",
    "time": {
      "start_sec": 556.368,
      "end_sec": 556.368,
      "start_hms": "00:09:16.368",
      "end_hms": "00:09:16.368"
    },
    "evidence_ids": [
      "T-R43"
    ],
    "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
  },
  {
    "artifact": "events",
    "event_id": "E049",
    "source_ref": "events.json#/events/48/facts/1",
    "field": "inner_wall_oil_film",
    "value": null,
    "status": "UNCERTAIN",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02",
      "I-E049-01",
      "T-R43",
      "T-R45"
    ],
    "reason": "模底见油、倾斜旋转不证明内壁油膜或覆盖程度；R45评价不升级事实。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O12",
    "state_id": "O12.S02",
    "source_ref": "objects.json#/objects/11/state_history/1",
    "event_id": "E049",
    "time": {
      "start_sec": 560,
      "end_sec": 581,
      "start_hms": "00:09:20.000",
      "end_hms": "00:09:41.000"
    },
    "kind": "transition",
    "field": "inner_wall_oil_film",
    "before": null,
    "after": null,
    "status": "UNCERTAIN",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02",
      "I-E049-01",
      "T-R43",
      "T-R45"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "T-R43",
    "kind": "ego_mc_text",
    "source": {
      "path": "source/annotations.json",
      "section": "texts[42]"
    },
    "description": "原始Ego-MC线索，非视觉事实。",
    "grade": "TEXT",
    "time": {
      "start_sec": 556.368,
      "end_sec": 556.368,
      "start_hms": "00:09:16.368",
      "end_hms": "00:09:16.368"
    },
    "original_text": "Yes, you can use oil."
  }
]
```

#### GX010021-T2-002-F06

中性核验问题：结合这组问答，各建议或许可指向什么对象、用途和条件，彼此关系是什么？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "annotations",
    "record_id": "R39",
    "source_ref": "../../annotations.json#/texts/38",
    "source_index": 38,
    "text": "Use a parchment paper to line the baking tray.",
    "text_type": "Instruction-Clarification",
    "time": {
      "start_sec": 538.698,
      "end_sec": 538.698,
      "start_hms": "00:08:58.698",
      "end_hms": "00:08:58.698"
    },
    "evidence_ids": [
      "T-R39"
    ],
    "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
  },
  {
    "artifact": "annotations",
    "record_id": "R40",
    "source_ref": "../../annotations.json#/texts/39",
    "source_index": 39,
    "text": "I don't have a parchment paper.",
    "text_type": "User-Comment",
    "time": {
      "start_sec": 544.398,
      "end_sec": 544.398,
      "start_hms": "00:09:04.398",
      "end_hms": "00:09:04.398"
    },
    "evidence_ids": [
      "T-R40"
    ],
    "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
  },
  {
    "artifact": "annotations",
    "record_id": "R41",
    "source_ref": "../../annotations.json#/texts/40",
    "source_index": 40,
    "text": "You can then use some of the leftover butter from the melt to line up the tray.",
    "text_type": "Instruction-Clarification",
    "time": {
      "start_sec": 546.378,
      "end_sec": 546.378,
      "start_hms": "00:09:06.378",
      "end_hms": "00:09:06.378"
    },
    "evidence_ids": [
      "T-R41"
    ],
    "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
  },
  {
    "artifact": "annotations",
    "record_id": "R42",
    "source_ref": "../../annotations.json#/texts/41",
    "source_index": 41,
    "text": "I don't have any leftover butter, should I use oil instead?",
    "text_type": "User-Question",
    "time": {
      "start_sec": 552.478,
      "end_sec": 552.478,
      "start_hms": "00:09:12.478",
      "end_hms": "00:09:12.478"
    },
    "evidence_ids": [
      "T-R42"
    ],
    "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
  },
  {
    "artifact": "annotations",
    "record_id": "R43",
    "source_ref": "../../annotations.json#/texts/42",
    "source_index": 42,
    "text": "Yes, you can use oil.",
    "text_type": "Instruction-Clarification",
    "time": {
      "start_sec": 556.368,
      "end_sec": 556.368,
      "start_hms": "00:09:16.368",
      "end_hms": "00:09:16.368"
    },
    "evidence_ids": [
      "T-R43"
    ],
    "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
  },
  {
    "artifact": "events",
    "event_id": "E049",
    "source_ref": "events.json#/events/48/facts/1",
    "field": "inner_wall_oil_film",
    "value": null,
    "status": "UNCERTAIN",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02",
      "I-E049-01",
      "T-R43",
      "T-R45"
    ],
    "reason": "模底见油、倾斜旋转不证明内壁油膜或覆盖程度；R45评价不升级事实。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O12",
    "state_id": "O12.S02",
    "source_ref": "objects.json#/objects/11/state_history/1",
    "event_id": "E049",
    "time": {
      "start_sec": 560,
      "end_sec": 581,
      "start_hms": "00:09:20.000",
      "end_hms": "00:09:41.000"
    },
    "kind": "transition",
    "field": "inner_wall_oil_film",
    "before": null,
    "after": null,
    "status": "UNCERTAIN",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02",
      "I-E049-01",
      "T-R43",
      "T-R45"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "T-R39",
    "kind": "ego_mc_text",
    "source": {
      "path": "source/annotations.json",
      "section": "texts[38]"
    },
    "description": "原始Ego-MC线索，非视觉事实。",
    "grade": "TEXT",
    "time": {
      "start_sec": 538.698,
      "end_sec": 538.698,
      "start_hms": "00:08:58.698",
      "end_hms": "00:08:58.698"
    },
    "original_text": "Use a parchment paper to line the baking tray."
  },
  {
    "id": "T-R40",
    "kind": "ego_mc_text",
    "source": {
      "path": "source/annotations.json",
      "section": "texts[39]"
    },
    "description": "原始Ego-MC线索，非视觉事实。",
    "grade": "TEXT",
    "time": {
      "start_sec": 544.398,
      "end_sec": 544.398,
      "start_hms": "00:09:04.398",
      "end_hms": "00:09:04.398"
    },
    "original_text": "I don't have a parchment paper."
  },
  {
    "id": "T-R41",
    "kind": "ego_mc_text",
    "source": {
      "path": "source/annotations.json",
      "section": "texts[40]"
    },
    "description": "原始Ego-MC线索，非视觉事实。",
    "grade": "TEXT",
    "time": {
      "start_sec": 546.378,
      "end_sec": 546.378,
      "start_hms": "00:09:06.378",
      "end_hms": "00:09:06.378"
    },
    "original_text": "You can then use some of the leftover butter from the melt to line up the tray."
  },
  {
    "id": "T-R42",
    "kind": "ego_mc_text",
    "source": {
      "path": "source/annotations.json",
      "section": "texts[41]"
    },
    "description": "原始Ego-MC线索，非视觉事实。",
    "grade": "TEXT",
    "time": {
      "start_sec": 552.478,
      "end_sec": 552.478,
      "start_hms": "00:09:12.478",
      "end_hms": "00:09:12.478"
    },
    "original_text": "I don't have any leftover butter, should I use oil instead?"
  },
  {
    "id": "T-R43",
    "kind": "ego_mc_text",
    "source": {
      "path": "source/annotations.json",
      "section": "texts[42]"
    },
    "description": "原始Ego-MC线索，非视觉事实。",
    "grade": "TEXT",
    "time": {
      "start_sec": 556.368,
      "end_sec": 556.368,
      "start_hms": "00:09:16.368",
      "end_hms": "00:09:16.368"
    },
    "original_text": "Yes, you can use oil."
  }
]
```

#### GX010021-T2-002-F07

中性核验问题：560–563秒期间，是否有物质从瓶口进入烤模，进入什么位置？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E049",
    "source_ref": "events.json#/events/48/facts/1",
    "field": "inner_wall_oil_film",
    "value": null,
    "status": "UNCERTAIN",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02",
      "I-E049-01",
      "T-R43",
      "T-R45"
    ],
    "reason": "模底见油、倾斜旋转不证明内壁油膜或覆盖程度；R45评价不升级事实。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O12",
    "state_id": "O12.S01",
    "source_ref": "objects.json#/objects/11/state_history/0",
    "event_id": "E049",
    "time": {
      "start_sec": 560,
      "end_sec": 581,
      "start_hms": "00:09:20.000",
      "end_hms": "00:09:41.000"
    },
    "kind": "transition",
    "field": "oil_at_bottom",
    "before": null,
    "after": "模底见少量油；烤模被倾斜旋转",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O12",
    "state_id": "O12.S02",
    "source_ref": "objects.json#/objects/11/state_history/1",
    "event_id": "E049",
    "time": {
      "start_sec": 560,
      "end_sec": 581,
      "start_hms": "00:09:20.000",
      "end_hms": "00:09:41.000"
    },
    "kind": "transition",
    "field": "inner_wall_oil_film",
    "before": null,
    "after": null,
    "status": "UNCERTAIN",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02",
      "I-E049-01",
      "T-R43",
      "T-R45"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E049-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 78,
      "section": "B"
    },
    "description": "油流/油滴进入模底",
    "grade": "V1",
    "time": {
      "start_sec": 560.2,
      "end_sec": 562.2,
      "start_hms": "00:09:20.200",
      "end_hms": "00:09:22.200"
    },
    "original_text": "改为\"向烤模倒入少量油并倾斜旋转烤模（意图使油分布内壁；是否形成内壁油膜 UNCERTAIN）\"",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  }
]
```

#### GX010021-T2-002-F08

中性核验问题：563–581秒期间，烤模如何被移动、倾斜或旋转？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E049",
    "source_ref": "events.json#/events/48/facts/1",
    "field": "inner_wall_oil_film",
    "value": null,
    "status": "UNCERTAIN",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02",
      "I-E049-01",
      "T-R43",
      "T-R45"
    ],
    "reason": "模底见油、倾斜旋转不证明内壁油膜或覆盖程度；R45评价不升级事实。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O12",
    "state_id": "O12.S01",
    "source_ref": "objects.json#/objects/11/state_history/0",
    "event_id": "E049",
    "time": {
      "start_sec": 560,
      "end_sec": 581,
      "start_hms": "00:09:20.000",
      "end_hms": "00:09:41.000"
    },
    "kind": "transition",
    "field": "oil_at_bottom",
    "before": null,
    "after": "模底见少量油；烤模被倾斜旋转",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O12",
    "state_id": "O12.S02",
    "source_ref": "objects.json#/objects/11/state_history/1",
    "event_id": "E049",
    "time": {
      "start_sec": 560,
      "end_sec": 581,
      "start_hms": "00:09:20.000",
      "end_hms": "00:09:41.000"
    },
    "kind": "transition",
    "field": "inner_wall_oil_film",
    "before": null,
    "after": null,
    "status": "UNCERTAIN",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02",
      "I-E049-01",
      "T-R43",
      "T-R45"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E049-02",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 78,
      "section": "B"
    },
    "description": "持模倾斜旋转，内壁油膜不可辨",
    "grade": "V1",
    "time": {
      "start_sec": 567.2,
      "end_sec": 579.2,
      "start_hms": "00:09:27.200",
      "end_hms": "00:09:39.200"
    },
    "original_text": "改为\"向烤模倒入少量油并倾斜旋转烤模（意图使油分布内壁；是否形成内壁油膜 UNCERTAIN）\"",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  }
]
```

#### GX010021-T2-002-F09

中性核验问题：处理后烤模内壁的表面状态与覆盖范围能否直接辨识？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E049",
    "source_ref": "events.json#/events/48/facts/1",
    "field": "inner_wall_oil_film",
    "value": null,
    "status": "UNCERTAIN",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02",
      "I-E049-01",
      "T-R43",
      "T-R45"
    ],
    "reason": "模底见油、倾斜旋转不证明内壁油膜或覆盖程度；R45评价不升级事实。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O12",
    "state_id": "O12.S01",
    "source_ref": "objects.json#/objects/11/state_history/0",
    "event_id": "E049",
    "time": {
      "start_sec": 560,
      "end_sec": 581,
      "start_hms": "00:09:20.000",
      "end_hms": "00:09:41.000"
    },
    "kind": "transition",
    "field": "oil_at_bottom",
    "before": null,
    "after": "模底见少量油；烤模被倾斜旋转",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O12",
    "state_id": "O12.S02",
    "source_ref": "objects.json#/objects/11/state_history/1",
    "event_id": "E049",
    "time": {
      "start_sec": 560,
      "end_sec": 581,
      "start_hms": "00:09:20.000",
      "end_hms": "00:09:41.000"
    },
    "kind": "transition",
    "field": "inner_wall_oil_film",
    "before": null,
    "after": null,
    "status": "UNCERTAIN",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02",
      "I-E049-01",
      "T-R43",
      "T-R45"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E049-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 78,
      "section": "B"
    },
    "description": "油流/油滴进入模底",
    "grade": "V1",
    "time": {
      "start_sec": 560.2,
      "end_sec": 562.2,
      "start_hms": "00:09:20.200",
      "end_hms": "00:09:22.200"
    },
    "original_text": "改为\"向烤模倒入少量油并倾斜旋转烤模（意图使油分布内壁；是否形成内壁油膜 UNCERTAIN）\"",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  },
  {
    "id": "V-E049-02",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 78,
      "section": "B"
    },
    "description": "持模倾斜旋转，内壁油膜不可辨",
    "grade": "V1",
    "time": {
      "start_sec": 567.2,
      "end_sec": 579.2,
      "start_hms": "00:09:27.200",
      "end_hms": "00:09:39.200"
    },
    "original_text": "改为\"向烤模倒入少量油并倾斜旋转烤模（意图使油分布内壁；是否形成内壁油膜 UNCERTAIN）\"",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  }
]
```

#### GX010021-T2-002-F10

中性核验问题：截至641.3秒，当前发生了哪些容器间的材料转移动作？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E053-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 82,
      "section": "B"
    },
    "description": "混合容器面糊倾入烤模",
    "grade": "V1",
    "time": {
      "start_sec": 633.2,
      "end_sec": 641.2,
      "start_hms": "00:10:33.200",
      "end_hms": "00:10:41.200"
    },
    "original_text": "工具注明\"黑色柄刮刀/勺状工具（身份见 O05 修正）\"",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  }
]
```

#### GX010021-T2-002-F11

中性核验问题：先前接受瓶中物质的烤模与当前接收材料的烤模能否连续关联？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E049",
    "source_ref": "events.json#/events/48/facts/1",
    "field": "inner_wall_oil_film",
    "value": null,
    "status": "UNCERTAIN",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02",
      "I-E049-01",
      "T-R43",
      "T-R45"
    ],
    "reason": "模底见油、倾斜旋转不证明内壁油膜或覆盖程度；R45评价不升级事实。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O12",
    "state_id": "O12.S01",
    "source_ref": "objects.json#/objects/11/state_history/0",
    "event_id": "E049",
    "time": {
      "start_sec": 560,
      "end_sec": 581,
      "start_hms": "00:09:20.000",
      "end_hms": "00:09:41.000"
    },
    "kind": "transition",
    "field": "oil_at_bottom",
    "before": null,
    "after": "模底见少量油；烤模被倾斜旋转",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O12",
    "state_id": "O12.S02",
    "source_ref": "objects.json#/objects/11/state_history/1",
    "event_id": "E049",
    "time": {
      "start_sec": 560,
      "end_sec": 581,
      "start_hms": "00:09:20.000",
      "end_hms": "00:09:41.000"
    },
    "kind": "transition",
    "field": "inner_wall_oil_film",
    "before": null,
    "after": null,
    "status": "UNCERTAIN",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02",
      "I-E049-01",
      "T-R43",
      "T-R45"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E049-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 78,
      "section": "B"
    },
    "description": "油流/油滴进入模底",
    "grade": "V1",
    "time": {
      "start_sec": 560.2,
      "end_sec": 562.2,
      "start_hms": "00:09:20.200",
      "end_hms": "00:09:22.200"
    },
    "original_text": "改为\"向烤模倒入少量油并倾斜旋转烤模（意图使油分布内壁；是否形成内壁油膜 UNCERTAIN）\"",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  },
  {
    "id": "V-E049-02",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 78,
      "section": "B"
    },
    "description": "持模倾斜旋转，内壁油膜不可辨",
    "grade": "V1",
    "time": {
      "start_sec": 567.2,
      "end_sec": 579.2,
      "start_hms": "00:09:27.200",
      "end_hms": "00:09:39.200"
    },
    "original_text": "改为\"向烤模倒入少量油并倾斜旋转烤模（意图使油分布内壁；是否形成内壁油膜 UNCERTAIN）\"",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  },
  {
    "id": "V-E053-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 82,
      "section": "B"
    },
    "description": "混合容器面糊倾入烤模",
    "grade": "V1",
    "time": {
      "start_sec": 633.2,
      "end_sec": 641.2,
      "start_hms": "00:10:33.200",
      "end_hms": "00:10:41.200"
    },
    "original_text": "工具注明\"黑色柄刮刀/勺状工具（身份见 O05 修正）\"",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  }
]
```

#### GX010021-T2-002-F12

中性核验问题：这组原话何时结束、何时实际公开，各建议何时生效能否独立确定？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "annotations",
    "record_id": "R39",
    "source_ref": "../../annotations.json#/texts/38",
    "source_index": 38,
    "text": "Use a parchment paper to line the baking tray.",
    "text_type": "Instruction-Clarification",
    "time": {
      "start_sec": 538.698,
      "end_sec": 538.698,
      "start_hms": "00:08:58.698",
      "end_hms": "00:08:58.698"
    },
    "evidence_ids": [
      "T-R39"
    ],
    "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
  },
  {
    "artifact": "annotations",
    "record_id": "R40",
    "source_ref": "../../annotations.json#/texts/39",
    "source_index": 39,
    "text": "I don't have a parchment paper.",
    "text_type": "User-Comment",
    "time": {
      "start_sec": 544.398,
      "end_sec": 544.398,
      "start_hms": "00:09:04.398",
      "end_hms": "00:09:04.398"
    },
    "evidence_ids": [
      "T-R40"
    ],
    "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
  },
  {
    "artifact": "annotations",
    "record_id": "R41",
    "source_ref": "../../annotations.json#/texts/40",
    "source_index": 40,
    "text": "You can then use some of the leftover butter from the melt to line up the tray.",
    "text_type": "Instruction-Clarification",
    "time": {
      "start_sec": 546.378,
      "end_sec": 546.378,
      "start_hms": "00:09:06.378",
      "end_hms": "00:09:06.378"
    },
    "evidence_ids": [
      "T-R41"
    ],
    "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
  },
  {
    "artifact": "annotations",
    "record_id": "R42",
    "source_ref": "../../annotations.json#/texts/41",
    "source_index": 41,
    "text": "I don't have any leftover butter, should I use oil instead?",
    "text_type": "User-Question",
    "time": {
      "start_sec": 552.478,
      "end_sec": 552.478,
      "start_hms": "00:09:12.478",
      "end_hms": "00:09:12.478"
    },
    "evidence_ids": [
      "T-R42"
    ],
    "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
  },
  {
    "artifact": "annotations",
    "record_id": "R43",
    "source_ref": "../../annotations.json#/texts/42",
    "source_index": 42,
    "text": "Yes, you can use oil.",
    "text_type": "Instruction-Clarification",
    "time": {
      "start_sec": 556.368,
      "end_sec": 556.368,
      "start_hms": "00:09:16.368",
      "end_hms": "00:09:16.368"
    },
    "evidence_ids": [
      "T-R43"
    ],
    "use": "NORMATIVE_OR_DIALOGUE_CANDIDATE; NOT_PROOF_OF_EXECUTED_ACTION"
  },
  {
    "artifact": "events",
    "event_id": "E049",
    "source_ref": "events.json#/events/48/facts/1",
    "field": "inner_wall_oil_film",
    "value": null,
    "status": "UNCERTAIN",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02",
      "I-E049-01",
      "T-R43",
      "T-R45"
    ],
    "reason": "模底见油、倾斜旋转不证明内壁油膜或覆盖程度；R45评价不升级事实。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O12",
    "state_id": "O12.S02",
    "source_ref": "objects.json#/objects/11/state_history/1",
    "event_id": "E049",
    "time": {
      "start_sec": 560,
      "end_sec": 581,
      "start_hms": "00:09:20.000",
      "end_hms": "00:09:41.000"
    },
    "kind": "transition",
    "field": "inner_wall_oil_film",
    "before": null,
    "after": null,
    "status": "UNCERTAIN",
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02",
      "I-E049-01",
      "T-R43",
      "T-R45"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "T-R39",
    "kind": "ego_mc_text",
    "source": {
      "path": "source/annotations.json",
      "section": "texts[38]"
    },
    "description": "原始Ego-MC线索，非视觉事实。",
    "grade": "TEXT",
    "time": {
      "start_sec": 538.698,
      "end_sec": 538.698,
      "start_hms": "00:08:58.698",
      "end_hms": "00:08:58.698"
    },
    "original_text": "Use a parchment paper to line the baking tray."
  },
  {
    "id": "T-R40",
    "kind": "ego_mc_text",
    "source": {
      "path": "source/annotations.json",
      "section": "texts[39]"
    },
    "description": "原始Ego-MC线索，非视觉事实。",
    "grade": "TEXT",
    "time": {
      "start_sec": 544.398,
      "end_sec": 544.398,
      "start_hms": "00:09:04.398",
      "end_hms": "00:09:04.398"
    },
    "original_text": "I don't have a parchment paper."
  },
  {
    "id": "T-R41",
    "kind": "ego_mc_text",
    "source": {
      "path": "source/annotations.json",
      "section": "texts[40]"
    },
    "description": "原始Ego-MC线索，非视觉事实。",
    "grade": "TEXT",
    "time": {
      "start_sec": 546.378,
      "end_sec": 546.378,
      "start_hms": "00:09:06.378",
      "end_hms": "00:09:06.378"
    },
    "original_text": "You can then use some of the leftover butter from the melt to line up the tray."
  },
  {
    "id": "T-R42",
    "kind": "ego_mc_text",
    "source": {
      "path": "source/annotations.json",
      "section": "texts[41]"
    },
    "description": "原始Ego-MC线索，非视觉事实。",
    "grade": "TEXT",
    "time": {
      "start_sec": 552.478,
      "end_sec": 552.478,
      "start_hms": "00:09:12.478",
      "end_hms": "00:09:12.478"
    },
    "original_text": "I don't have any leftover butter, should I use oil instead?"
  },
  {
    "id": "T-R43",
    "kind": "ego_mc_text",
    "source": {
      "path": "source/annotations.json",
      "section": "texts[42]"
    },
    "description": "原始Ego-MC线索，非视觉事实。",
    "grade": "TEXT",
    "time": {
      "start_sec": 556.368,
      "end_sec": 556.368,
      "start_hms": "00:09:16.368",
      "end_hms": "00:09:16.368"
    },
    "original_text": "Yes, you can use oil."
  }
]
```

### GX010021-T2-003

原候选答案（未核验）：
```json
{
  "milk_path": [
    "O06",
    "O05（组内具体杯未确认）",
    "O01"
  ],
  "flour_paths": [
    [
      "O08",
      "O05（组内具体杯未确认）",
      "O01"
    ],
    [
      "O08",
      "O01"
    ]
  ],
  "downstream_path": [
    "O01内O15",
    "O12内O15",
    "O14中O12内O15"
  ],
  "visible_flour_addition_event_ids": [
    "E032",
    "E051"
  ],
  "visible_flour_additions": 2,
  "excluded_from_addition_count": [
    "E031：只量取到杯"
  ],
  "total_hidden_additions": "unknown",
  "actual_volumes": "unknown",
  "lineage_status": "CANDIDATE_CONTINUITY; 不声称质量守恒、全量转移或器具物理同一"
}
```

完整任务定义（内部原样快照）：
```json
{
  "task_id": "GX010021-T2-003",
  "episode_id": "GX010021",
  "track": "T2",
  "task_type": "T2.3",
  "title": "已入烤箱面糊的牛奶与两种加粉路径",
  "data_status": "CANDIDATE",
  "human_review": "NOT_REVIEWED",
  "hard_scoring_eligible": false,
  "execution_ready": false,
  "design_refs": [
    "4.2",
    "5.4",
    "6.2"
  ],
  "trigger": {
    "mode": "query_snapshot",
    "media_time": 692.3,
    "scheduling_status": "CANDIDATE_CHECKPOINT"
  },
  "observation_cutoff": 692.3,
  "reference_event_ids": [
    "E022",
    "E023",
    "E031",
    "E032",
    "E051",
    "E053",
    "E055"
  ],
  "reference_object_ids": [
    "O01",
    "O05",
    "O06",
    "O08",
    "O12",
    "O14",
    "O15"
  ],
  "reference_facts": [
    {
      "artifact": "events",
      "event_id": "E022",
      "source_ref": "events.json#/events/21/facts/0",
      "field": "core_action",
      "value": "倾倒量取（牛奶）",
      "status": "REPORTED_SUPPORTED",
      "evidence_ids": [
        "V-E022-01"
      ],
      "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
      "use": "CANDIDATE_REFERENCE_ONLY"
    },
    {
      "artifact": "events",
      "event_id": "E023",
      "source_ref": "events.json#/events/22/facts/0",
      "field": "core_action",
      "value": "倒入（牛奶）",
      "status": "REPORTED_SUPPORTED",
      "evidence_ids": [
        "V-E023-01"
      ],
      "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
      "use": "CANDIDATE_REFERENCE_ONLY"
    },
    {
      "artifact": "events",
      "event_id": "E031",
      "source_ref": "events.json#/events/30/facts/0",
      "field": "core_action",
      "value": "开袋并量取（面粉）",
      "status": "REPORTED_SUPPORTED",
      "evidence_ids": [
        "V-E031-01"
      ],
      "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
      "use": "CANDIDATE_REFERENCE_ONLY"
    },
    {
      "artifact": "events",
      "event_id": "E032",
      "source_ref": "events.json#/events/31/facts/0",
      "field": "core_action",
      "value": "倒入（面粉）",
      "status": "REPORTED_SUPPORTED",
      "evidence_ids": [
        "V-E032-01"
      ],
      "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
      "use": "CANDIDATE_REFERENCE_ONLY"
    },
    {
      "artifact": "events",
      "event_id": "E051",
      "source_ref": "events.json#/events/50/facts/0",
      "field": "core_action",
      "value": "直接补加面粉",
      "status": "REPORTED_SUPPORTED",
      "evidence_ids": [
        "V-E051-01",
        "V-E051-02"
      ],
      "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
      "use": "CANDIDATE_REFERENCE_ONLY"
    },
    {
      "artifact": "objects",
      "object_id": "O15",
      "state_id": "O15.S11",
      "source_ref": "objects.json#/objects/14/state_history/10",
      "event_id": "E053",
      "time": {
        "start_sec": 633,
        "end_sec": 679,
        "start_hms": "00:10:33.000",
        "end_hms": "00:11:19.000"
      },
      "kind": "transition",
      "field": "mixture_state",
      "before": null,
      "after": "转入烤模",
      "status": "REPORTED_SUPPORTED",
      "evidence_ids": [
        "V-E053-01",
        "V-E053-02"
      ],
      "use": "CANDIDATE_REFERENCE_ONLY"
    },
    {
      "artifact": "objects",
      "object_id": "O15",
      "state_id": "O15.S12",
      "source_ref": "objects.json#/objects/14/state_history/11",
      "event_id": "E055",
      "time": {
        "start_sec": 687,
        "end_sec": 692,
        "start_hms": "00:11:27.000",
        "end_hms": "00:11:32.000"
      },
      "kind": "transition",
      "field": "mixture_state",
      "before": null,
      "after": "随烤模入烤箱",
      "status": "REPORTED_SUPPORTED",
      "evidence_ids": [
        "V-E055-01"
      ],
      "use": "CANDIDATE_REFERENCE_ONLY"
    }
  ],
  "evidence_refs": [
    {
      "evidence_id": "V-E022-01",
      "registry_ref": "events.json#/evidence/28",
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 51,
        "section": "B"
      },
      "time": {
        "start_sec": 153.2,
        "end_sec": 156.2,
        "start_hms": "00:02:33.200",
        "end_hms": "00:02:36.200"
      },
      "kind": "reported_visual_observation",
      "grade": "V1",
      "description": "牛奶盒倒奶入杯，一次可见量取",
      "role": "牛奶盒→量杯",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 153.2,
          "end_sec": 156.2,
          "start_hms": "00:02:33.200",
          "end_hms": "00:02:36.200"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    },
    {
      "evidence_id": "V-E023-01",
      "registry_ref": "events.json#/evidence/29",
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 52,
        "section": "B"
      },
      "time": {
        "start_sec": 159.2,
        "end_sec": 161.2,
        "start_hms": "00:02:39.200",
        "end_hms": "00:02:41.200"
      },
      "kind": "reported_visual_observation",
      "grade": "V1",
      "description": "杯中奶倾入容器，台面见白色液滴",
      "role": "量杯→混合容器",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 159.2,
          "end_sec": 161.2,
          "start_hms": "00:02:39.200",
          "end_hms": "00:02:41.200"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    },
    {
      "evidence_id": "V-E031-01",
      "registry_ref": "events.json#/evidence/41",
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 60,
        "section": "B"
      },
      "time": {
        "start_sec": 270.2,
        "end_sec": 281.2,
        "start_hms": "00:04:30.200",
        "end_hms": "00:04:41.200"
      },
      "kind": "reported_visual_observation",
      "grade": "V1",
      "description": "开袋并向杯倒粉",
      "role": "面粉袋→量杯",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 270.2,
          "end_sec": 281.2,
          "start_hms": "00:04:30.200",
          "end_hms": "00:04:41.200"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    },
    {
      "evidence_id": "V-E032-01",
      "registry_ref": "events.json#/evidence/42",
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 61,
        "section": "B"
      },
      "time": {
        "start_sec": 287.2,
        "end_sec": 291.2,
        "start_hms": "00:04:47.200",
        "end_hms": "00:04:51.200"
      },
      "kind": "reported_visual_observation",
      "grade": "V1",
      "description": "量杯倒粉入混合容器，出现白色粉堆",
      "role": "量杯→混合容器",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 287.2,
          "end_sec": 291.2,
          "start_hms": "00:04:47.200",
          "end_hms": "00:04:51.200"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    },
    {
      "evidence_id": "V-E051-01",
      "registry_ref": "events.json#/evidence/67",
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 80,
        "section": "B"
      },
      "time": {
        "start_sec": 595.2,
        "end_sec": 602.2,
        "start_hms": "00:09:55.200",
        "end_hms": "00:10:02.200"
      },
      "kind": "reported_visual_observation",
      "grade": "V1",
      "description": "袋直接向混合容器倒粉",
      "role": "面粉袋→同一混合容器的补粉",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 595.2,
          "end_sec": 602.2,
          "start_hms": "00:09:55.200",
          "end_hms": "00:10:02.200"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    },
    {
      "evidence_id": "V-E053-01",
      "registry_ref": "events.json#/evidence/71",
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 82,
        "section": "B"
      },
      "time": {
        "start_sec": 633.2,
        "end_sec": 641.2,
        "start_hms": "00:10:33.200",
        "end_hms": "00:10:41.200"
      },
      "kind": "reported_visual_observation",
      "grade": "V1",
      "description": "混合容器面糊倾入烤模",
      "role": "混合容器面糊→烤模",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 633.2,
          "end_sec": 641.2,
          "start_hms": "00:10:33.200",
          "end_hms": "00:10:41.200"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    },
    {
      "evidence_id": "V-E055-01",
      "registry_ref": "events.json#/evidence/75",
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 84,
        "section": "B"
      },
      "time": {
        "start_sec": 687.2,
        "end_sec": 691.2,
        "start_hms": "00:11:27.200",
        "end_hms": "00:11:31.200"
      },
      "kind": "reported_visual_observation",
      "grade": "V1",
      "description": "开烤箱门、放模入架、关门",
      "role": "同一盛糊烤模→烤箱",
      "media_ref": {
        "path": "../../source/GX010021.MP4",
        "time": {
          "start_sec": 687.2,
          "end_sec": 691.2,
          "start_hms": "00:11:27.200",
          "end_hms": "00:11:31.200"
        }
      },
      "availability_time": null,
      "human_review": "NOT_REVIEWED"
    }
  ],
  "normative_rules": [],
  "candidate_answer": {
    "milk_path": [
      "O06",
      "O05（组内具体杯未确认）",
      "O01"
    ],
    "flour_paths": [
      [
        "O08",
        "O05（组内具体杯未确认）",
        "O01"
      ],
      [
        "O08",
        "O01"
      ]
    ],
    "downstream_path": [
      "O01内O15",
      "O12内O15",
      "O14中O12内O15"
    ],
    "visible_flour_addition_event_ids": [
      "E032",
      "E051"
    ],
    "visible_flour_additions": 2,
    "excluded_from_addition_count": [
      "E031：只量取到杯"
    ],
    "total_hidden_additions": "unknown",
    "actual_volumes": "unknown",
    "lineage_status": "CANDIDATE_CONTINUITY; 不声称质量守恒、全量转移或器具物理同一"
  },
  "gold_answer": null,
  "scorable_conditions": [
    "独立确认牛奶、面粉、混合容器、烤模的连续链后，分别评分两段加奶路径、两种供粉路径与下游去向。",
    "至少需盒→杯→容器、袋→杯→容器、袋→容器与容器→烤模→烤箱等非冗余证据；不能仅回答次数2。",
    "仅计两处已报告可见入混合容器事件；E031不能算第三次，不能排除隐藏加入。",
    "不评分实际杯数/半杯或一杯体积，不强行给O05组内单杯身份。"
  ],
  "pending_verification": [
    "复核153.2–161.2s、270.2–291.2s、595.2–602.2s、633.2–641.2s、687.2–691.2s对象连续性。",
    "间隙内是否换容器、替换面糊或有额外加入，需独立核验；完整连续性尚非Gold。",
    "做必要证据片段删除、Current-only/No-video审核，确认路径不能由当前烤模/常识直接恢复。"
  ],
  "existing_review_queue_ids": [
    "RQ05",
    "RQ06",
    "RQ12"
  ],
  "evidence_quality": {
    "status": "NOT_INDEPENDENTLY_VERIFIED",
    "directly_observed_in_this_round": false,
    "visual_source": "ARCHIVED_AI_REPORTS_ONLY",
    "numeric_confidence": null,
    "annotation_disagreements": "继承字段不确定性与历史修订；未做人类一致性测量。"
  },
  "visibility_regime": "G1",
  "causal_constraints": {
    "max_media_time": 692.3,
    "require_availability_time_check": true,
    "evaluator_reference_visible_to_agent": false,
    "event_id_link_is_not_full_record_access": true,
    "unknown_requires_observability_adjudication": true
  },
  "protocol_tbd": [
    "输入窗口/采样与实际availability_time",
    "运行预算/超时",
    "最终输出Schema/证据匹配阈值",
    "近期窗口长度/B0成本控制",
    "Evidence Score容差/无关片段惩罚/最小集裁决"
  ],
  "earliest_answerable_time": {
    "start_sec": 687.2,
    "end_sec": 692.0,
    "start_hms": "00:11:27.200",
    "end_hms": "00:11:32.000"
  },
  "earliest_answerable_time_status": "CANDIDATE_ENVELOPE_NOT_VERIFIED_FIRST_TIME",
  "question": "烤模中的面糊刚被放入烤箱。请用此前分散操作证据说明：这份面糊中的牛奶经哪些容器进入混合物，面粉有哪些不同的入料路径，这些入料与现在烤模内的面糊如何相连？请区分向量杯量取与真正向混合容器加入，并说明哪些数量或身份仍不能确定。",
  "answer_type": {
    "fields": [
      "milk_path",
      "flour_paths",
      "downstream_path",
      "visible_flour_addition_event_ids",
      "unknowns",
      "evidence_refs"
    ],
    "allow_unknown": true
  },
  "required_evidence_sets": [
    [
      {
        "evidence_id": "V-E022-01",
        "registry_ref": "events.json#/evidence/28",
        "source": {
          "path": "annotation_reports/verification_report.md",
          "line": 51,
          "section": "B"
        },
        "time": {
          "start_sec": 153.2,
          "end_sec": 156.2,
          "start_hms": "00:02:33.200",
          "end_hms": "00:02:36.200"
        },
        "kind": "reported_visual_observation",
        "grade": "V1",
        "description": "牛奶盒倒奶入杯，一次可见量取",
        "role": "牛奶盒→量杯",
        "media_ref": {
          "path": "../../source/GX010021.MP4",
          "time": {
            "start_sec": 153.2,
            "end_sec": 156.2,
            "start_hms": "00:02:33.200",
            "end_hms": "00:02:36.200"
          }
        },
        "availability_time": null,
        "human_review": "NOT_REVIEWED"
      },
      {
        "evidence_id": "V-E023-01",
        "registry_ref": "events.json#/evidence/29",
        "source": {
          "path": "annotation_reports/verification_report.md",
          "line": 52,
          "section": "B"
        },
        "time": {
          "start_sec": 159.2,
          "end_sec": 161.2,
          "start_hms": "00:02:39.200",
          "end_hms": "00:02:41.200"
        },
        "kind": "reported_visual_observation",
        "grade": "V1",
        "description": "杯中奶倾入容器，台面见白色液滴",
        "role": "量杯→混合容器",
        "media_ref": {
          "path": "../../source/GX010021.MP4",
          "time": {
            "start_sec": 159.2,
            "end_sec": 161.2,
            "start_hms": "00:02:39.200",
            "end_hms": "00:02:41.200"
          }
        },
        "availability_time": null,
        "human_review": "NOT_REVIEWED"
      },
      {
        "evidence_id": "V-E031-01",
        "registry_ref": "events.json#/evidence/41",
        "source": {
          "path": "annotation_reports/verification_report.md",
          "line": 60,
          "section": "B"
        },
        "time": {
          "start_sec": 270.2,
          "end_sec": 281.2,
          "start_hms": "00:04:30.200",
          "end_hms": "00:04:41.200"
        },
        "kind": "reported_visual_observation",
        "grade": "V1",
        "description": "开袋并向杯倒粉",
        "role": "面粉袋→量杯",
        "media_ref": {
          "path": "../../source/GX010021.MP4",
          "time": {
            "start_sec": 270.2,
            "end_sec": 281.2,
            "start_hms": "00:04:30.200",
            "end_hms": "00:04:41.200"
          }
        },
        "availability_time": null,
        "human_review": "NOT_REVIEWED"
      },
      {
        "evidence_id": "V-E032-01",
        "registry_ref": "events.json#/evidence/42",
        "source": {
          "path": "annotation_reports/verification_report.md",
          "line": 61,
          "section": "B"
        },
        "time": {
          "start_sec": 287.2,
          "end_sec": 291.2,
          "start_hms": "00:04:47.200",
          "end_hms": "00:04:51.200"
        },
        "kind": "reported_visual_observation",
        "grade": "V1",
        "description": "量杯倒粉入混合容器，出现白色粉堆",
        "role": "量杯→混合容器",
        "media_ref": {
          "path": "../../source/GX010021.MP4",
          "time": {
            "start_sec": 287.2,
            "end_sec": 291.2,
            "start_hms": "00:04:47.200",
            "end_hms": "00:04:51.200"
          }
        },
        "availability_time": null,
        "human_review": "NOT_REVIEWED"
      },
      {
        "evidence_id": "V-E051-01",
        "registry_ref": "events.json#/evidence/67",
        "source": {
          "path": "annotation_reports/verification_report.md",
          "line": 80,
          "section": "B"
        },
        "time": {
          "start_sec": 595.2,
          "end_sec": 602.2,
          "start_hms": "00:09:55.200",
          "end_hms": "00:10:02.200"
        },
        "kind": "reported_visual_observation",
        "grade": "V1",
        "description": "袋直接向混合容器倒粉",
        "role": "面粉袋→同一混合容器的补粉",
        "media_ref": {
          "path": "../../source/GX010021.MP4",
          "time": {
            "start_sec": 595.2,
            "end_sec": 602.2,
            "start_hms": "00:09:55.200",
            "end_hms": "00:10:02.200"
          }
        },
        "availability_time": null,
        "human_review": "NOT_REVIEWED"
      },
      {
        "evidence_id": "V-E053-01",
        "registry_ref": "events.json#/evidence/71",
        "source": {
          "path": "annotation_reports/verification_report.md",
          "line": 82,
          "section": "B"
        },
        "time": {
          "start_sec": 633.2,
          "end_sec": 641.2,
          "start_hms": "00:10:33.200",
          "end_hms": "00:10:41.200"
        },
        "kind": "reported_visual_observation",
        "grade": "V1",
        "description": "混合容器面糊倾入烤模",
        "role": "混合容器面糊→烤模",
        "media_ref": {
          "path": "../../source/GX010021.MP4",
          "time": {
            "start_sec": 633.2,
            "end_sec": 641.2,
            "start_hms": "00:10:33.200",
            "end_hms": "00:10:41.200"
          }
        },
        "availability_time": null,
        "human_review": "NOT_REVIEWED"
      },
      {
        "evidence_id": "V-E055-01",
        "registry_ref": "events.json#/evidence/75",
        "source": {
          "path": "annotation_reports/verification_report.md",
          "line": 84,
          "section": "B"
        },
        "time": {
          "start_sec": 687.2,
          "end_sec": 691.2,
          "start_hms": "00:11:27.200",
          "end_hms": "00:11:31.200"
        },
        "kind": "reported_visual_observation",
        "grade": "V1",
        "description": "开烤箱门、放模入架、关门",
        "role": "同一盛糊烤模→烤箱",
        "media_ref": {
          "path": "../../source/GX010021.MP4",
          "time": {
            "start_sec": 687.2,
            "end_sec": 691.2,
            "start_hms": "00:11:27.200",
            "end_hms": "00:11:31.200"
          }
        },
        "availability_time": null,
        "human_review": "NOT_REVIEWED"
      }
    ]
  ],
  "reasoning_relation": [
    "对象传递",
    "uses_output_of（事实来源链，非新增规范次序）",
    "非冗余入料路径整合"
  ],
  "history_necessity": {
    "status": "PENDING_RECENT_ONLY_AND_NO_VIDEO_AUDIT",
    "long_horizon_claim": "NOT_ESTABLISHED",
    "recall_only": false,
    "nonredundant_evidence": "不同材料的不同转移边共同连接到当前烤模；路径重建比单问次数有更多约束。",
    "shortcut_risk": "需排除当前指令或画面泄漏配料路径，以及依据通常菜谱猜测。"
  },
  "current_process_evidence_ids": [
    "V-E055-01"
  ],
  "query_time": 692.3,
  "dependency_span": 539.1,
  "dependency_span_unit": "seconds",
  "dependency_span_basis": {
    "earliest_required_evidence_start": 153.2,
    "note": "仅描述候选证据跨度，不等于通过长程必要性门禁。"
  },
  "required_evidence_sets_status": "PROPOSED_MINIMAL_SUFFICIENT; 独立审核与片段删除实验前不声明已最小充分",
  "probe_isolation": {
    "required": true,
    "write_back_to_main_agent": false,
    "method": "冻结t_q主执行状态，复制到只读分支，回答后丢弃分支；主状态继续",
    "fallback": "预先声明并验证等价隔离策略及额外成本",
    "verified": false
  },
  "agent_facing_input": {
    "interface": "query_snapshot(query, at_media_time, isolated=true)",
    "expose_only_at_query_time": [
      "question",
      "answer_type"
    ],
    "private_fields": "其余均为Evaluator私有，不作为Agent输入",
    "answer_evidence_refs": "Agent引用已公开observation/指令；私有V-/T-证据ID仅由Evaluator映射"
  }
}
```

#### GX010021-T2-003-F01

中性核验问题：152–157秒期间，盒内物质被转移到哪个容器？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E022",
    "source_ref": "events.json#/events/21/facts/0",
    "field": "core_action",
    "value": "倾倒量取（牛奶）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E022-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E022-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 51,
      "section": "B"
    },
    "description": "牛奶盒倒奶入杯，一次可见量取",
    "grade": "V1",
    "time": {
      "start_sec": 153.2,
      "end_sec": 156.2,
      "start_hms": "00:02:33.200",
      "end_hms": "00:02:36.200"
    },
    "original_text": "无需修改"
  }
]
```

#### GX010021-T2-003-F02

中性核验问题：158–165秒期间，杯内物质被转移到哪个容器？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E023",
    "source_ref": "events.json#/events/22/facts/0",
    "field": "core_action",
    "value": "倒入（牛奶）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E023-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E023-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 52,
      "section": "B"
    },
    "description": "杯中奶倾入容器，台面见白色液滴",
    "grade": "V1",
    "time": {
      "start_sec": 159.2,
      "end_sec": 161.2,
      "start_hms": "00:02:39.200",
      "end_hms": "00:02:41.200"
    },
    "original_text": "无需修改"
  }
]
```

#### GX010021-T2-003-F03

中性核验问题：上述量取与倒入动作使用的杯能否在两动作之间连续关联？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E022",
    "source_ref": "events.json#/events/21/facts/0",
    "field": "core_action",
    "value": "倾倒量取（牛奶）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E022-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "events",
    "event_id": "E023",
    "source_ref": "events.json#/events/22/facts/0",
    "field": "core_action",
    "value": "倒入（牛奶）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E023-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E022-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 51,
      "section": "B"
    },
    "description": "牛奶盒倒奶入杯，一次可见量取",
    "grade": "V1",
    "time": {
      "start_sec": 153.2,
      "end_sec": 156.2,
      "start_hms": "00:02:33.200",
      "end_hms": "00:02:36.200"
    },
    "original_text": "无需修改"
  },
  {
    "id": "V-E023-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 52,
      "section": "B"
    },
    "description": "杯中奶倾入容器，台面见白色液滴",
    "grade": "V1",
    "time": {
      "start_sec": 159.2,
      "end_sec": 161.2,
      "start_hms": "00:02:39.200",
      "end_hms": "00:02:41.200"
    },
    "original_text": "无需修改"
  }
]
```

#### GX010021-T2-003-F04

中性核验问题：269–282秒期间，袋中物质被转移到哪个容器？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E031",
    "source_ref": "events.json#/events/30/facts/0",
    "field": "core_action",
    "value": "开袋并量取（面粉）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E031-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E031-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 60,
      "section": "B"
    },
    "description": "开袋并向杯倒粉",
    "grade": "V1",
    "time": {
      "start_sec": 270.2,
      "end_sec": 281.2,
      "start_hms": "00:04:30.200",
      "end_hms": "00:04:41.200"
    },
    "original_text": "无需修改"
  }
]
```

#### GX010021-T2-003-F05

中性核验问题：283–292秒期间，杯内物质被转移到哪个容器？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E032",
    "source_ref": "events.json#/events/31/facts/0",
    "field": "core_action",
    "value": "倒入（面粉）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E032-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E032-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 61,
      "section": "B"
    },
    "description": "量杯倒粉入混合容器，出现白色粉堆",
    "grade": "V1",
    "time": {
      "start_sec": 287.2,
      "end_sec": 291.2,
      "start_hms": "00:04:47.200",
      "end_hms": "00:04:51.200"
    },
    "original_text": "无需修改"
  }
]
```

#### GX010021-T2-003-F06

中性核验问题：上述袋中量取与其后倒入动作使用的杯能否连续关联？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E031",
    "source_ref": "events.json#/events/30/facts/0",
    "field": "core_action",
    "value": "开袋并量取（面粉）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E031-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "events",
    "event_id": "E032",
    "source_ref": "events.json#/events/31/facts/0",
    "field": "core_action",
    "value": "倒入（面粉）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E032-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E031-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 60,
      "section": "B"
    },
    "description": "开袋并向杯倒粉",
    "grade": "V1",
    "time": {
      "start_sec": 270.2,
      "end_sec": 281.2,
      "start_hms": "00:04:30.200",
      "end_hms": "00:04:41.200"
    },
    "original_text": "无需修改"
  },
  {
    "id": "V-E032-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 61,
      "section": "B"
    },
    "description": "量杯倒粉入混合容器，出现白色粉堆",
    "grade": "V1",
    "time": {
      "start_sec": 287.2,
      "end_sec": 291.2,
      "start_hms": "00:04:47.200",
      "end_hms": "00:04:51.200"
    },
    "original_text": "无需修改"
  }
]
```

#### GX010021-T2-003-F07

中性核验问题：595–604秒期间，袋中物质通过什么路径到达什么容器？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E051",
    "source_ref": "events.json#/events/50/facts/0",
    "field": "core_action",
    "value": "直接补加面粉",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E051-01",
      "V-E051-02"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E051-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 80,
      "section": "B"
    },
    "description": "袋直接向混合容器倒粉",
    "grade": "V1",
    "time": {
      "start_sec": 595.2,
      "end_sec": 602.2,
      "start_hms": "00:09:55.200",
      "end_hms": "00:10:02.200"
    },
    "original_text": "开始由 9:52 修至约 9:55",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  },
  {
    "id": "V-E051-02",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 80,
      "section": "B"
    },
    "description": "表面新增白粉堆",
    "grade": "V1",
    "time": {
      "start_sec": 603.2,
      "end_sec": 603.2,
      "start_hms": "00:10:03.200",
      "end_hms": "00:10:03.200"
    },
    "original_text": "开始由 9:52 修至约 9:55",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  }
]
```

#### GX010021-T2-003-F08

中性核验问题：早段供粉袋与595–604秒出现的供料袋之间能否连续关联？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E031",
    "source_ref": "events.json#/events/30/facts/0",
    "field": "core_action",
    "value": "开袋并量取（面粉）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E031-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "events",
    "event_id": "E051",
    "source_ref": "events.json#/events/50/facts/0",
    "field": "core_action",
    "value": "直接补加面粉",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E051-01",
      "V-E051-02"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E031-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 60,
      "section": "B"
    },
    "description": "开袋并向杯倒粉",
    "grade": "V1",
    "time": {
      "start_sec": 270.2,
      "end_sec": 281.2,
      "start_hms": "00:04:30.200",
      "end_hms": "00:04:41.200"
    },
    "original_text": "无需修改"
  },
  {
    "id": "V-E051-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 80,
      "section": "B"
    },
    "description": "袋直接向混合容器倒粉",
    "grade": "V1",
    "time": {
      "start_sec": 595.2,
      "end_sec": 602.2,
      "start_hms": "00:09:55.200",
      "end_hms": "00:10:02.200"
    },
    "original_text": "开始由 9:52 修至约 9:55",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  }
]
```

#### GX010021-T2-003-F09

中性核验问题：各入料与后段倒出动作涉及的混合容器能否连续关联？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E023",
    "source_ref": "events.json#/events/22/facts/0",
    "field": "core_action",
    "value": "倒入（牛奶）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E023-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "events",
    "event_id": "E032",
    "source_ref": "events.json#/events/31/facts/0",
    "field": "core_action",
    "value": "倒入（面粉）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E032-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "events",
    "event_id": "E051",
    "source_ref": "events.json#/events/50/facts/0",
    "field": "core_action",
    "value": "直接补加面粉",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E051-01",
      "V-E051-02"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O15",
    "state_id": "O15.S11",
    "source_ref": "objects.json#/objects/14/state_history/10",
    "event_id": "E053",
    "time": {
      "start_sec": 633,
      "end_sec": 679,
      "start_hms": "00:10:33.000",
      "end_hms": "00:11:19.000"
    },
    "kind": "transition",
    "field": "mixture_state",
    "before": null,
    "after": "转入烤模",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E053-01",
      "V-E053-02"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E023-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 52,
      "section": "B"
    },
    "description": "杯中奶倾入容器，台面见白色液滴",
    "grade": "V1",
    "time": {
      "start_sec": 159.2,
      "end_sec": 161.2,
      "start_hms": "00:02:39.200",
      "end_hms": "00:02:41.200"
    },
    "original_text": "无需修改"
  },
  {
    "id": "V-E032-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 61,
      "section": "B"
    },
    "description": "量杯倒粉入混合容器，出现白色粉堆",
    "grade": "V1",
    "time": {
      "start_sec": 287.2,
      "end_sec": 291.2,
      "start_hms": "00:04:47.200",
      "end_hms": "00:04:51.200"
    },
    "original_text": "无需修改"
  },
  {
    "id": "V-E051-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 80,
      "section": "B"
    },
    "description": "袋直接向混合容器倒粉",
    "grade": "V1",
    "time": {
      "start_sec": 595.2,
      "end_sec": 602.2,
      "start_hms": "00:09:55.200",
      "end_hms": "00:10:02.200"
    },
    "original_text": "开始由 9:52 修至约 9:55",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  },
  {
    "id": "V-E053-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 82,
      "section": "B"
    },
    "description": "混合容器面糊倾入烤模",
    "grade": "V1",
    "time": {
      "start_sec": 633.2,
      "end_sec": 641.2,
      "start_hms": "00:10:33.200",
      "end_hms": "00:10:41.200"
    },
    "original_text": "工具注明\"黑色柄刮刀/勺状工具（身份见 O05 修正）\"",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  }
]
```

#### GX010021-T2-003-F10

中性核验问题：161.2–291.2秒期间，容器内材料的延续或替换情况能否确定？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E023",
    "source_ref": "events.json#/events/22/facts/0",
    "field": "core_action",
    "value": "倒入（牛奶）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E023-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "events",
    "event_id": "E032",
    "source_ref": "events.json#/events/31/facts/0",
    "field": "core_action",
    "value": "倒入（面粉）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E032-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E023-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 52,
      "section": "B"
    },
    "description": "杯中奶倾入容器，台面见白色液滴",
    "grade": "V1",
    "time": {
      "start_sec": 159.2,
      "end_sec": 161.2,
      "start_hms": "00:02:39.200",
      "end_hms": "00:02:41.200"
    },
    "original_text": "无需修改"
  },
  {
    "id": "V-E027-02",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 56,
      "section": "B"
    },
    "description": "搅拌、混合液渐均匀",
    "grade": "V1",
    "time": {
      "start_sec": 200.2,
      "end_sec": 234.2,
      "start_hms": "00:03:20.200",
      "end_hms": "00:03:54.200"
    },
    "original_text": "结束时间由 3:54 修至约 3:55；开始由 3:20 修至约 3:19"
  },
  {
    "id": "V-E032-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 61,
      "section": "B"
    },
    "description": "量杯倒粉入混合容器，出现白色粉堆",
    "grade": "V1",
    "time": {
      "start_sec": 287.2,
      "end_sec": 291.2,
      "start_hms": "00:04:47.200",
      "end_hms": "00:04:51.200"
    },
    "original_text": "无需修改"
  }
]
```

#### GX010021-T2-003-F11

中性核验问题：291.2–602.2秒期间，容器内材料的延续或替换情况能否确定？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E032",
    "source_ref": "events.json#/events/31/facts/0",
    "field": "core_action",
    "value": "倒入（面粉）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E032-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "events",
    "event_id": "E051",
    "source_ref": "events.json#/events/50/facts/0",
    "field": "core_action",
    "value": "直接补加面粉",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E051-01",
      "V-E051-02"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E032-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 61,
      "section": "B"
    },
    "description": "量杯倒粉入混合容器，出现白色粉堆",
    "grade": "V1",
    "time": {
      "start_sec": 287.2,
      "end_sec": 291.2,
      "start_hms": "00:04:47.200",
      "end_hms": "00:04:51.200"
    },
    "original_text": "无需修改"
  },
  {
    "id": "V-E051-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 80,
      "section": "B"
    },
    "description": "袋直接向混合容器倒粉",
    "grade": "V1",
    "time": {
      "start_sec": 595.2,
      "end_sec": 602.2,
      "start_hms": "00:09:55.200",
      "end_hms": "00:10:02.200"
    },
    "original_text": "开始由 9:52 修至约 9:55",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  }
]
```

#### GX010021-T2-003-F12

中性核验问题：602.2–633.2秒期间，容器内材料与倒出时材料能否连续关联？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E051",
    "source_ref": "events.json#/events/50/facts/0",
    "field": "core_action",
    "value": "直接补加面粉",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E051-01",
      "V-E051-02"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O15",
    "state_id": "O15.S11",
    "source_ref": "objects.json#/objects/14/state_history/10",
    "event_id": "E053",
    "time": {
      "start_sec": 633,
      "end_sec": 679,
      "start_hms": "00:10:33.000",
      "end_hms": "00:11:19.000"
    },
    "kind": "transition",
    "field": "mixture_state",
    "before": null,
    "after": "转入烤模",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E053-01",
      "V-E053-02"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E051-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 80,
      "section": "B"
    },
    "description": "袋直接向混合容器倒粉",
    "grade": "V1",
    "time": {
      "start_sec": 595.2,
      "end_sec": 602.2,
      "start_hms": "00:09:55.200",
      "end_hms": "00:10:02.200"
    },
    "original_text": "开始由 9:52 修至约 9:55",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  },
  {
    "id": "V-E053-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 82,
      "section": "B"
    },
    "description": "混合容器面糊倾入烤模",
    "grade": "V1",
    "time": {
      "start_sec": 633.2,
      "end_sec": 641.2,
      "start_hms": "00:10:33.200",
      "end_hms": "00:10:41.200"
    },
    "original_text": "工具注明\"黑色柄刮刀/勺状工具（身份见 O05 修正）\"",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  }
]
```

#### GX010021-T2-003-F13

中性核验问题：633–679秒期间，材料实际转移到什么容器？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "objects",
    "object_id": "O15",
    "state_id": "O15.S11",
    "source_ref": "objects.json#/objects/14/state_history/10",
    "event_id": "E053",
    "time": {
      "start_sec": 633,
      "end_sec": 679,
      "start_hms": "00:10:33.000",
      "end_hms": "00:11:19.000"
    },
    "kind": "transition",
    "field": "mixture_state",
    "before": null,
    "after": "转入烤模",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E053-01",
      "V-E053-02"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E053-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 82,
      "section": "B"
    },
    "description": "混合容器面糊倾入烤模",
    "grade": "V1",
    "time": {
      "start_sec": 633.2,
      "end_sec": 641.2,
      "start_hms": "00:10:33.200",
      "end_hms": "00:10:41.200"
    },
    "original_text": "工具注明\"黑色柄刮刀/勺状工具（身份见 O05 修正）\"",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  },
  {
    "id": "V-E053-02",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 82,
      "section": "B"
    },
    "description": "黑色工具刮容器壁",
    "grade": "V1",
    "time": {
      "start_sec": 645.2,
      "end_sec": 677.2,
      "start_hms": "00:10:45.200",
      "end_hms": "00:11:17.200"
    },
    "original_text": "工具注明\"黑色柄刮刀/勺状工具（身份见 O05 修正）\"",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  }
]
```

#### GX010021-T2-003-F14

中性核验问题：接收材料的烤模与687–692.3秒出现的烤模能否连续关联？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "objects",
    "object_id": "O15",
    "state_id": "O15.S11",
    "source_ref": "objects.json#/objects/14/state_history/10",
    "event_id": "E053",
    "time": {
      "start_sec": 633,
      "end_sec": 679,
      "start_hms": "00:10:33.000",
      "end_hms": "00:11:19.000"
    },
    "kind": "transition",
    "field": "mixture_state",
    "before": null,
    "after": "转入烤模",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E053-01",
      "V-E053-02"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "objects",
    "object_id": "O15",
    "state_id": "O15.S12",
    "source_ref": "objects.json#/objects/14/state_history/11",
    "event_id": "E055",
    "time": {
      "start_sec": 687,
      "end_sec": 692,
      "start_hms": "00:11:27.000",
      "end_hms": "00:11:32.000"
    },
    "kind": "transition",
    "field": "mixture_state",
    "before": null,
    "after": "随烤模入烤箱",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E055-01"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E053-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 82,
      "section": "B"
    },
    "description": "混合容器面糊倾入烤模",
    "grade": "V1",
    "time": {
      "start_sec": 633.2,
      "end_sec": 641.2,
      "start_hms": "00:10:33.200",
      "end_hms": "00:10:41.200"
    },
    "original_text": "工具注明\"黑色柄刮刀/勺状工具（身份见 O05 修正）\"",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  },
  {
    "id": "V-E053-02",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 82,
      "section": "B"
    },
    "description": "黑色工具刮容器壁",
    "grade": "V1",
    "time": {
      "start_sec": 645.2,
      "end_sec": 677.2,
      "start_hms": "00:10:45.200",
      "end_hms": "00:11:17.200"
    },
    "original_text": "工具注明\"黑色柄刮刀/勺状工具（身份见 O05 修正）\"",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  },
  {
    "id": "V-E055-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 84,
      "section": "B"
    },
    "description": "开烤箱门、放模入架、关门",
    "grade": "V1",
    "time": {
      "start_sec": 687.2,
      "end_sec": 691.2,
      "start_hms": "00:11:27.200",
      "end_hms": "00:11:31.200"
    },
    "original_text": "开始由 11:26 修至 11:27"
  }
]
```

#### GX010021-T2-003-F15

中性核验问题：截至692.3秒，烤模及其中材料被移到什么位置？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "objects",
    "object_id": "O15",
    "state_id": "O15.S12",
    "source_ref": "objects.json#/objects/14/state_history/11",
    "event_id": "E055",
    "time": {
      "start_sec": 687,
      "end_sec": 692,
      "start_hms": "00:11:27.000",
      "end_hms": "00:11:32.000"
    },
    "kind": "transition",
    "field": "mixture_state",
    "before": null,
    "after": "随烤模入烤箱",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E055-01"
    ],
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E055-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 84,
      "section": "B"
    },
    "description": "开烤箱门、放模入架、关门",
    "grade": "V1",
    "time": {
      "start_sec": 687.2,
      "end_sec": 691.2,
      "start_hms": "00:11:27.200",
      "end_hms": "00:11:31.200"
    },
    "original_text": "开始由 11:26 修至 11:27"
  }
]
```

#### GX010021-T2-003-F16

中性核验问题：在已提供历史中，有多少独立、直接可见的粉状材料入混合容器动作？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E031",
    "source_ref": "events.json#/events/30/facts/0",
    "field": "core_action",
    "value": "开袋并量取（面粉）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E031-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "events",
    "event_id": "E032",
    "source_ref": "events.json#/events/31/facts/0",
    "field": "core_action",
    "value": "倒入（面粉）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E032-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "events",
    "event_id": "E051",
    "source_ref": "events.json#/events/50/facts/0",
    "field": "core_action",
    "value": "直接补加面粉",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E051-01",
      "V-E051-02"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E031-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 60,
      "section": "B"
    },
    "description": "开袋并向杯倒粉",
    "grade": "V1",
    "time": {
      "start_sec": 270.2,
      "end_sec": 281.2,
      "start_hms": "00:04:30.200",
      "end_hms": "00:04:41.200"
    },
    "original_text": "无需修改"
  },
  {
    "id": "V-E032-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 61,
      "section": "B"
    },
    "description": "量杯倒粉入混合容器，出现白色粉堆",
    "grade": "V1",
    "time": {
      "start_sec": 287.2,
      "end_sec": 291.2,
      "start_hms": "00:04:47.200",
      "end_hms": "00:04:51.200"
    },
    "original_text": "无需修改"
  },
  {
    "id": "V-E051-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 80,
      "section": "B"
    },
    "description": "袋直接向混合容器倒粉",
    "grade": "V1",
    "time": {
      "start_sec": 595.2,
      "end_sec": 602.2,
      "start_hms": "00:09:55.200",
      "end_hms": "00:10:02.200"
    },
    "original_text": "开始由 9:52 修至约 9:55",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  },
  {
    "id": "V-E051-02",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 80,
      "section": "B"
    },
    "description": "表面新增白粉堆",
    "grade": "V1",
    "time": {
      "start_sec": 603.2,
      "end_sec": 603.2,
      "start_hms": "00:10:03.200",
      "end_hms": "00:10:03.200"
    },
    "original_text": "开始由 9:52 修至约 9:55",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  }
]
```

#### GX010021-T2-003-F17

中性核验问题：是否存在无法排除额外加入或材料替换的遮挡/出画区间？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E032",
    "source_ref": "events.json#/events/31/facts/0",
    "field": "core_action",
    "value": "倒入（面粉）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E032-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "events",
    "event_id": "E051",
    "source_ref": "events.json#/events/50/facts/0",
    "field": "core_action",
    "value": "直接补加面粉",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E051-01",
      "V-E051-02"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E032-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 61,
      "section": "B"
    },
    "description": "量杯倒粉入混合容器，出现白色粉堆",
    "grade": "V1",
    "time": {
      "start_sec": 287.2,
      "end_sec": 291.2,
      "start_hms": "00:04:47.200",
      "end_hms": "00:04:51.200"
    },
    "original_text": "无需修改"
  },
  {
    "id": "V-E051-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 80,
      "section": "B"
    },
    "description": "袋直接向混合容器倒粉",
    "grade": "V1",
    "time": {
      "start_sec": 595.2,
      "end_sec": 602.2,
      "start_hms": "00:09:55.200",
      "end_hms": "00:10:02.200"
    },
    "original_text": "开始由 9:52 修至约 9:55",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  }
]
```

#### GX010021-T2-003-F18

中性核验问题：奶操作所用杯与早先查看标签的杯能否独立确认为同一只？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E022",
    "source_ref": "events.json#/events/21/facts/0",
    "field": "core_action",
    "value": "倾倒量取（牛奶）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E022-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "events",
    "event_id": "E023",
    "source_ref": "events.json#/events/22/facts/0",
    "field": "core_action",
    "value": "倒入（牛奶）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E023-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E020-02",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 49,
      "section": "B"
    },
    "description": "杯柄标签 \"1/4 CUP\"",
    "grade": "V1",
    "time": {
      "start_sec": 144.2,
      "end_sec": 144.2,
      "start_hms": "00:02:24.200",
      "end_hms": "00:02:24.200"
    },
    "original_text": "改为\"手持黑色量杯（1/4 cup）查看；是否为第二只量杯 UNCERTAIN\""
  },
  {
    "id": "V-E022-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 51,
      "section": "B"
    },
    "description": "牛奶盒倒奶入杯，一次可见量取",
    "grade": "V1",
    "time": {
      "start_sec": 153.2,
      "end_sec": 156.2,
      "start_hms": "00:02:33.200",
      "end_hms": "00:02:36.200"
    },
    "original_text": "无需修改"
  },
  {
    "id": "V-E023-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 52,
      "section": "B"
    },
    "description": "杯中奶倾入容器，台面见白色液滴",
    "grade": "V1",
    "time": {
      "start_sec": 159.2,
      "end_sec": 161.2,
      "start_hms": "00:02:39.200",
      "end_hms": "00:02:41.200"
    },
    "original_text": "无需修改"
  }
]
```

#### GX010021-T2-003-F19

中性核验问题：实际加入的奶量能否由杯规格和操作过程直接读证？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E022",
    "source_ref": "events.json#/events/21/facts/0",
    "field": "core_action",
    "value": "倾倒量取（牛奶）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E022-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "events",
    "event_id": "E023",
    "source_ref": "events.json#/events/22/facts/0",
    "field": "core_action",
    "value": "倒入（牛奶）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E023-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E020-02",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 49,
      "section": "B"
    },
    "description": "杯柄标签 \"1/4 CUP\"",
    "grade": "V1",
    "time": {
      "start_sec": 144.2,
      "end_sec": 144.2,
      "start_hms": "00:02:24.200",
      "end_hms": "00:02:24.200"
    },
    "original_text": "改为\"手持黑色量杯（1/4 cup）查看；是否为第二只量杯 UNCERTAIN\""
  },
  {
    "id": "V-E022-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 51,
      "section": "B"
    },
    "description": "牛奶盒倒奶入杯，一次可见量取",
    "grade": "V1",
    "time": {
      "start_sec": 153.2,
      "end_sec": 156.2,
      "start_hms": "00:02:33.200",
      "end_hms": "00:02:36.200"
    },
    "original_text": "无需修改"
  },
  {
    "id": "V-E023-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 52,
      "section": "B"
    },
    "description": "杯中奶倾入容器，台面见白色液滴",
    "grade": "V1",
    "time": {
      "start_sec": 159.2,
      "end_sec": 161.2,
      "start_hms": "00:02:39.200",
      "end_hms": "00:02:41.200"
    },
    "original_text": "无需修改"
  }
]
```

#### GX010021-T2-003-F20

中性核验问题：粉操作所用杯的具体物理身份能否由此前历史独立确定？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E031",
    "source_ref": "events.json#/events/30/facts/0",
    "field": "core_action",
    "value": "开袋并量取（面粉）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E031-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "events",
    "event_id": "E032",
    "source_ref": "events.json#/events/31/facts/0",
    "field": "core_action",
    "value": "倒入（面粉）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E032-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E020-02",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 49,
      "section": "B"
    },
    "description": "杯柄标签 \"1/4 CUP\"",
    "grade": "V1",
    "time": {
      "start_sec": 144.2,
      "end_sec": 144.2,
      "start_hms": "00:02:24.200",
      "end_hms": "00:02:24.200"
    },
    "original_text": "改为\"手持黑色量杯（1/4 cup）查看；是否为第二只量杯 UNCERTAIN\""
  },
  {
    "id": "V-E031-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 60,
      "section": "B"
    },
    "description": "开袋并向杯倒粉",
    "grade": "V1",
    "time": {
      "start_sec": 270.2,
      "end_sec": 281.2,
      "start_hms": "00:04:30.200",
      "end_hms": "00:04:41.200"
    },
    "original_text": "无需修改"
  },
  {
    "id": "V-E032-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 61,
      "section": "B"
    },
    "description": "量杯倒粉入混合容器，出现白色粉堆",
    "grade": "V1",
    "time": {
      "start_sec": 287.2,
      "end_sec": 291.2,
      "start_hms": "00:04:47.200",
      "end_hms": "00:04:51.200"
    },
    "original_text": "无需修改"
  }
]
```

#### GX010021-T2-003-F21

中性核验问题：首段实际加入的粉量能否由杯规格和操作过程直接读证？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E031",
    "source_ref": "events.json#/events/30/facts/0",
    "field": "core_action",
    "value": "开袋并量取（面粉）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E031-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  },
  {
    "artifact": "events",
    "event_id": "E032",
    "source_ref": "events.json#/events/31/facts/0",
    "field": "core_action",
    "value": "倒入（面粉）",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E032-01"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E031-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 60,
      "section": "B"
    },
    "description": "开袋并向杯倒粉",
    "grade": "V1",
    "time": {
      "start_sec": 270.2,
      "end_sec": 281.2,
      "start_hms": "00:04:30.200",
      "end_hms": "00:04:41.200"
    },
    "original_text": "无需修改"
  },
  {
    "id": "V-E032-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 61,
      "section": "B"
    },
    "description": "量杯倒粉入混合容器，出现白色粉堆",
    "grade": "V1",
    "time": {
      "start_sec": 287.2,
      "end_sec": 291.2,
      "start_hms": "00:04:47.200",
      "end_hms": "00:04:51.200"
    },
    "original_text": "无需修改"
  }
]
```

#### GX010021-T2-003-F22

中性核验问题：后段实际加入的粉量能否由合法观察直接确定？

关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：
```json
[
  {
    "artifact": "events",
    "event_id": "E051",
    "source_ref": "events.json#/events/50/facts/0",
    "field": "core_action",
    "value": "直接补加面粉",
    "status": "REPORTED_SUPPORTED",
    "evidence_ids": [
      "V-E051-01",
      "V-E051-02"
    ],
    "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。",
    "use": "CANDIDATE_REFERENCE_ONLY"
  }
]
```

来源证据（历史V-/I-/T-分类不升级）：
```json
[
  {
    "id": "V-E051-01",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 80,
      "section": "B"
    },
    "description": "袋直接向混合容器倒粉",
    "grade": "V1",
    "time": {
      "start_sec": 595.2,
      "end_sec": 602.2,
      "start_hms": "00:09:55.200",
      "end_hms": "00:10:02.200"
    },
    "original_text": "开始由 9:52 修至约 9:55",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  },
  {
    "id": "V-E051-02",
    "kind": "reported_visual_observation",
    "source": {
      "path": "annotation_reports/verification_report.md",
      "line": 80,
      "section": "B"
    },
    "description": "表面新增白粉堆",
    "grade": "V1",
    "time": {
      "start_sec": 603.2,
      "end_sec": 603.2,
      "start_hms": "00:10:03.200",
      "end_hms": "00:10:03.200"
    },
    "original_text": "开始由 9:52 修至约 9:55",
    "normalization_source": {
      "path": "annotation_reports/consistency_revision.md",
      "section": "1"
    }
  }
]
```

## 相关结构化记录和历史来源完整保留

### events

```json
[
  {
    "id": "E022",
    "time": {
      "start_sec": 152.0,
      "end_sec": 157.0,
      "start_hms": "00:02:32.000",
      "end_hms": "00:02:37.000"
    },
    "time_status": "APPROXIMATE",
    "action": "倾倒量取（牛奶）",
    "actor": "右手持盒",
    "description": "向量杯倒白色牛奶至满",
    "object_ids": [
      "O06",
      "O05"
    ],
    "original_candidate": {
      "id": "E022",
      "start_time": "00:02:32",
      "end_time": "00:02:37",
      "action": "倾倒量取（牛奶）",
      "actor": "右手持盒",
      "target": "牛奶盒→黑色量杯",
      "description": "向量杯倒白色牛奶至满",
      "state_change": "量杯由空变为满牛奶",
      "certainty": "高",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 48,
        "section": "B"
      },
      "raw_row": "| E022 | 00:02:32 | 00:02:37 | 倾倒量取（牛奶） | 右手持盒 | 牛奶盒→黑色量杯 | 向量杯倒白色牛奶至满 | 量杯由空变为满牛奶 | 高 |"
    },
    "verification": {
      "original_claim_status": "SUPPORTED",
      "current_claim_status": "REPORTED_SUPPORTED",
      "human_status": "NOT_REVIEWED",
      "report_row": {
        "id": "E022",
        "verdict": "SUPPORTED",
        "time_accuracy": "是（152–157s）",
        "action_accuracy": "是",
        "state_accuracy": "是（量杯满牛奶）",
        "evidence": "153.2–156.2s 倒奶入杯",
        "recommendation": "无需修改"
      },
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 51,
        "section": "B"
      },
      "raw_row": "| E022 | SUPPORTED | 是（152–157s） | 是 | 是（量杯满牛奶） | 153.2–156.2s 倒奶入杯 | 无需修改 |"
    },
    "facts": [
      {
        "field": "core_action",
        "value": "倾倒量取（牛奶）",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E022-01"
        ],
        "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。"
      },
      {
        "field": "milk_volume_cup",
        "value": null,
        "status": "UNCERTAIN",
        "evidence_ids": [
          "V-E022-01",
          "T-R18",
          "T-R19"
        ],
        "reason": "R18半杯指令与早先1/4 CUP标签不能确认实际使用杯及量值；半杯来自Ego-MC。"
      },
      {
        "field": "visible_milk_measurements",
        "value": 1,
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E022-01"
        ],
        "reason": "报告只见一次盒到杯的量取；非全帧排除其他动作。"
      }
    ],
    "state_change_ids": [
      "O05.S06",
      "O06.S02"
    ],
    "evidence_ids": [
      "V-E022-01",
      "T-R18",
      "T-R19"
    ],
    "ego_mc_record_ids": [
      "R18",
      "R19"
    ],
    "revisions": []
  },
  {
    "id": "E023",
    "time": {
      "start_sec": 158.0,
      "end_sec": 165.0,
      "start_hms": "00:02:38.000",
      "end_hms": "00:02:45.000"
    },
    "time_status": "APPROXIMATE",
    "action": "倒入（牛奶）",
    "actor": "左手",
    "description": "牛奶倒入容器（少量洒落于台面可见白色液滴）",
    "object_ids": [
      "O05",
      "O01",
      "O15"
    ],
    "original_candidate": {
      "id": "E023",
      "start_time": "00:02:38",
      "end_time": "00:02:45",
      "action": "倒入（牛奶）",
      "actor": "左手",
      "target": "满牛奶量杯→塑料容器",
      "description": "牛奶倒入容器（少量洒落于台面可见白色液滴）",
      "state_change": "容器内新增牛奶；量杯空",
      "certainty": "高",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 49,
        "section": "B"
      },
      "raw_row": "| E023 | 00:02:38 | 00:02:45 | 倒入（牛奶） | 左手 | 满牛奶量杯→塑料容器 | 牛奶倒入容器（少量洒落于台面可见白色液滴） | 容器内新增牛奶；量杯空 | 高 |"
    },
    "verification": {
      "original_claim_status": "SUPPORTED",
      "current_claim_status": "REPORTED_SUPPORTED",
      "human_status": "NOT_REVIEWED",
      "report_row": {
        "id": "E023",
        "verdict": "SUPPORTED",
        "time_accuracy": "是（158–165s）",
        "action_accuracy": "是",
        "state_accuracy": "是（容器加牛奶；台面见白色洒液）",
        "evidence": "159.2–161.2s 倾倒、161.2s 起台面白色液滴",
        "recommendation": "无需修改"
      },
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 52,
        "section": "B"
      },
      "raw_row": "| E023 | SUPPORTED | 是（158–165s） | 是 | 是（容器加牛奶；台面见白色洒液） | 159.2–161.2s 倾倒、161.2s 起台面白色液滴 | 无需修改 |"
    },
    "facts": [
      {
        "field": "core_action",
        "value": "倒入（牛奶）",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E023-01"
        ],
        "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。"
      },
      {
        "field": "milk_volume_cup",
        "value": null,
        "status": "UNCERTAIN",
        "evidence_ids": [
          "V-E023-01",
          "T-R18",
          "T-R19"
        ],
        "reason": "R18半杯指令与早先1/4 CUP标签不能确认实际使用杯及量值；半杯来自Ego-MC。"
      },
      {
        "field": "visible_milk_additions",
        "value": 1,
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E023-01"
        ],
        "reason": "报告只见一次杯到混合容器倾倒。"
      }
    ],
    "state_change_ids": [
      "O01.S05",
      "O05.S07",
      "O15.S04"
    ],
    "evidence_ids": [
      "V-E023-01",
      "T-R18",
      "T-R19"
    ],
    "ego_mc_record_ids": [
      "R18",
      "R19"
    ],
    "revisions": []
  },
  {
    "id": "E027",
    "time": {
      "start_sec": 199,
      "end_sec": 235,
      "start_hms": "00:03:19.000",
      "end_hms": "00:03:55.000"
    },
    "time_status": "APPROXIMATE",
    "action": "电动搅拌（第 1 次）",
    "actor": "右手持打蛋器",
    "description": "搅拌棒进入混合液，第一次电动搅拌；蛋、糖、奶由分层渐变为淡黄均匀液，随后提离。",
    "object_ids": [
      "O07",
      "O01",
      "O15"
    ],
    "original_candidate": {
      "id": "E027",
      "start_time": "00:03:20",
      "end_time": "00:03:54",
      "action": "电动搅拌（第 1 次）",
      "actor": "右手持打蛋器",
      "target": "塑料容器内蛋+糖+奶",
      "description": "搅拌棒插入液面开机搅拌，左手扶容器；混合物由分层（蛋黄/糖/奶）渐变为淡黄均匀液",
      "state_change": "混合物状态：分层→均匀淡黄液",
      "certainty": "高",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 53,
        "section": "B"
      },
      "raw_row": "| E027 | 00:03:20 | 00:03:54 | 电动搅拌（第 1 次） | 右手持打蛋器 | 塑料容器内蛋+糖+奶 | 搅拌棒插入液面开机搅拌，左手扶容器；混合物由分层（蛋黄/糖/奶）渐变为淡黄均匀液 | 混合物状态：分层→均匀淡黄液 | 高 |"
    },
    "verification": {
      "original_claim_status": "SUPPORTED",
      "current_claim_status": "REPORTED_SUPPORTED",
      "human_status": "NOT_REVIEWED",
      "report_row": {
        "id": "E027",
        "verdict": "SUPPORTED（边界修正）",
        "time_accuracy": "**否：建议 00:03:19–00:03:55**",
        "action_accuracy": "是",
        "state_accuracy": "是（分层→淡黄均匀液）",
        "evidence": "199.2s 棒入液、200–234s 搅拌、235.2s 提离",
        "recommendation": "结束时间由 3:54 修至约 3:55；开始由 3:20 修至约 3:19"
      },
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 56,
        "section": "B"
      },
      "raw_row": "| E027 | SUPPORTED（边界修正） | **否：建议 00:03:19–00:03:55** | 是 | 是（分层→淡黄均匀液） | 199.2s 棒入液、200–234s 搅拌、235.2s 提离 | 结束时间由 3:54 修至约 3:55；开始由 3:20 修至约 3:19 |"
    },
    "facts": [
      {
        "field": "core_action",
        "value": "电动搅拌（第 1 次）",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E027-01",
          "V-E027-02",
          "V-E027-03"
        ],
        "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。"
      }
    ],
    "state_change_ids": [
      "O01.S06",
      "O07.S02",
      "O15.S05"
    ],
    "evidence_ids": [
      "V-E027-01",
      "V-E027-02",
      "V-E027-03",
      "T-R18",
      "T-R22",
      "T-R23",
      "T-R24",
      "T-R25"
    ],
    "ego_mc_record_ids": [
      "R18",
      "R22",
      "R23",
      "R24",
      "R25"
    ],
    "revisions": [
      {
        "field": "time",
        "before": {
          "start_sec": 200.0,
          "end_sec": 234.0,
          "start_hms": "00:03:20.000",
          "end_hms": "00:03:54.000"
        },
        "after": {
          "start_sec": 199,
          "end_sec": 235,
          "start_hms": "00:03:19.000",
          "end_hms": "00:03:55.000"
        },
        "reason": "依据报告明确边界修正；仍为近似边界。",
        "source": {
          "path": "annotation_reports/verification_report.md",
          "line": 56,
          "section": "B"
        }
      },
      {
        "field": "description/action",
        "before": "搅拌棒插入液面开机搅拌，左手扶容器；混合物由分层（蛋黄/糖/奶）渐变为淡黄均匀液",
        "after": "搅拌棒进入混合液，第一次电动搅拌；蛋、糖、奶由分层渐变为淡黄均匀液，随后提离。",
        "reason": "应用后轮修订，去除过度断言并分离观察、推断、文本用途。",
        "source": {
          "path": "annotation_reports/verification_report.md",
          "line": 56,
          "section": "B"
        }
      }
    ]
  },
  {
    "id": "E028",
    "time": {
      "start_sec": 234.0,
      "end_sec": 239.0,
      "start_hms": "00:03:54.000",
      "end_hms": "00:03:59.000"
    },
    "time_status": "APPROXIMATE",
    "action": "停机放置",
    "actor": "双手",
    "description": "提离容器，将打蛋器放左侧台面",
    "object_ids": [
      "O07"
    ],
    "original_candidate": {
      "id": "E028",
      "start_time": "00:03:54",
      "end_time": "00:03:59",
      "action": "停机放置",
      "actor": "双手",
      "target": "打蛋器",
      "description": "提离容器，将打蛋器放左侧台面",
      "state_change": "打蛋器离容器",
      "certainty": "高",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 54,
        "section": "B"
      },
      "raw_row": "| E028 | 00:03:54 | 00:03:59 | 停机放置 | 双手 | 打蛋器 | 提离容器，将打蛋器放左侧台面 | 打蛋器离容器 | 高 |"
    },
    "verification": {
      "original_claim_status": "SUPPORTED",
      "current_claim_status": "REPORTED_SUPPORTED",
      "human_status": "NOT_REVIEWED",
      "report_row": {
        "id": "E028",
        "verdict": "SUPPORTED",
        "time_accuracy": "是（235–239s）",
        "action_accuracy": "是",
        "state_accuracy": "是",
        "evidence": "236.2–238.2s 打蛋器放左台面",
        "recommendation": "无需修改"
      },
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 57,
        "section": "B"
      },
      "raw_row": "| E028 | SUPPORTED | 是（235–239s） | 是 | 是 | 236.2–238.2s 打蛋器放左台面 | 无需修改 |"
    },
    "facts": [
      {
        "field": "core_action",
        "value": "停机放置",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E028-01"
        ],
        "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。"
      }
    ],
    "state_change_ids": [
      "O07.S05"
    ],
    "evidence_ids": [
      "V-E028-01",
      "T-R25"
    ],
    "ego_mc_record_ids": [
      "R25"
    ],
    "revisions": []
  },
  {
    "id": "E031",
    "time": {
      "start_sec": 269.0,
      "end_sec": 282.0,
      "start_hms": "00:04:29.000",
      "end_hms": "00:04:42.000"
    },
    "time_status": "APPROXIMATE",
    "action": "开袋并量取（面粉）",
    "actor": "双手",
    "description": "撑开袋口，向量杯倒白色面粉至满",
    "object_ids": [
      "O08",
      "O05"
    ],
    "original_candidate": {
      "id": "E031",
      "start_time": "00:04:29",
      "end_time": "00:04:42",
      "action": "开袋并量取（面粉）",
      "actor": "双手",
      "target": "面粉袋→黑色量杯",
      "description": "撑开袋口，向量杯倒白色面粉至满",
      "state_change": "量杯满面粉",
      "certainty": "高",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 57,
        "section": "B"
      },
      "raw_row": "| E031 | 00:04:29 | 00:04:42 | 开袋并量取（面粉） | 双手 | 面粉袋→黑色量杯 | 撑开袋口，向量杯倒白色面粉至满 | 量杯满面粉 | 高 |"
    },
    "verification": {
      "original_claim_status": "SUPPORTED",
      "current_claim_status": "REPORTED_SUPPORTED",
      "human_status": "NOT_REVIEWED",
      "report_row": {
        "id": "E031",
        "verdict": "SUPPORTED",
        "time_accuracy": "是（269–282s）",
        "action_accuracy": "是",
        "state_accuracy": "是（量杯满面粉）",
        "evidence": "270.2s 撑袋口、273.2–281.2s 倒粉入杯",
        "recommendation": "无需修改"
      },
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 60,
        "section": "B"
      },
      "raw_row": "| E031 | SUPPORTED | 是（269–282s） | 是 | 是（量杯满面粉） | 270.2s 撑袋口、273.2–281.2s 倒粉入杯 | 无需修改 |"
    },
    "facts": [
      {
        "field": "core_action",
        "value": "开袋并量取（面粉）",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E031-01"
        ],
        "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。"
      },
      {
        "field": "flour_volume_cup",
        "value": null,
        "status": "UNCERTAIN",
        "evidence_ids": [
          "V-E031-01",
          "T-R26"
        ],
        "reason": "R26一杯指令非测量；实际杯规格未读证，一杯来自Ego-MC。"
      }
    ],
    "state_change_ids": [
      "O05.S09",
      "O08.S02"
    ],
    "evidence_ids": [
      "V-E031-01",
      "T-R26"
    ],
    "ego_mc_record_ids": [
      "R26"
    ],
    "revisions": []
  },
  {
    "id": "E032",
    "time": {
      "start_sec": 283.0,
      "end_sec": 292.0,
      "start_hms": "00:04:43.000",
      "end_hms": "00:04:52.000"
    },
    "time_status": "APPROXIMATE",
    "action": "倒入（面粉）",
    "actor": "左手/右手",
    "description": "面粉倾倒在容器内淡黄液面上成白色粉堆；量杯放右侧",
    "object_ids": [
      "O05",
      "O01",
      "O15"
    ],
    "original_candidate": {
      "id": "E032",
      "start_time": "00:04:43",
      "end_time": "00:04:52",
      "action": "倒入（面粉）",
      "actor": "左手/右手",
      "target": "满面粉量杯→塑料容器",
      "description": "面粉倾倒在容器内淡黄液面上成白色粉堆；量杯放右侧",
      "state_change": "容器内新增面粉层",
      "certainty": "高",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 58,
        "section": "B"
      },
      "raw_row": "| E032 | 00:04:43 | 00:04:52 | 倒入（面粉） | 左手/右手 | 满面粉量杯→塑料容器 | 面粉倾倒在容器内淡黄液面上成白色粉堆；量杯放右侧 | 容器内新增面粉层 | 高 |"
    },
    "verification": {
      "original_claim_status": "SUPPORTED",
      "current_claim_status": "REPORTED_SUPPORTED",
      "human_status": "NOT_REVIEWED",
      "report_row": {
        "id": "E032",
        "verdict": "SUPPORTED",
        "time_accuracy": "是（283–292s）",
        "action_accuracy": "是",
        "state_accuracy": "是（液面加白色粉堆）",
        "evidence": "287.2–291.2s 倾倒、291.2s 粉堆",
        "recommendation": "无需修改"
      },
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 61,
        "section": "B"
      },
      "raw_row": "| E032 | SUPPORTED | 是（283–292s） | 是 | 是（液面加白色粉堆） | 287.2–291.2s 倾倒、291.2s 粉堆 | 无需修改 |"
    },
    "facts": [
      {
        "field": "core_action",
        "value": "倒入（面粉）",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E032-01"
        ],
        "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。"
      },
      {
        "field": "flour_volume_cup",
        "value": null,
        "status": "UNCERTAIN",
        "evidence_ids": [
          "V-E032-01",
          "T-R26"
        ],
        "reason": "R26一杯指令非测量；实际杯规格未读证，一杯来自Ego-MC。"
      },
      {
        "field": "flour_addition_to_mixing_container",
        "value": 1,
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E032-01"
        ],
        "reason": "第一处可见粉入容器；E031仅上游量取。"
      }
    ],
    "state_change_ids": [
      "O01.S07",
      "O05.S10",
      "O15.S06"
    ],
    "evidence_ids": [
      "V-E032-01",
      "T-R26",
      "T-R27"
    ],
    "ego_mc_record_ids": [
      "R26",
      "R27"
    ],
    "revisions": []
  },
  {
    "id": "E049",
    "time": {
      "start_sec": 560,
      "end_sec": 581,
      "start_hms": "00:09:20.000",
      "end_hms": "00:09:41.000"
    },
    "time_status": "APPROXIMATE",
    "action": "倒油并倾斜旋转烤模",
    "actor": "双手",
    "description": "向烤模模底倒少量油，再持模倾斜旋转；内壁油膜是否形成与覆盖范围未确证。",
    "object_ids": [
      "O13",
      "O12"
    ],
    "original_candidate": {
      "id": "E049",
      "start_time": "00:09:26",
      "end_time": "00:09:41",
      "action": "倒油并涂布烤模",
      "actor": "双手",
      "target": "油瓶→面包烤模",
      "description": "向烤模内倒少量油，随后双手持模倾斜旋转，使油接触内壁各面",
      "state_change": "烤模内壁沾油",
      "certainty": "中（涂布方式依据倾斜旋转推断）",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 75,
        "section": "B"
      },
      "raw_row": "| E049 | 00:09:26 | 00:09:41 | 倒油并涂布烤模 | 双手 | 油瓶→面包烤模 | 向烤模内倒少量油，随后双手持模倾斜旋转，使油接触内壁各面 | 烤模内壁沾油 | 中（涂布方式依据倾斜旋转推断） |"
    },
    "verification": {
      "original_claim_status": "UNCERTAIN",
      "current_claim_status": "UNCERTAIN",
      "human_status": "NOT_REVIEWED",
      "report_row": {
        "id": "E049",
        "verdict": "**UNCERTAIN**",
        "time_accuracy": "是（926–941s）",
        "action_accuracy": "倒油可见；\"涂布内壁\"为推断",
        "state_accuracy": "\"内壁沾油\"不可见证",
        "evidence": "920.2–922.2s 瓶口向烤模倾倒（可见油流/油滴入模底）；927.2–939.2s 双手持模倾斜旋转；内壁油膜分布不可分辨",
        "recommendation": "改为\"向烤模倒入少量油并倾斜旋转烤模（意图使油分布内壁；是否形成内壁油膜 UNCERTAIN）\""
      },
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 78,
        "section": "B"
      },
      "raw_row": "| E049 | **UNCERTAIN** | 是（926–941s） | 倒油可见；\"涂布内壁\"为推断 | \"内壁沾油\"不可见证 | 920.2–922.2s 瓶口向烤模倾倒（可见油流/油滴入模底）；927.2–939.2s 双手持模倾斜旋转；内壁油膜分布不可分辨 | 改为\"向烤模倒入少量油并倾斜旋转烤模（意图使油分布内壁；是否形成内壁油膜 UNCERTAIN）\" |"
    },
    "facts": [
      {
        "field": "core_action",
        "value": "倒油并倾斜旋转烤模",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E049-01",
          "V-E049-02"
        ],
        "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。"
      },
      {
        "field": "inner_wall_oil_film",
        "value": null,
        "status": "UNCERTAIN",
        "evidence_ids": [
          "V-E049-01",
          "V-E049-02",
          "I-E049-01",
          "T-R43",
          "T-R45"
        ],
        "reason": "模底见油、倾斜旋转不证明内壁油膜或覆盖程度；R45评价不升级事实。"
      }
    ],
    "state_change_ids": [
      "O12.S01",
      "O12.S02",
      "O13.S02"
    ],
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02",
      "T-R37",
      "T-R39",
      "T-R41",
      "T-R43",
      "T-R44",
      "T-R45",
      "I-E049-01"
    ],
    "ego_mc_record_ids": [
      "R37",
      "R39",
      "R41",
      "R43",
      "R44",
      "R45"
    ],
    "revisions": [
      {
        "field": "time",
        "before": {
          "start_sec": 566.0,
          "end_sec": 581.0,
          "start_hms": "00:09:26.000",
          "end_hms": "00:09:41.000"
        },
        "after": {
          "start_sec": 560,
          "end_sec": 581,
          "start_hms": "00:09:20.000",
          "end_hms": "00:09:41.000"
        },
        "reason": "依据报告明确边界修正；仍为近似边界。",
        "source": {
          "path": "annotation_reports/crosscheck_report.md",
          "section": "E.4"
        }
      },
      {
        "field": "description/action",
        "before": "向烤模内倒少量油，随后双手持模倾斜旋转，使油接触内壁各面",
        "after": "向烤模模底倒少量油，再持模倾斜旋转；内壁油膜是否形成与覆盖范围未确证。",
        "reason": "应用后轮修订，去除过度断言并分离观察、推断、文本用途。",
        "source": {
          "path": "annotation_reports/crosscheck_report.md",
          "section": "E"
        }
      },
      {
        "field": "evidence.time",
        "before": "改为\"向烤模倒入少量油并倾斜旋转烤模（意图使油分布内壁；是否形成内壁油膜 UNCERTAIN）\"",
        "after": [
          {
            "start_sec": 560.2,
            "end_sec": 562.2,
            "start_hms": "00:09:20.200",
            "end_hms": "00:09:22.200"
          },
          {
            "start_sec": 567.2,
            "end_sec": 579.2,
            "start_hms": "00:09:27.200",
            "end_hms": "00:09:39.200"
          }
        ],
        "reason": "逐项采用第三轮映射，修正去冒号秒数与内容错配；不是按>696.2阈值机械转换。",
        "source": {
          "path": "annotation_reports/consistency_revision.md",
          "section": "1"
        }
      }
    ]
  },
  {
    "id": "E051",
    "time": {
      "start_sec": 595,
      "end_sec": 604,
      "start_hms": "00:09:55.000",
      "end_hms": "00:10:04.000"
    },
    "time_status": "APPROXIMATE",
    "action": "直接补加面粉",
    "actor": "双手",
    "description": "拿起面粉袋直接向容器面糊表面倾倒少量白色面粉",
    "object_ids": [
      "O08",
      "O01",
      "O15"
    ],
    "original_candidate": {
      "id": "E051",
      "start_time": "00:09:52",
      "end_time": "00:10:04",
      "action": "直接补加面粉",
      "actor": "双手",
      "target": "面粉袋→塑料容器",
      "description": "拿起面粉袋直接向容器面糊表面倾倒少量白色面粉",
      "state_change": "面糊表面新增面粉",
      "certainty": "高",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 77,
        "section": "B"
      },
      "raw_row": "| E051 | 00:09:52 | 00:10:04 | 直接补加面粉 | 双手 | 面粉袋→塑料容器 | 拿起面粉袋直接向容器面糊表面倾倒少量白色面粉 | 面糊表面新增面粉 | 高 |"
    },
    "verification": {
      "original_claim_status": "SUPPORTED",
      "current_claim_status": "REPORTED_SUPPORTED",
      "human_status": "NOT_REVIEWED",
      "report_row": {
        "id": "E051",
        "verdict": "SUPPORTED（边界修正）",
        "time_accuracy": "**否：建议 00:09:55–00:10:04**",
        "action_accuracy": "是（袋直接倒粉入容器）",
        "state_accuracy": "是（面糊表面加白粉）",
        "evidence": "995.2–1002.2s 持面粉袋向容器倾倒、1003.2s 表面白粉堆",
        "recommendation": "开始由 9:52 修至约 9:55"
      },
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 80,
        "section": "B"
      },
      "raw_row": "| E051 | SUPPORTED（边界修正） | **否：建议 00:09:55–00:10:04** | 是（袋直接倒粉入容器） | 是（面糊表面加白粉） | 995.2–1002.2s 持面粉袋向容器倾倒、1003.2s 表面白粉堆 | 开始由 9:52 修至约 9:55 |"
    },
    "facts": [
      {
        "field": "core_action",
        "value": "直接补加面粉",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E051-01",
          "V-E051-02"
        ],
        "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。"
      },
      {
        "field": "flour_addition_to_mixing_container",
        "value": 2,
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E051-01",
          "V-E051-02"
        ],
        "reason": "第二处可见粉入容器；仅计E032/E051。"
      },
      {
        "field": "additional_hidden_flour_addition",
        "value": null,
        "status": "UNCERTAIN",
        "evidence_ids": [
          "V-E051-01",
          "V-E051-02",
          "I-E051-02"
        ],
        "reason": "1fps不能排除遮挡动作，无证据不补造第三次。"
      },
      {
        "field": "supplement_intent",
        "value": "操作者自述仍要加一点面粉",
        "status": "UNCERTAIN",
        "evidence_ids": [
          "T-R49"
        ],
        "reason": "R49语句印证意图；意图字段仍非视觉事实。"
      }
    ],
    "state_change_ids": [
      "O01.S10",
      "O08.S03",
      "O15.S09"
    ],
    "evidence_ids": [
      "V-E051-01",
      "V-E051-02",
      "T-R46",
      "T-R47",
      "T-R48",
      "T-R49",
      "I-E051-02"
    ],
    "ego_mc_record_ids": [
      "R46",
      "R47",
      "R48",
      "R49"
    ],
    "revisions": [
      {
        "field": "time",
        "before": {
          "start_sec": 592.0,
          "end_sec": 604.0,
          "start_hms": "00:09:52.000",
          "end_hms": "00:10:04.000"
        },
        "after": {
          "start_sec": 595,
          "end_sec": 604,
          "start_hms": "00:09:55.000",
          "end_hms": "00:10:04.000"
        },
        "reason": "依据报告明确边界修正；仍为近似边界。",
        "source": {
          "path": "annotation_reports/verification_report.md",
          "line": 80,
          "section": "B"
        }
      },
      {
        "field": "evidence.time",
        "before": "开始由 9:52 修至约 9:55",
        "after": [
          {
            "start_sec": 595.2,
            "end_sec": 602.2,
            "start_hms": "00:09:55.200",
            "end_hms": "00:10:02.200"
          },
          {
            "start_sec": 603.2,
            "end_sec": 603.2,
            "start_hms": "00:10:03.200",
            "end_hms": "00:10:03.200"
          }
        ],
        "reason": "逐项采用第三轮映射，修正去冒号秒数与内容错配；不是按>696.2阈值机械转换。",
        "source": {
          "path": "annotation_reports/consistency_revision.md",
          "section": "1"
        }
      }
    ]
  },
  {
    "id": "E053",
    "time": {
      "start_sec": 633,
      "end_sec": 679,
      "start_hms": "00:10:33.000",
      "end_hms": "00:11:19.000"
    },
    "time_status": "APPROXIMATE",
    "action": "倒入面糊入模并刮净",
    "actor": "双手+黑色刮刀",
    "description": "面糊倾入烤模，并用黑色柄刮刀/勺状工具刮擦混合容器壁底，将残留面糊刮入模；容器近空。",
    "object_ids": [
      "O01",
      "O15",
      "O12",
      "O17"
    ],
    "original_candidate": {
      "id": "E053",
      "start_time": "00:10:32",
      "end_time": "00:11:19",
      "action": "倒入面糊入模并刮净",
      "actor": "双手+黑色刮刀",
      "target": "塑料容器面糊→面包烤模",
      "description": "将面糊倾入已抹油烤模，用黑色刮刀反复刮擦容器内壁与底部，将残留面糊刮入烤模",
      "state_change": "面糊转移至烤模；塑料容器近空",
      "certainty": "高",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 79,
        "section": "B"
      },
      "raw_row": "| E053 | 00:10:32 | 00:11:19 | 倒入面糊入模并刮净 | 双手+黑色刮刀 | 塑料容器面糊→面包烤模 | 将面糊倾入已抹油烤模，用黑色刮刀反复刮擦容器内壁与底部，将残留面糊刮入烤模 | 面糊转移至烤模；塑料容器近空 | 高 |"
    },
    "verification": {
      "original_claim_status": "SUPPORTED",
      "current_claim_status": "REPORTED_SUPPORTED",
      "human_status": "NOT_REVIEWED",
      "report_row": {
        "id": "E053",
        "verdict": "SUPPORTED（边界修正+工具注明）",
        "time_accuracy": "**否：建议 00:10:33–00:11:19**",
        "action_accuracy": "是（倒糊入模+刮净）",
        "state_accuracy": "是",
        "evidence": "1033.2–1041.2s 倾倒、1045.2–1117.2s 黑色刮刀刮容器壁",
        "recommendation": "工具注明\"黑色柄刮刀/勺状工具（身份见 O05 修正）\""
      },
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 82,
        "section": "B"
      },
      "raw_row": "| E053 | SUPPORTED（边界修正+工具注明） | **否：建议 00:10:33–00:11:19** | 是（倒糊入模+刮净） | 是 | 1033.2–1041.2s 倾倒、1045.2–1117.2s 黑色刮刀刮容器壁 | 工具注明\"黑色柄刮刀/勺状工具（身份见 O05 修正）\" |"
    },
    "facts": [
      {
        "field": "core_action",
        "value": "倒入面糊入模并刮净",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E053-01",
          "V-E053-02"
        ],
        "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。"
      },
      {
        "field": "same_tool_as_E043_or_cups",
        "value": null,
        "status": "UNCERTAIN",
        "evidence_ids": [
          "V-E053-01",
          "V-E053-02",
          "I-E053-01"
        ],
        "reason": "黑色刮糊工具与E043工具及O05杯组的物理同一性均未知。"
      }
    ],
    "state_change_ids": [
      "O01.S12",
      "O12.S03",
      "O15.S11",
      "O17.S01",
      "O17.S02"
    ],
    "evidence_ids": [
      "V-E053-01",
      "V-E053-02",
      "T-R52",
      "T-R53",
      "T-R37",
      "T-R46",
      "I-E053-01"
    ],
    "ego_mc_record_ids": [
      "R52",
      "R53",
      "R37",
      "R46"
    ],
    "revisions": [
      {
        "field": "time",
        "before": {
          "start_sec": 632.0,
          "end_sec": 679.0,
          "start_hms": "00:10:32.000",
          "end_hms": "00:11:19.000"
        },
        "after": {
          "start_sec": 633,
          "end_sec": 679,
          "start_hms": "00:10:33.000",
          "end_hms": "00:11:19.000"
        },
        "reason": "依据报告明确边界修正；仍为近似边界。",
        "source": {
          "path": "annotation_reports/verification_report.md",
          "line": 82,
          "section": "B"
        }
      },
      {
        "field": "description/action",
        "before": "将面糊倾入已抹油烤模，用黑色刮刀反复刮擦容器内壁与底部，将残留面糊刮入烤模",
        "after": "面糊倾入烤模，并用黑色柄刮刀/勺状工具刮擦混合容器壁底，将残留面糊刮入模；容器近空。",
        "reason": "应用后轮修订，去除过度断言并分离观察、推断、文本用途。",
        "source": {
          "path": "annotation_reports/verification_report.md",
          "line": 82,
          "section": "B"
        }
      },
      {
        "field": "evidence.time",
        "before": "工具注明\"黑色柄刮刀/勺状工具（身份见 O05 修正）\"",
        "after": [
          {
            "start_sec": 633.2,
            "end_sec": 641.2,
            "start_hms": "00:10:33.200",
            "end_hms": "00:10:41.200"
          },
          {
            "start_sec": 645.2,
            "end_sec": 677.2,
            "start_hms": "00:10:45.200",
            "end_hms": "00:11:17.200"
          }
        ],
        "reason": "逐项采用第三轮映射，修正去冒号秒数与内容错配；不是按>696.2阈值机械转换。",
        "source": {
          "path": "annotation_reports/consistency_revision.md",
          "section": "1"
        }
      }
    ]
  },
  {
    "id": "E055",
    "time": {
      "start_sec": 687,
      "end_sec": 692,
      "start_hms": "00:11:27.000",
      "end_hms": "00:11:32.000"
    },
    "time_status": "APPROXIMATE",
    "action": "放入烤箱",
    "actor": "左手开门/右手放",
    "description": "打开烤箱门，将盛面糊的烤模放入烤架，关门；实际温度和预热完成未确证。",
    "object_ids": [
      "O12",
      "O14",
      "O15"
    ],
    "original_candidate": {
      "id": "E055",
      "start_time": "00:11:26",
      "end_time": "00:11:32",
      "action": "放入烤箱",
      "actor": "左手开门/右手放",
      "target": "面包烤模（面糊）→烤箱",
      "description": "打开烤箱门（内部灯亮、可见烤架），将烤模放入烤架，关门",
      "state_change": "面糊入烤箱",
      "certainty": "高",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 81,
        "section": "B"
      },
      "raw_row": "| E055 | 00:11:26 | 00:11:32 | 放入烤箱 | 左手开门/右手放 | 面包烤模（面糊）→烤箱 | 打开烤箱门（内部灯亮、可见烤架），将烤模放入烤架，关门 | 面糊入烤箱 | 高 |"
    },
    "verification": {
      "original_claim_status": "SUPPORTED",
      "current_claim_status": "REPORTED_SUPPORTED",
      "human_status": "NOT_REVIEWED",
      "report_row": {
        "id": "E055",
        "verdict": "SUPPORTED（边界修正）",
        "time_accuracy": "**否：建议 00:11:27–00:11:32**",
        "action_accuracy": "是",
        "state_accuracy": "是",
        "evidence": "687.2s（=11:27）开门、689.2–690.2s 放烤模、691.2s 关门",
        "recommendation": "开始由 11:26 修至 11:27"
      },
      "source": {
        "path": "annotation_reports/verification_report.md",
        "line": 84,
        "section": "B"
      },
      "raw_row": "| E055 | SUPPORTED（边界修正） | **否：建议 00:11:27–00:11:32** | 是 | 是 | 687.2s（=11:27）开门、689.2–690.2s 放烤模、691.2s 关门 | 开始由 11:26 修至 11:27 |"
    },
    "facts": [
      {
        "field": "core_action",
        "value": "放入烤箱",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E055-01"
        ],
        "reason": "仅依据历史报告所述抽样帧的核心动作；未人工确认。"
      },
      {
        "field": "oven_preheat_complete",
        "value": null,
        "status": "UNCERTAIN",
        "evidence_ids": [
          "V-E055-01",
          "H-E055-01",
          "T-R01",
          "T-R02"
        ],
        "reason": "实际温度与预热完成无视觉证据；R01/R02仅指令/自述。"
      }
    ],
    "state_change_ids": [
      "O12.S04",
      "O14.S04",
      "O14.S05",
      "O15.S12"
    ],
    "evidence_ids": [
      "V-E055-01",
      "T-R54",
      "T-R55",
      "H-E055-01",
      "T-R01",
      "T-R02"
    ],
    "ego_mc_record_ids": [
      "R54",
      "R55",
      "R01",
      "R02"
    ],
    "revisions": [
      {
        "field": "time",
        "before": {
          "start_sec": 686.0,
          "end_sec": 692.0,
          "start_hms": "00:11:26.000",
          "end_hms": "00:11:32.000"
        },
        "after": {
          "start_sec": 687,
          "end_sec": 692,
          "start_hms": "00:11:27.000",
          "end_hms": "00:11:32.000"
        },
        "reason": "依据报告明确边界修正；仍为近似边界。",
        "source": {
          "path": "annotation_reports/verification_report.md",
          "line": 84,
          "section": "B"
        }
      },
      {
        "field": "description/action",
        "before": "打开烤箱门（内部灯亮、可见烤架），将烤模放入烤架，关门",
        "after": "打开烤箱门，将盛面糊的烤模放入烤架，关门；实际温度和预热完成未确证。",
        "reason": "应用后轮修订，去除过度断言并分离观察、推断、文本用途。",
        "source": {
          "path": "annotation_reports/verification_report.md",
          "line": 84,
          "section": "B"
        }
      }
    ]
  }
]
```

### objects

```json
[
  {
    "id": "O01",
    "name": "方形透明塑料容器（混合容器）",
    "identity_status": "CANDIDATE",
    "original_candidate": {
      "id": "O01",
      "name": "方形透明塑料容器（混合容器）",
      "time_range": "00:00:29–11:19",
      "operation": "选定→装料→搅拌→倒空",
      "before": "空置嵌套存放",
      "after": "依次加入蛋液、糖、牛奶、面粉、融化黄油并三次搅拌，最终面糊倒出、容器近空（内留刮刀）",
      "event_ids_text": "E005, E010, E011, E018, E023, E032, E044, E027, E045, E052, E053",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 88,
        "section": "C"
      },
      "raw_row": "| O01 | 方形透明塑料容器（混合容器） | 00:00:29–11:19 | 选定→装料→搅拌→倒空 | 空置嵌套存放 | 依次加入蛋液、糖、牛奶、面粉、融化黄油并三次搅拌，最终面糊倒出、容器近空（内留刮刀） | E005, E010, E011, E018, E023, E032, E044, E027, E045, E052, E053 |"
    },
    "summary": "选定混合容器，逐步装料并三次电动搅拌；面糊转移后近空，后段报告可见内留黑色工具。",
    "identity_relations": [],
    "facts": [],
    "event_ids": [
      "E005",
      "E010",
      "E011",
      "E012",
      "E018",
      "E023",
      "E027",
      "E032",
      "E033",
      "E044",
      "E045",
      "E046",
      "E050",
      "E051",
      "E052",
      "E053",
      "E054"
    ],
    "state_history": [
      {
        "id": "O01.S01",
        "event_id": "E005",
        "time": {
          "start_sec": 29.0,
          "end_sec": 41.0,
          "start_hms": "00:00:29.000",
          "end_hms": "00:00:41.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "location",
        "before": "旁侧嵌套存放",
        "after": "台面中央、空置",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E005-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O01.S02",
        "event_id": "E010",
        "time": {
          "start_sec": 60.0,
          "end_sec": 66.0,
          "start_hms": "00:01:00.000",
          "end_hms": "00:01:06.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "contents",
        "before": null,
        "after": "一枚蛋液（一个蛋黄）",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E010-01",
          "V-E010-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O01.S03",
        "event_id": "E011",
        "time": {
          "start_sec": 67.0,
          "end_sec": 76.0,
          "start_hms": "00:01:07.000",
          "end_hms": "00:01:16.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "contents",
        "before": null,
        "after": "累计两枚蛋液（两个蛋黄）",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E011-01",
          "V-E011-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O01.S04",
        "event_id": "E018",
        "time": {
          "start_sec": 123.0,
          "end_sec": 132.0,
          "start_hms": "00:02:03.000",
          "end_hms": "00:02:12.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "contents",
        "before": null,
        "after": "蛋液上新增褐色糖堆",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E018-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O01.S05",
        "event_id": "E023",
        "time": {
          "start_sec": 158.0,
          "end_sec": 165.0,
          "start_hms": "00:02:38.000",
          "end_hms": "00:02:45.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "contents",
        "before": null,
        "after": "新增牛奶",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E023-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O01.S06",
        "event_id": "E027",
        "time": {
          "start_sec": 199,
          "end_sec": 235,
          "start_hms": "00:03:19.000",
          "end_hms": "00:03:55.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "contents",
        "before": "蛋/糖/奶分层",
        "after": "淡黄均匀液",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E027-01",
          "V-E027-02",
          "V-E027-03"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O01.S07",
        "event_id": "E032",
        "time": {
          "start_sec": 283.0,
          "end_sec": 292.0,
          "start_hms": "00:04:43.000",
          "end_hms": "00:04:52.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "contents",
        "before": null,
        "after": "淡黄液面新增白色粉堆",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E032-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O01.S08",
        "event_id": "E044",
        "time": {
          "start_sec": 461.0,
          "end_sec": 469.0,
          "start_hms": "00:07:41.000",
          "end_hms": "00:07:49.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "contents",
        "before": null,
        "after": "新增倒入的黄油；是否含固块另列未知",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E044-01",
          "V-E044-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O01.S09",
        "event_id": "E045",
        "time": {
          "start_sec": 470.0,
          "end_sec": 529.0,
          "start_hms": "00:07:50.000",
          "end_hms": "00:08:49.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "contents",
        "before": "粉/液分层",
        "after": "稠厚淡黄糊",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E045-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O01.S10",
        "event_id": "E051",
        "time": {
          "start_sec": 595,
          "end_sec": 604,
          "start_hms": "00:09:55.000",
          "end_hms": "00:10:04.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "contents",
        "before": null,
        "after": "面糊表面新增干粉",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E051-01",
          "V-E051-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O01.S11",
        "event_id": "E052",
        "time": {
          "start_sec": 605.0,
          "end_sec": 631.0,
          "start_hms": "00:10:05.000",
          "end_hms": "00:10:31.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "contents",
        "before": "表面带干粉",
        "after": "光滑均匀淡黄面糊",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E052-01",
          "V-E052-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O01.S12",
        "event_id": "E053",
        "time": {
          "start_sec": 633,
          "end_sec": 679,
          "start_hms": "00:10:33.000",
          "end_hms": "00:11:19.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "contents",
        "before": null,
        "after": "面糊已转入烤模、容器近空",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E053-01",
          "V-E053-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O01.S13",
        "event_id": "E054",
        "time": {
          "start_sec": 680.2,
          "end_sec": 680.2,
          "start_hms": "00:11:20.200",
          "end_hms": "00:11:20.200"
        },
        "temporal_role": "during",
        "kind": "observation",
        "field": "tool_present",
        "before": null,
        "after": "内留黑色刮刀/勺状工具",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E054-01"
        ],
        "reason": "工具已在容器内，仅观察结果状态；放置动作时间未知。"
      }
    ],
    "revisions": [
      {
        "field": "identity/state_history",
        "before": "依次加入蛋液、糖、牛奶、面粉、融化黄油并三次搅拌，最终面糊倒出、容器近空（内留刮刀）",
        "after": "选定混合容器，逐步装料并三次电动搅拌；面糊转移后近空，后段报告可见内留黑色工具。",
        "reason": "将11:20s内留工具记为状态，放置动作时间未知。",
        "source": {
          "path": "annotation_reports/consistency_revision.md",
          "section": "3–6"
        }
      }
    ]
  },
  {
    "id": "O05",
    "name": "黑色量杯组",
    "identity_status": "GROUP",
    "original_candidate": {
      "id": "O05",
      "name": "黑色量杯组",
      "time_range": "01:38–10:49",
      "operation": "多次取用（糖、牛奶、面粉、搅黄油、刮糊）",
      "before": "成组放置台面",
      "after": "单只反复手持使用并放回；末期一只作为刮刀使用",
      "event_ids_text": "E015, E020, E022, E031, E043, E053",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 92,
        "section": "C"
      },
      "raw_row": "| O05 | 黑色量杯组 | 01:38–10:49 | 多次取用（糖、牛奶、面粉、搅黄油、刮糊） | 成组放置台面 | 单只反复手持使用并放回；末期一只作为刮刀使用 | E015, E020, E022, E031, E043, E053 |"
    },
    "summary": "量杯组用于糖/奶/粉量取；各段单杯同一性及实际规格未知，不将后段刮刀并入已确认身份。",
    "identity_relations": [
      {
        "object_id": "O16",
        "relation": "SAME_AS_UNKNOWN",
        "evidence_ids": [
          "V-E043-01",
          "V-E043-02",
          "I-E043-01"
        ],
        "reason": "不同观察指称，不断言同一件，也不证明一定为不同件。"
      },
      {
        "object_id": "O17",
        "relation": "SAME_AS_UNKNOWN",
        "evidence_ids": [
          "V-E053-01",
          "V-E053-02",
          "I-E053-01"
        ],
        "reason": "不同观察指称，不断言同一件，也不证明一定为不同件。"
      }
    ],
    "facts": [],
    "event_ids": [
      "E015",
      "E016",
      "E018",
      "E019",
      "E020",
      "E022",
      "E023",
      "E029",
      "E031",
      "E032"
    ],
    "state_history": [
      {
        "id": "O05.S01",
        "event_id": "E015",
        "time": {
          "start_sec": 98.0,
          "end_sec": 106.0,
          "start_hms": "00:01:38.000",
          "end_hms": "00:01:46.000"
        },
        "temporal_role": "during",
        "kind": "observation",
        "field": "group_member_use",
        "before": null,
        "after": "取一只量杯查看",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E015-01"
        ],
        "reason": "指组内当时观察到的一只量杯，不推定与其他时段为同一只。"
      },
      {
        "id": "O05.S02",
        "event_id": "E016",
        "time": {
          "start_sec": 107.0,
          "end_sec": 119.0,
          "start_hms": "00:01:47.000",
          "end_hms": "00:01:59.000"
        },
        "temporal_role": "during",
        "kind": "observation",
        "field": "group_member_use",
        "before": null,
        "after": "杯内见褐色糖",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E016-01"
        ],
        "reason": "指组内当时观察到的一只量杯，不推定与其他时段为同一只。"
      },
      {
        "id": "O05.S03",
        "event_id": "E018",
        "time": {
          "start_sec": 123.0,
          "end_sec": 132.0,
          "start_hms": "00:02:03.000",
          "end_hms": "00:02:12.000"
        },
        "temporal_role": "during",
        "kind": "observation",
        "field": "group_member_use",
        "before": null,
        "after": "杯内糖倒入混合容器",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E018-01"
        ],
        "reason": "指组内当时观察到的一只量杯，不推定与其他时段为同一只。"
      },
      {
        "id": "O05.S04",
        "event_id": "E019",
        "time": {
          "start_sec": 133.0,
          "end_sec": 138.0,
          "start_hms": "00:02:13.000",
          "end_hms": "00:02:18.000"
        },
        "temporal_role": "during",
        "kind": "observation",
        "field": "group_member_use",
        "before": null,
        "after": "量杯放回",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E019-01"
        ],
        "reason": "指组内当时观察到的一只量杯，不推定与其他时段为同一只。"
      },
      {
        "id": "O05.S05",
        "event_id": "E020",
        "time": {
          "start_sec": 139.0,
          "end_sec": 145.0,
          "start_hms": "00:02:19.000",
          "end_hms": "00:02:25.000"
        },
        "temporal_role": "during",
        "kind": "observation",
        "field": "group_member_use",
        "before": null,
        "after": "查看量杯；一只杯柄见1/4 CUP",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E020-01",
          "V-E020-02"
        ],
        "reason": "指组内当时观察到的一只量杯，不推定与其他时段为同一只。"
      },
      {
        "id": "O05.S11",
        "event_id": "E020",
        "time": {
          "start_sec": 139.0,
          "end_sec": 145.0,
          "start_hms": "00:02:19.000",
          "end_hms": "00:02:25.000"
        },
        "temporal_role": "during",
        "kind": "observation",
        "field": "same_cup_as_E015",
        "before": null,
        "after": null,
        "status": "UNCERTAIN",
        "evidence_ids": [
          "V-E020-01",
          "V-E020-02",
          "I-E020-02"
        ],
        "reason": "单杯身份无连续跟踪。"
      },
      {
        "id": "O05.S06",
        "event_id": "E022",
        "time": {
          "start_sec": 152.0,
          "end_sec": 157.0,
          "start_hms": "00:02:32.000",
          "end_hms": "00:02:37.000"
        },
        "temporal_role": "during",
        "kind": "observation",
        "field": "group_member_use",
        "before": null,
        "after": "杯中量取牛奶",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E022-01"
        ],
        "reason": "指组内当时观察到的一只量杯，不推定与其他时段为同一只。"
      },
      {
        "id": "O05.S07",
        "event_id": "E023",
        "time": {
          "start_sec": 158.0,
          "end_sec": 165.0,
          "start_hms": "00:02:38.000",
          "end_hms": "00:02:45.000"
        },
        "temporal_role": "during",
        "kind": "observation",
        "field": "group_member_use",
        "before": null,
        "after": "杯中奶倒入混合容器",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E023-01"
        ],
        "reason": "指组内当时观察到的一只量杯，不推定与其他时段为同一只。"
      },
      {
        "id": "O05.S08",
        "event_id": "E029",
        "time": {
          "start_sec": 240.0,
          "end_sec": 258.0,
          "start_hms": "00:04:00.000",
          "end_hms": "00:04:18.000"
        },
        "temporal_role": "during",
        "kind": "observation",
        "field": "group_member_use",
        "before": null,
        "after": "手持空量杯",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E029-01",
          "V-E029-02"
        ],
        "reason": "指组内当时观察到的一只量杯，不推定与其他时段为同一只。"
      },
      {
        "id": "O05.S09",
        "event_id": "E031",
        "time": {
          "start_sec": 269.0,
          "end_sec": 282.0,
          "start_hms": "00:04:29.000",
          "end_hms": "00:04:42.000"
        },
        "temporal_role": "during",
        "kind": "observation",
        "field": "group_member_use",
        "before": null,
        "after": "杯中量取面粉",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E031-01"
        ],
        "reason": "指组内当时观察到的一只量杯，不推定与其他时段为同一只。"
      },
      {
        "id": "O05.S10",
        "event_id": "E032",
        "time": {
          "start_sec": 283.0,
          "end_sec": 292.0,
          "start_hms": "00:04:43.000",
          "end_hms": "00:04:52.000"
        },
        "temporal_role": "during",
        "kind": "observation",
        "field": "group_member_use",
        "before": null,
        "after": "杯中面粉倒入混合容器",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E032-01"
        ],
        "reason": "指组内当时观察到的一只量杯，不推定与其他时段为同一只。"
      }
    ],
    "revisions": [
      {
        "field": "identity/state_history",
        "before": "单只反复手持使用并放回；末期一只作为刮刀使用",
        "after": "量杯组用于糖/奶/粉量取；各段单杯同一性及实际规格未知，不将后段刮刀并入已确认身份。",
        "reason": "保持量杯组ID；移除末期一只充当刮刀的身份断言，关联O16/O17未知关系。",
        "source": {
          "path": "annotation_reports/consistency_revision.md",
          "section": "3–6"
        }
      }
    ]
  },
  {
    "id": "O06",
    "name": "牛奶盒（品牌文字为原候选线索）",
    "identity_status": "CANDIDATE",
    "original_candidate": {
      "id": "O06",
      "name": "牛奶盒（Horizon Organic）",
      "time_range": "02:26–02:53",
      "operation": "开盖→倒奶→拧盖归位",
      "before": "闭合立置",
      "after": "开启倒出部分牛奶后闭合归位",
      "event_ids_text": "E021–E024",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 93,
        "section": "C"
      },
      "raw_row": "| O06 | 牛奶盒（Horizon Organic） | 02:26–02:53 | 开盖→倒奶→拧盖归位 | 闭合立置 | 开启倒出部分牛奶后闭合归位 | E021–E024 |"
    },
    "summary": "开黄盖、量奶、拧盖归位；实际奶体积未知。",
    "identity_relations": [],
    "facts": [
      {
        "field": "brand",
        "value": "Horizon Organic",
        "status": "UNCERTAIN",
        "evidence_ids": [
          "H-O06-NAME"
        ],
        "reason": "后续报告未提供独立标签核验；保留原文字作为线索。"
      }
    ],
    "event_ids": [
      "E021",
      "E022",
      "E024"
    ],
    "state_history": [
      {
        "id": "O06.S01",
        "event_id": "E021",
        "time": {
          "start_sec": 146.0,
          "end_sec": 151.0,
          "start_hms": "00:02:26.000",
          "end_hms": "00:02:31.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "closure",
        "before": null,
        "after": "黄盖打开",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E021-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O06.S02",
        "event_id": "E022",
        "time": {
          "start_sec": 152.0,
          "end_sec": 157.0,
          "start_hms": "00:02:32.000",
          "end_hms": "00:02:37.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "contents_use",
        "before": null,
        "after": "部分牛奶倒入量杯",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E022-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O06.S03",
        "event_id": "E024",
        "time": {
          "start_sec": 164.0,
          "end_sec": 173.0,
          "start_hms": "00:02:44.000",
          "end_hms": "00:02:53.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "closure_and_location",
        "before": null,
        "after": "拧回黄盖、归位灶侧",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E024-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      }
    ],
    "revisions": []
  },
  {
    "id": "O07",
    "name": "手持电动打蛋器+搅拌棒",
    "identity_status": "GROUP",
    "original_candidate": {
      "id": "O07",
      "name": "手持电动打蛋器+搅拌棒",
      "time_range": "02:54–10:31",
      "operation": "装配→三次搅拌→放置",
      "before": "本体与棒分离放置",
      "after": "双棒装配并完成三次搅拌，末期放台面",
      "event_ids_text": "E025, E027, E045, E052",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 94,
        "section": "C"
      },
      "raw_row": "| O07 | 手持电动打蛋器+搅拌棒 | 02:54–10:31 | 装配→三次搅拌→放置 | 本体与棒分离放置 | 双棒装配并完成三次搅拌，末期放台面 | E025, E027, E045, E052 |"
    },
    "summary": "装两根搅拌棒，完成三次可见电动搅拌。",
    "identity_relations": [],
    "facts": [],
    "event_ids": [
      "E025",
      "E026",
      "E027",
      "E028",
      "E045",
      "E046",
      "E052"
    ],
    "state_history": [
      {
        "id": "O07.S01",
        "event_id": "E025",
        "time": {
          "start_sec": 174.0,
          "end_sec": 193.0,
          "start_hms": "00:02:54.000",
          "end_hms": "00:03:13.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "assembly",
        "before": "本体与棒分离",
        "after": "两根棒装入本体",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E025-01",
          "V-E025-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O07.S02",
        "event_id": "E027",
        "time": {
          "start_sec": 199,
          "end_sec": 235,
          "start_hms": "00:03:19.000",
          "end_hms": "00:03:55.000"
        },
        "temporal_role": "during",
        "kind": "observation",
        "field": "mixing_round",
        "before": null,
        "after": 1,
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E027-01",
          "V-E027-02",
          "V-E027-03"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O07.S05",
        "event_id": "E028",
        "time": {
          "start_sec": 234.0,
          "end_sec": 239.0,
          "start_hms": "00:03:54.000",
          "end_hms": "00:03:59.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "location",
        "before": null,
        "after": "提离混合容器并置左台面",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E028-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O07.S03",
        "event_id": "E045",
        "time": {
          "start_sec": 470.0,
          "end_sec": 529.0,
          "start_hms": "00:07:50.000",
          "end_hms": "00:08:49.000"
        },
        "temporal_role": "during",
        "kind": "observation",
        "field": "mixing_round",
        "before": null,
        "after": 2,
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E045-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O07.S04",
        "event_id": "E052",
        "time": {
          "start_sec": 605.0,
          "end_sec": 631.0,
          "start_hms": "00:10:05.000",
          "end_hms": "00:10:31.000"
        },
        "temporal_role": "during",
        "kind": "observation",
        "field": "mixing_round",
        "before": null,
        "after": 3,
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E052-01",
          "V-E052-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      }
    ],
    "revisions": []
  },
  {
    "id": "O08",
    "name": "面粉纸袋（品牌文字为原候选线索）",
    "identity_status": "CANDIDATE",
    "original_candidate": {
      "id": "O08",
      "name": "面粉纸袋（All-Purpose Flour）",
      "time_range": "04:19–10:04",
      "operation": "柜内取出→量取→直接补加",
      "before": "吊柜内封存",
      "after": "开口袋，两次向容器/量杯供粉后立置右侧台面",
      "event_ids_text": "E030, E031, E051",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 95,
        "section": "C"
      },
      "raw_row": "| O08 | 面粉纸袋（All-Purpose Flour） | 04:19–10:04 | 柜内取出→量取→直接补加 | 吊柜内封存 | 开口袋，两次向容器/量杯供粉后立置右侧台面 | E030, E031, E051 |"
    },
    "summary": "吊柜取袋、供粉至量杯、后段直接补粉；加入混合容器可见两次，不作量值断言。",
    "identity_relations": [],
    "facts": [
      {
        "field": "brand_and_product",
        "value": "Trader Joe's All-Purpose Flour",
        "status": "UNCERTAIN",
        "evidence_ids": [
          "H-O08-NAME"
        ],
        "reason": "后续报告未提供独立标签核验；保留原文字作为线索。"
      }
    ],
    "event_ids": [
      "E030",
      "E031",
      "E051"
    ],
    "state_history": [
      {
        "id": "O08.S01",
        "event_id": "E030",
        "time": {
          "start_sec": 259.0,
          "end_sec": 268.0,
          "start_hms": "00:04:19.000",
          "end_hms": "00:04:28.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "location",
        "before": null,
        "after": "从吊柜取出至手持",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E030-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O08.S02",
        "event_id": "E031",
        "time": {
          "start_sec": 269.0,
          "end_sec": 282.0,
          "start_hms": "00:04:29.000",
          "end_hms": "00:04:42.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "contents_use",
        "before": null,
        "after": "开袋、供粉入量杯",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E031-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O08.S03",
        "event_id": "E051",
        "time": {
          "start_sec": 595,
          "end_sec": 604,
          "start_hms": "00:09:55.000",
          "end_hms": "00:10:04.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "contents_use",
        "before": null,
        "after": "袋直接供粉入混合容器",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E051-01",
          "V-E051-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      }
    ],
    "revisions": []
  },
  {
    "id": "O12",
    "name": "面包烤模（loaf pan）",
    "identity_status": "CANDIDATE",
    "original_candidate": {
      "id": "O12",
      "name": "面包烤模（loaf pan）",
      "time_range": "00:20–11:32",
      "operation": "空模放置→抹油→装糊→入烤箱",
      "before": "空置台面",
      "after": "内壁沾油→装入面糊→置于烤箱烤架",
      "event_ids_text": "E049, E053, E055",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 99,
        "section": "C"
      },
      "raw_row": "| O12 | 面包烤模（loaf pan） | 00:20–11:32 | 空模放置→抹油→装糊→入烤箱 | 空置台面 | 内壁沾油→装入面糊→置于烤箱烤架 | E049, E053, E055 |"
    },
    "summary": "模底见油并被倾斜旋转；内壁油膜未知；后续装面糊并入烤箱。",
    "identity_relations": [],
    "facts": [],
    "event_ids": [
      "E049",
      "E053",
      "E055"
    ],
    "state_history": [
      {
        "id": "O12.S01",
        "event_id": "E049",
        "time": {
          "start_sec": 560,
          "end_sec": 581,
          "start_hms": "00:09:20.000",
          "end_hms": "00:09:41.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "oil_at_bottom",
        "before": null,
        "after": "模底见少量油；烤模被倾斜旋转",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E049-01",
          "V-E049-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O12.S02",
        "event_id": "E049",
        "time": {
          "start_sec": 560,
          "end_sec": 581,
          "start_hms": "00:09:20.000",
          "end_hms": "00:09:41.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "inner_wall_oil_film",
        "before": null,
        "after": null,
        "status": "UNCERTAIN",
        "evidence_ids": [
          "V-E049-01",
          "V-E049-02",
          "I-E049-01",
          "T-R43",
          "T-R45"
        ],
        "reason": "动作不等于油膜分布确证。"
      },
      {
        "id": "O12.S03",
        "event_id": "E053",
        "time": {
          "start_sec": 633,
          "end_sec": 679,
          "start_hms": "00:10:33.000",
          "end_hms": "00:11:19.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "contents",
        "before": null,
        "after": "装入面糊",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E053-01",
          "V-E053-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O12.S04",
        "event_id": "E055",
        "time": {
          "start_sec": 687,
          "end_sec": 692,
          "start_hms": "00:11:27.000",
          "end_hms": "00:11:32.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "location",
        "before": null,
        "after": "烤箱烤架内",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E055-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      }
    ],
    "revisions": [
      {
        "field": "identity/state_history",
        "before": "内壁沾油→装入面糊→置于烤箱烤架",
        "after": "模底见油并被倾斜旋转；内壁油膜未知；后续装面糊并入烤箱。",
        "reason": "内壁沾油降为未知，模底见油和旋转保留。",
        "source": {
          "path": "annotation_reports/consistency_revision.md",
          "section": "3–6"
        }
      }
    ]
  },
  {
    "id": "O13",
    "name": "食用油瓶（绿盖）",
    "identity_status": "CANDIDATE",
    "original_candidate": {
      "id": "O13",
      "name": "食用油瓶（绿盖）",
      "time_range": "09:08–09:25",
      "operation": "取用开盖倒油",
      "before": "闭合立置",
      "after": "开启并倒出少量油后持于台面（盖开放）",
      "event_ids_text": "E048, E049",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 100,
        "section": "C"
      },
      "raw_row": "| O13 | 食用油瓶（绿盖） | 09:08–09:25 | 取用开盖倒油 | 闭合立置 | 开启并倒出少量油后持于台面（盖开放） | E048, E049 |"
    },
    "summary": "取瓶、开绿盖、倒油；后续是否复盖没有足够证据。",
    "identity_relations": [],
    "facts": [],
    "event_ids": [
      "E048",
      "E049"
    ],
    "state_history": [
      {
        "id": "O13.S01",
        "event_id": "E048",
        "time": {
          "start_sec": 548.0,
          "end_sec": 565.0,
          "start_hms": "00:09:08.000",
          "end_hms": "00:09:25.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "closure",
        "before": null,
        "after": "绿盖打开",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E048-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O13.S02",
        "event_id": "E049",
        "time": {
          "start_sec": 560,
          "end_sec": 581,
          "start_hms": "00:09:20.000",
          "end_hms": "00:09:41.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "contents_use",
        "before": null,
        "after": "少量油倒入烤模",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E049-01",
          "V-E049-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      }
    ],
    "revisions": []
  },
  {
    "id": "O14",
    "name": "烤箱/灶台",
    "identity_status": "CANDIDATE",
    "original_candidate": {
      "id": "O14",
      "name": "烤箱/灶台",
      "time_range": "00:10–11:32",
      "operation": "面板设定→放入烤模",
      "before": "显示时钟样数字",
      "after": "显示 \"100\"（疑似预热设定）；末期烤模入内、门关闭",
      "event_ids_text": "E002, E055",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 101,
        "section": "C"
      },
      "raw_row": "| O14 | 烤箱/灶台 | 00:10–11:32 | 面板设定→放入烤模 | 显示时钟样数字 | 显示 \"100\"（疑似预热设定）；末期烤模入内、门关闭 | E002, E055 |"
    },
    "summary": "按键后显示100；显示语义、实际温度、预热完成未知；烤模入架后门关闭。",
    "identity_relations": [],
    "facts": [],
    "event_ids": [
      "E002",
      "E003",
      "E055",
      "E056"
    ],
    "state_history": [
      {
        "id": "O14.S03",
        "event_id": "E002",
        "time": {
          "start_sec": 10.0,
          "end_sec": 14.0,
          "start_hms": "00:00:10.000",
          "end_hms": "00:00:14.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "display_semantics",
        "before": null,
        "after": null,
        "status": "UNCERTAIN",
        "evidence_ids": [
          "V-E002-01",
          "V-E002-02",
          "H-E002-02",
          "T-R01",
          "T-R02"
        ],
        "reason": "显示语义未知，不能当预热温度。"
      },
      {
        "id": "O14.S02",
        "event_id": "E003",
        "time": {
          "start_sec": 15.0,
          "end_sec": 19.0,
          "start_hms": "00:00:15.000",
          "end_hms": "00:00:19.000"
        },
        "temporal_role": "during",
        "kind": "observation",
        "field": "display",
        "before": null,
        "after": "100",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E003-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O14.S01",
        "event_id": "E002",
        "time": {
          "start_sec": 15.2,
          "end_sec": 15.2,
          "start_hms": "00:00:15.200",
          "end_hms": "00:00:15.200"
        },
        "temporal_role": "aftermath",
        "kind": "observation",
        "field": "display",
        "before": null,
        "after": "100",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E002-02"
        ],
        "reason": "按键后的结果帧，比事件末界晚1.2s；不证明按键因果或温度语义。"
      },
      {
        "id": "O14.S04",
        "event_id": "E055",
        "time": {
          "start_sec": 687,
          "end_sec": 692,
          "start_hms": "00:11:27.000",
          "end_hms": "00:11:32.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "door_and_contents",
        "before": null,
        "after": "门打开、置入盛面糊烤模、关门",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E055-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O14.S05",
        "event_id": "E055",
        "time": {
          "start_sec": 687,
          "end_sec": 692,
          "start_hms": "00:11:27.000",
          "end_hms": "00:11:32.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "oven_preheat_complete",
        "before": null,
        "after": null,
        "status": "UNCERTAIN",
        "evidence_ids": [
          "V-E055-01",
          "H-E055-01",
          "T-R01",
          "T-R02"
        ],
        "reason": "预热完成无实际温度证据。"
      }
    ],
    "revisions": [
      {
        "field": "identity/state_history",
        "before": "显示 \"100\"（疑似预热设定）；末期烤模入内、门关闭",
        "after": "按键后显示100；显示语义、实际温度、预热完成未知；烤模入架后门关闭。",
        "reason": "100语义和预热完成未知。",
        "source": {
          "path": "annotation_reports/consistency_revision.md",
          "section": "3–6"
        }
      }
    ]
  },
  {
    "id": "O15",
    "name": "中间混合物/面糊（随配料逐步形成）",
    "identity_status": "CANDIDATE",
    "original_candidate": {
      "id": "O15",
      "name": "中间产物：面糊",
      "time_range": "01:00–11:32",
      "operation": "逐步混合形成",
      "before": "不存在",
      "after": "蛋液→+糖+奶均匀液→+面粉稠糊→+黄油光滑面糊→入模",
      "event_ids_text": "E010–E055",
      "source": {
        "path": "annotation_reports/candidate_events_v1.md",
        "line": 102,
        "section": "C"
      },
      "raw_row": "| O15 | 中间产物：面糊 | 01:00–11:32 | 逐步混合形成 | 不存在 | 蛋液→+糖+奶均匀液→+面粉稠糊→+黄油光滑面糊→入模 | E010–E055 |"
    },
    "summary": "蛋液→加糖/奶→均匀淡黄液→表层干粉→加黄油→稠糊→补粉/搅拌成光滑面糊→入模/入烤箱。",
    "identity_relations": [],
    "facts": [],
    "event_ids": [
      "E010",
      "E011",
      "E012",
      "E018",
      "E023",
      "E027",
      "E032",
      "E033",
      "E044",
      "E045",
      "E046",
      "E050",
      "E051",
      "E052",
      "E053",
      "E055"
    ],
    "state_history": [
      {
        "id": "O15.S01",
        "event_id": "E010",
        "time": {
          "start_sec": 60.0,
          "end_sec": 66.0,
          "start_hms": "00:01:00.000",
          "end_hms": "00:01:06.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "mixture_state",
        "before": null,
        "after": "一枚蛋液",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E010-01",
          "V-E010-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O15.S02",
        "event_id": "E011",
        "time": {
          "start_sec": 67.0,
          "end_sec": 76.0,
          "start_hms": "00:01:07.000",
          "end_hms": "00:01:16.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "mixture_state",
        "before": null,
        "after": "累计两枚蛋液",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E011-01",
          "V-E011-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O15.S03",
        "event_id": "E018",
        "time": {
          "start_sec": 123.0,
          "end_sec": 132.0,
          "start_hms": "00:02:03.000",
          "end_hms": "00:02:12.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "mixture_state",
        "before": null,
        "after": "蛋液上加入糖堆",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E018-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O15.S04",
        "event_id": "E023",
        "time": {
          "start_sec": 158.0,
          "end_sec": 165.0,
          "start_hms": "00:02:38.000",
          "end_hms": "00:02:45.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "mixture_state",
        "before": null,
        "after": "加入牛奶",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E023-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O15.S05",
        "event_id": "E027",
        "time": {
          "start_sec": 199,
          "end_sec": 235,
          "start_hms": "00:03:19.000",
          "end_hms": "00:03:55.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "mixture_state",
        "before": null,
        "after": "均匀淡黄混合液",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E027-01",
          "V-E027-02",
          "V-E027-03"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O15.S06",
        "event_id": "E032",
        "time": {
          "start_sec": 283.0,
          "end_sec": 292.0,
          "start_hms": "00:04:43.000",
          "end_hms": "00:04:52.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "mixture_state",
        "before": null,
        "after": "液面新增干粉层",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E032-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O15.S07",
        "event_id": "E044",
        "time": {
          "start_sec": 461.0,
          "end_sec": 469.0,
          "start_hms": "00:07:41.000",
          "end_hms": "00:07:49.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "mixture_state",
        "before": null,
        "after": "加入黄油，固块终态未知",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E044-01",
          "V-E044-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O15.S08",
        "event_id": "E045",
        "time": {
          "start_sec": 470.0,
          "end_sec": 529.0,
          "start_hms": "00:07:50.000",
          "end_hms": "00:08:49.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "mixture_state",
        "before": null,
        "after": "稠厚淡黄糊",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E045-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O15.S09",
        "event_id": "E051",
        "time": {
          "start_sec": 595,
          "end_sec": 604,
          "start_hms": "00:09:55.000",
          "end_hms": "00:10:04.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "mixture_state",
        "before": null,
        "after": "表面补加干粉",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E051-01",
          "V-E051-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O15.S10",
        "event_id": "E052",
        "time": {
          "start_sec": 605.0,
          "end_sec": 631.0,
          "start_hms": "00:10:05.000",
          "end_hms": "00:10:31.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "mixture_state",
        "before": null,
        "after": "光滑均匀面糊",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E052-01",
          "V-E052-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O15.S11",
        "event_id": "E053",
        "time": {
          "start_sec": 633,
          "end_sec": 679,
          "start_hms": "00:10:33.000",
          "end_hms": "00:11:19.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "mixture_state",
        "before": null,
        "after": "转入烤模",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E053-01",
          "V-E053-02"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      },
      {
        "id": "O15.S12",
        "event_id": "E055",
        "time": {
          "start_sec": 687,
          "end_sec": 692,
          "start_hms": "00:11:27.000",
          "end_hms": "00:11:32.000"
        },
        "temporal_role": "during",
        "kind": "transition",
        "field": "mixture_state",
        "before": null,
        "after": "随烤模入烤箱",
        "status": "REPORTED_SUPPORTED",
        "evidence_ids": [
          "V-E055-01"
        ],
        "reason": "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"
      }
    ],
    "revisions": [
      {
        "field": "identity/state_history",
        "before": "蛋液→+糖+奶均匀液→+面粉稠糊→+黄油光滑面糊→入模",
        "after": "蛋液→加糖/奶→均匀淡黄液→表层干粉→加黄油→稠糊→补粉/搅拌成光滑面糊→入模/入烤箱。",
        "reason": "面粉层加入后未立即搅拌；稠糊节点到E045才出现，不能提前继承。",
        "source": {
          "path": "annotation_reports/consistency_revision.md",
          "section": "3–6"
        }
      }
    ]
  }
]
```

### review_items

```json
[
  {
    "id": "RQ03",
    "priority": "P1",
    "status": "OPEN",
    "title": "烤模内壁油膜",
    "question": "确认油是否覆盖内壁及其分布；倾斜旋转与Success评价均不足以证明油膜。",
    "time_ranges": [
      {
        "start_sec": 560,
        "end_sec": 581,
        "start_hms": "00:09:20.000",
        "end_hms": "00:09:41.000"
      }
    ],
    "event_ids": [
      "E049"
    ],
    "object_ids": [
      "O12",
      "O13"
    ],
    "ego_mc_record_ids": [
      "R43",
      "R45"
    ],
    "targets": [
      {
        "artifact": "events",
        "record_id": "E049",
        "field": "facts/inner_wall_oil_film"
      },
      {
        "artifact": "objects",
        "record_id": "O12",
        "field": "state_history/O12.S02"
      }
    ],
    "evidence_ids": [
      "V-E049-01",
      "V-E049-02",
      "I-E049-01",
      "T-R43",
      "T-R45"
    ],
    "sources": [
      {
        "path": "annotation_reports/verification_report.md",
        "section": "F/P0"
      },
      {
        "path": "annotation_reports/consistency_revision.md",
        "section": "7"
      },
      {
        "path": "annotation_reports/crosscheck_report.md",
        "section": "D/P1"
      }
    ],
    "review_method": "人工查看连续视频/高清局部并记录裁决；若仍无证据则保留UNCERTAIN。",
    "priority_notes": "第三轮/第二轮P0；第四轮D表降为P1，本整合采用第四轮P1，字段仍UNCERTAIN。"
  },
  {
    "id": "RQ05",
    "priority": "P1",
    "status": "OPEN",
    "title": "牛奶量杯规格和实际量值",
    "question": "确认实际使用杯是否为标签1/4 CUP的杯、规格与倒奶量；半杯指令/自述不能代替量值。",
    "time_ranges": [
      {
        "start_sec": 139,
        "end_sec": 165,
        "start_hms": "00:02:19.000",
        "end_hms": "00:02:45.000"
      }
    ],
    "event_ids": [
      "E020",
      "E022",
      "E023"
    ],
    "object_ids": [
      "O01",
      "O05",
      "O06",
      "O15"
    ],
    "ego_mc_record_ids": [
      "R18",
      "R19"
    ],
    "targets": [
      {
        "artifact": "events",
        "record_id": "E020",
        "field": "facts/same_cup_as_E015"
      },
      {
        "artifact": "events",
        "record_id": "E020",
        "field": "facts/search_purpose"
      },
      {
        "artifact": "events",
        "record_id": "E022",
        "field": "facts/milk_volume_cup"
      },
      {
        "artifact": "events",
        "record_id": "E023",
        "field": "facts/milk_volume_cup"
      },
      {
        "artifact": "objects",
        "record_id": "O05",
        "field": "state_history/O05.S11"
      }
    ],
    "evidence_ids": [
      "V-E020-01",
      "V-E020-02",
      "I-E020-02",
      "T-R18",
      "T-R19",
      "V-E022-01",
      "V-E023-01"
    ],
    "sources": [
      {
        "path": "annotation_reports/crosscheck_report.md",
        "section": "C/Q-03、D/P1"
      }
    ],
    "review_method": "人工查看连续视频/高清局部并记录裁决；若仍无证据则保留UNCERTAIN。",
    "priority_notes": "优先采用第四轮D节明确片段清单；未覆盖问题沿用先前优先级，保留来源，不改变事实状态。"
  },
  {
    "id": "RQ06",
    "priority": "P1",
    "status": "OPEN",
    "title": "首次面粉量杯规格和实际量值",
    "question": "确认杯规格与实际加粉量；R26一杯仅为文本线索。",
    "time_ranges": [
      {
        "start_sec": 269,
        "end_sec": 292,
        "start_hms": "00:04:29.000",
        "end_hms": "00:04:52.000"
      }
    ],
    "event_ids": [
      "E031",
      "E032"
    ],
    "object_ids": [
      "O01",
      "O05",
      "O08",
      "O15"
    ],
    "ego_mc_record_ids": [
      "R26"
    ],
    "targets": [
      {
        "artifact": "events",
        "record_id": "E031",
        "field": "facts/flour_volume_cup"
      },
      {
        "artifact": "events",
        "record_id": "E032",
        "field": "facts/flour_volume_cup"
      }
    ],
    "evidence_ids": [
      "V-E031-01",
      "T-R26",
      "V-E032-01"
    ],
    "sources": [
      {
        "path": "annotation_reports/crosscheck_report.md",
        "section": "C/Q-04、D/P1"
      }
    ],
    "review_method": "人工查看连续视频/高清局部并记录裁决；若仍无证据则保留UNCERTAIN。",
    "priority_notes": "优先采用第四轮D节明确片段清单；未覆盖问题沿用先前优先级，保留来源，不改变事实状态。"
  },
  {
    "id": "RQ12",
    "priority": "P2",
    "status": "OPEN",
    "title": "是否存在遮挡的额外加粉",
    "question": "当前仅计两次可见入混合容器；若有连续证据再修订，不能预先添加第三次。",
    "time_ranges": [
      {
        "start_sec": 283,
        "end_sec": 292,
        "start_hms": "00:04:43.000",
        "end_hms": "00:04:52.000"
      },
      {
        "start_sec": 595,
        "end_sec": 604,
        "start_hms": "00:09:55.000",
        "end_hms": "00:10:04.000"
      }
    ],
    "event_ids": [
      "E051"
    ],
    "object_ids": [
      "O01",
      "O08",
      "O15"
    ],
    "ego_mc_record_ids": [
      "R26",
      "R49"
    ],
    "targets": [
      {
        "artifact": "events",
        "record_id": "E051",
        "field": "facts/additional_hidden_flour_addition"
      },
      {
        "artifact": "events",
        "record_id": "E051",
        "field": "facts/supplement_intent"
      }
    ],
    "evidence_ids": [
      "V-E051-01",
      "V-E051-02",
      "I-E051-02",
      "T-R49",
      "T-R26"
    ],
    "sources": [
      {
        "path": "annotation_reports/consistency_revision.md",
        "section": "4"
      }
    ],
    "review_method": "人工查看连续视频/高清局部并记录裁决；若仍无证据则保留UNCERTAIN。",
    "priority_notes": "优先采用第四轮D节明确片段清单；未覆盖问题沿用先前优先级，保留来源，不改变事实状态。"
  }
]
```

## 时间覆盖、桥接与技术校验

16个连续片段，29帧导航，42条原子项；431项结构/来源/截止/完整性检查PASS。

桥接详见manifest.continuity_gaps_and_bridges；uncovered_media_intervals为空只说明提取不漏段。observed_occlusion_intervals=null，表示未由Codex裁决视频遮挡；不是全程无遮挡结论。

阅读来源与SHA-256（生成前后未变）：

| 来源 | SHA-256 |
|---|---|
| golden_episode/GX010021/source/annotations.json | 88183e371dac0948378b723aa4c2ca102a2597770ed518805d52f180cd780527 |
| golden_episode/GX010021/source/GX010021.MP4 | fe4a11550bf2aea09a39ce1e72dba4633adc8c8b6a540e9894696e8b2ed1c8f9 |
| golden_episode/GX010021/annotations/events.json | e4e69cab21f6ee78a2f3253c7491a06ba773663660fb386d52b3acd5573c4ce2 |
| golden_episode/GX010021/annotations/objects.json | 6ab89d92d291f2dcd92d3eb821a2db4435eb2a84fa7e8effddd266d34b5fe42e |
| golden_episode/GX010021/annotations/review_queue.json | 0aa8ae4dcf195f022e9d5a38abe3b9c8c0ccdd44fe854c729b938f1cb06876e5 |
| golden_episode/GX010021/annotations/schema.json | 674a6727ac01456e0166f7fd32565f2e739527ace53a1a08460a3fbfdcd20ecb |
| golden_episode/GX010021/tasks/pilot_task_candidates.json | 58385dde24086f21404215449e644b90894ea8c226070af79122bed7f4c2705f |
| golden_episode/GX010021/annotation_reports/candidate_events_v1.md | d902836c5f22515682189559348f052853a7fa5c6aac2f8ebd779e41b88a43c4 |
| golden_episode/GX010021/annotation_reports/consistency_revision.md | 4d37d9b5d40374b1a32cb95cbacdccc5b26766b82eb00cf81451ad7228a0e2e7 |
| golden_episode/GX010021/annotation_reports/crosscheck_report.md | 5d0cab2dcf558cbd0ce92061a9bd91f9fdef7aa55c935a447208be9452d58026 |
| golden_episode/GX010021/annotation_reports/README.md | e028a30799080dda38ef369376631496e4626ac982636873a7dc508df845d31f |
| golden_episode/GX010021/annotation_reports/verification_report.md | 76128353fc3168eac4f358a0d29067c3f614bbe3640caac8c040f51eae4a63d5 |
| golden_episode/GX010021/reports/annotation_gaps.md | a59453a044aff98daa8d05d94c729aafd060eff436fbb0404373446702871dd5 |
| golden_episode/GX010021/reports/merge_report.md | 585f766b08edc64425dfa26279fb91e2a32c452bb6f7d4d6048dd49b3b4dba9e |
| golden_episode/GX010021/reports/task_generation_report.md | 0c95fb34eb92341e99a9866113ef96ff8b8f6e5feef22efcfe2cbc37ac289b4a |
| golden_episode/GX010021/reports/track_feasibility.md | 6064710cdd88b66beeccdd56c9f6084fc32771e81e0f90bc9e4e57ee493b250b |
| golden_episode/GX010021/reports/validation_results.json | 4cbd67918d4b98a34a60d75a7f304e141c52a863430e6079595af69fa152d17d |
| docs/Long_Horizon_Streaming_Agent_Benchmark_Overall_Design_v1.0 (1).md | 260908d8bab250d53bc27b13da48e74ffa22f9d7aa24f88470396f0361007cb0 |
