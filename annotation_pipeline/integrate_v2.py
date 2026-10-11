"""Offline candidate integration. No API calls, tasks, runner, or evaluator."""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
from .common import ROOT, PACKAGE, digest, file_hash, read_json
from .full_video import load_full_config, usage_summary
from .normalize_full_video import normalize

EPISODE = ROOT / "golden_episode/GX010021"
OUTPUT = EPISODE / "annotations/v2_video_model"
RUN = OUTPUT / "runs/session2-full-video"

def save(name, value):
    (OUTPUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")

def source_ref(source, pointer):
    return {"source_id": source, "json_pointer": pointer}

def base(rid, kind, refs, evidence=()):
    return {"id": rid, "annotation_status": "CANDIDATE", "source_type": kind,
            "source_refs": refs, "evidence_refs": list(evidence), "confirmation_status": "UNCONFIRMED"}

def run():
    raw_global = read_json(RUN / "seg-focused/global_analysis.json")
    global_data, repairs = normalize(raw_global)
    if read_json(OUTPUT / "global_analysis.json") != global_data:
        raise ValueError("Independent canonical output differs from deterministic normalization")
    v1 = read_json(EPISODE / "annotations/v1_candidate/events.json")
    old_objects = read_json(EPISODE / "annotations/v1_candidate/objects.json")
    text = read_json(EPISODE / "source/annotations.json")
    decisions = read_json(PACKAGE / "session2_integration_decisions.json")
    local = read_json(RUN / "local_visual_checks/manifest.json")
    config = load_full_config(PACKAGE / "config.full_video.yaml")
    trace = read_json(RUN / "seg-focused/request.json")
    media = trace["media"]
    aliases = decisions["duplicate_event_aliases"]
    def eid(x):
        return "V2-" + aliases.get(x, x)
    def oid(x):
        return "V2-" + x
    historical_event_map = {d["v1_event_id"]: list(dict.fromkeys(eid(e) for e in d["model_event_ids"]))
                            for d in decisions["crosscheck"]}
    def heid(x):
        ids = historical_event_map[x]
        return ids[0] if ids else "H1-" + x
    object_map = {k: [oid(x) for x in v] for k, v in decisions["object_correspondences"].items()}
    def hoid(x):
        ids = object_map[x]
        return ids[0] if len(ids) == 1 else "H1-" + x
    evidence_records = []
    for i, e in enumerate(global_data["evidence"]):
        evidence_records.append(base("V2-" + e["evidence_id"], "video_model",
            [source_ref("independent", "/evidence/" + str(i))]) | {k: e[k] for k in ("start_time", "end_time", "description", "observability")}
            | {"locator_precision": "MODEL_APPROXIMATE_RANGE", "source_media_sha256": media["sha256"], "server_sample_pts_known": False})
    for i, e in enumerate(v1["evidence"]):
        time = e.get("time")
        if time is None:
            continue
        evidence_records.append(base("H1-" + e["id"], "historical_candidate", [source_ref("v1_events", "/evidence/" + str(i))])
            | {"start_time": time["start_sec"], "end_time": time["end_sec"], "description": e["description"],
               "observability": "historical_report_only", "original_kind": e["kind"], "original_grade": e.get("grade"),
               "locator_precision": "HISTORICAL_UNVERIFIED", "source_media_sha256": media["sha256"]})
    for i, e in enumerate(local["records"]):
        evidence_records.append(base(e["id"], "integration_candidate", [source_ref("local_checks", "/records/" + str(i))])
            | {"start_time": e["source_time"], "end_time": e["source_time"], "description": e["observation"],
               "observability": "direct_visual_snapshot", "frame_path": e["path"], "frame_sha256": e["sha256"],
               "source_pts": e["source_pts"], "time_base": e["time_base"], "locator_precision": "VERIFIED_SINGLE_FRAME_PTS",
               "source_media_sha256": media["sha256"], "observer": "assistant_visual_inspection"})
    evidence_ids = {e["id"] for e in evidence_records}
    def historical_evidence(refs):
        return ["H1-" + e for e in refs if "H1-" + e in evidence_ids]
    event_records = []
    replacements = {"E2": "从蛋盒取出鸡蛋（累计数量未知）", "E4": "在容器边缘操作后续鸡蛋（第三枚是否倒入未知）",
                    "E7": "在牛奶盒与黑色量具之间量取/转移液体", "E19": "加热后取出玻璃容器（次数、完全融化主张有分歧）",
                    "E20": "用黑色工具搅动黄色固液混合物", "E36": "拿取/移动打蛋器",
                    "E44": "85–88秒台面附近物体操作候选（动作与对象未确认）",
                    "E45": "末段黑色工具位置候选（放台面动作未确认）"}
    for i, event in enumerate(global_data["events"]):
        original_id = event["event_id"]
        if original_id in aliases:
            continue
        raw = {k: v for k, v in event.items() if k != "event_id"}
        refs = [source_ref("independent", "/events/" + str(i))]
        dup_ids = [k for k, v in aliases.items() if v == original_id]
        for dup in dup_ids:
            refs.append(source_ref("independent", "/events/" + str(next(n for n, e in enumerate(global_data["events"]) if e["event_id"] == dup))))
        comparisons = [d for d in decisions["crosscheck"] if original_id in [aliases.get(x, x) for x in d["model_event_ids"]]]
        v1refs = [source_ref("v1_events", "/events/" + str(next(n for n, e in enumerate(v1["events"]) if e["id"] == d["v1_event_id"]))) for d in comparisons]
        row = base(eid(original_id), "video_model", refs + v1refs, ["V2-" + e for e in event["evidence_refs"]])
        row |= raw | {"objects": [oid(x) for x in event["objects"]], "evidence_refs": row["evidence_refs"],
                      "model_event_ids": [original_id] + dup_ids, "historical_event_ids": [d["v1_event_id"] for d in comparisons],
                      "time_precision": "MODEL_APPROXIMATE", "model_claim": event, "crosscheck_categories": sorted({d["category"] for d in comparisons}),
                      "interpretation_status": "MODEL_CANDIDATE", "interval_coverage_is_unverified": True}
        caveat = decisions["model_event_caveats"].get(original_id)
        if caveat:
            row["uncertainties"] = row["uncertainties"] + [caveat]
            row["interpretation_status"] = "DISPUTED_OR_EVIDENCE_GAP"
            row["confidence"] = None
            row["evidence_sufficient_time"] = None
        if original_id in replacements:
            row["action"] = replacements[original_id]
            row["source_type"] = "integration_candidate"
            row["execution_status"] = "uncertain" if original_id in ("E4", "E44", "E45") else event["execution_status"]
        if original_id == "E4":
            row["evidence_refs"] += ["LC-76-2", "LC-83-2"]
        if original_id in ("E19", "E20"):
            row["evidence_refs"].append("LC-431-2" if original_id == "E19" else "LC-445-2")
        if original_id == "E45":
            row["evidence_refs"].append("LC-680-2")
        if original_id in ("E4", "E19", "E20", "E45"):
            for ev in row["evidence_refs"]:
                if ev.startswith("LC-"):
                    ix = next(n for n, c in enumerate(local["records"]) if c["id"] == ev)
                    row["source_refs"].append(source_ref("local_checks", "/records/" + str(ix)))
        event_records.append(row)
    for i, e in enumerate(v1["events"]):
        if historical_event_map[e["id"]]:
            continue
        row = base("H1-" + e["id"], "historical_candidate", [source_ref("v1_events", "/events/" + str(i))], historical_evidence(e["evidence_ids"]))
        row |= {"action": e["action"], "actor": e["actor"], "objects": [hoid(x) for x in e["object_ids"]],
                "start_time": e["time"]["start_sec"], "end_time": e["time"]["end_sec"], "evidence_sufficient_time": None,
                "observability": "historical_report_only", "confidence": None, "execution_status": "uncertain",
                "time_precision": "HISTORICAL_APPROXIMATE", "historical_event_ids": [e["id"]],
                "description": e["description"], "historical_facts": e["facts"],
                "uncertainties": ["未在独立全片模型中单独表示；历史候选未自动成为新视觉事实。"]}
        if e["id"] in ("E051", "E052"):
            ev = "LC-599-2" if e["id"] == "E051" else "LC-610-2"
            row["evidence_refs"].append(ev)
            row["source_refs"].append(source_ref("local_checks", "/records/" + str(next(n for n, c in enumerate(local["records"]) if c["id"] == ev))))
            row["source_type"] = "integration_candidate"
            row["observability"] = "partial_visual_snapshot_plus_historical_candidate"
            row["uncertainties"].append("局部单帧佐证此动作阶段，未验证历史完整起止。")
        event_records.append(row)
    event_records.sort(key=lambda e: (e["start_time"] is None, e["start_time"] or 0, e["id"]))
    object_records = []
    for i, o in enumerate(global_data["objects"]):
        refs = [source_ref("independent", "/objects/" + str(i))]
        matching = [k for k, ids in object_map.items() if oid(o["object_id"]) in ids]
        refs += [source_ref("v1_objects", "/objects/" + str(next(n for n, x in enumerate(old_objects["objects"]) if x["id"] == k))) for k in matching]
        row = base(oid(o["object_id"]), "video_model", refs, ["V2-" + e for e in o["evidence_refs"]])
        row |= {k: v for k, v in o.items() if k not in ("object_id", "evidence_refs")}
        row |= {"historical_object_ids": matching, "identity_status": "uncertain", "model_identity_status": o["identity_status"],
                "identity_interpretation": "CANDIDATE_CORRESPONDENCE; disjoint sampled observations do not establish uninterrupted physical identity",
                "occlusion_and_out_of_frame": "NOT_EXHAUSTIVELY_ANNOTATED", "model_claim": o}
        row["uncertainties"] += ["连续身份仅为候选；出画及遮挡期间不能断言状态持续。"]
        if o["object_id"] == "O5":
            row["uncertainties"].append("首轮Half & Half与专题Whole Milk标签描述不一致，产品名仅为模型候选。")
        if o["object_id"] in ("O13", "O14"):
            row["uncertainties"].append("黑色量具/黑色搅动与刮糊工具不能凭相似外观强行确认同一件。")
        if o["object_id"] == "O8":
            row["label"] = "黄油包装及黄色材料的模型观察组"
            row["uncertainties"].append("原模型把包装和黄油材料合在同一ID；不得将两者物理身份等同。")
        object_records.append(row)
    for i, o in enumerate(old_objects["objects"]):
        if len(object_map[o["id"]]) == 1:
            continue
        row = base("H1-" + o["id"], "historical_candidate", [source_ref("v1_objects", "/objects/" + str(i))])
        row |= {"label": o["name"], "summary": o["summary"], "identity_status": "uncertain",
                "historical_object_ids": [o["id"]], "corresponding_model_object_ids": object_map[o["id"]],
                "uncertainties": ["历史材料/观察指称或组实体；未与新对象自动确认物理同一性。"]}
        object_records.append(row)
    states = []
    for i, s in enumerate(global_data["states"]):
        row = base("V2-" + s["state_id"], "video_model", [source_ref("independent", "/states/" + str(i))], ["V2-" + e for e in s["evidence_refs"]])
        row |= {k: v for k, v in s.items() if k not in ("state_id", "evidence_refs")}
        row |= {"object_id": oid(s["object_id"]), "transition_event_id": eid(s["transition_event_id"]) if s["transition_event_id"] else None,
                "valid_from": None, "valid_to": None, "model_claimed_interval": {"start_time": s["valid_from"], "end_time": s["valid_to"]},
                "validity_status": "UNVERIFIED_INTERVAL; event-driven claim only", "model_claim": s}
        row["uncertainties"] += ["模型给出的连续有效区间尚未被持续视觉跟踪核实，最终有效边界保留null。"]
        if s["state_id"] in ("ST2", "ST9"):
            row["value"] = "UNKNOWN: disputed count" if s["state_id"] == "ST2" else "UNKNOWN: full melting not established"
            row["confidence"] = None
            row["observability"] = "inference"
            row["uncertainties"].append("三蛋黄/完全融化的模型断言与局部图像冲突，不用于确定事实。")
        if s["state_id"] in ("ST4", "ST5", "ST6"):
            row["observability"] = "inference"
            row["uncertainties"].append("混合物材料成分来自跨事件谱系推断，当前画面不能直接识别全部成分。")
        states.append(row)
    for i, o in enumerate(old_objects["objects"]):
        for j, s in enumerate(o["state_history"]):
            row = base("H1-" + s["id"], "historical_candidate", [source_ref("v1_objects", f"/objects/{i}/state_history/{j}")], historical_evidence(s["evidence_ids"]))
            row |= {"object_id": hoid(o["id"]), "attribute": s["field"], "value": s["after"],
                    "before": s["before"], "valid_from": None, "valid_to": None,
                    "reported_observation_interval": {"start_time": s["time"]["start_sec"], "end_time": s["time"]["end_sec"]},
                    "transition_event_id": heid(s["event_id"]), "observability": "historical_report_only",
                    "confidence": None, "historical_status": s["status"], "uncertainties": [s["reason"], "历史观察区间不是已验证的状态持续区间。"]}
            states.append(row)
    snapshot_states = [("LC-15-2", "V2-O12", "display_text", "100"),
                       ("LC-76-2", "V2-O1", "visible_yolk_count", 2), ("LC-83-2", "V2-O1", "visible_yolk_count", 2),
                       ("LC-431-2", "V2-O9", "visible_phase", "yellow liquid plus pale solid block"),
                       ("LC-445-2", "V2-O9", "visible_phase", "liquid plus pale solid material"),
                       ("LC-599-2", "V2-O1", "visible_surface", "pale powder-like material under tilted brown paper bag"),
                       ("LC-610-2", "V2-O6", "location", "beaters inside main mixing container"),
                       ("LC-680-2", "V2-O10", "contents", "batter visible; transfer amount unknown")]
    for ev, object_id, attr, value in snapshot_states:
        n = next(i for i, c in enumerate(local["records"]) if c["id"] == ev)
        t = local["records"][n]["source_time"]
        states.append(base("STATE-" + ev, "integration_candidate", [source_ref("local_checks", "/records/" + str(n))], [ev])
            | {"object_id": object_id, "attribute": attr, "value": value, "valid_from": t, "valid_to": t,
               "transition_event_id": None, "observability": "direct_visual_snapshot", "confidence": None,
               "uncertainties": ["仅对应这一原始帧；不推定此前/此后状态或完整动作。"]})
    procedure = []
    for i, (word, kind, t) in enumerate(zip(text["texts"], text["text_types"], text["text_timestamps"])):
        row = base(f"SRC-R{i+1:02d}", "source_annotation_text", [source_ref("source_text", "/texts/" + str(i)),
                    source_ref("source_text", "/text_types/" + str(i)), source_ref("source_text", "/text_timestamps/" + str(i))])
        row |= {"text": word, "text_type": kind, "source_timestamp": t, "timestamp_semantics": "UNSPECIFIED_SINGLE_POINT_LABEL",
                "issued_at": None, "utterance_start": None, "utterance_end": None, "availability_time": None, "effective_from": None,
                "role": "normative_or_guidance_candidate" if kind in ("Instruction", "Instruction-Clarification", "Feedback") else "dialogue_context",
                "source_visibility": "EXTERNAL_ANNOTATION_ONLY; original video has no audio",
                "uncertainties": ["无法通过静音视频独立验证话语及其完整公开/生效时间。"]}
        procedure.append(row)
    observed_steps = []
    groups = [("control_panel", ["E31"], [1]), ("container_selection", ["E32", "E1"], [4,6]),
              ("egg_handling", ["E2", "E3", "E4"], [9]), ("sugar_transfer", ["E5", "E6"], [13,16]),
              ("milk_transfer", ["E7", "E8"], [18]), ("initial_mixing", ["E9", "E10"], [18,21]),
              ("initial_flour", ["E11", "E12", "E13"], [26]), ("heating_and_checking", ["E14", "E15", "E16", "E17", "E18", "E19", "E20"], [28,30,31]),
              ("butter_transfer_and_mixing", ["E21", "E22"], [33]), ("pan_liquid_treatment", ["E23", "E24", "E25"], [39,41,43]),
              ("late_powder_and_mixing", [], [48,49]), ("batter_transfer", ["E26", "E27"], [52]), ("oven_loading", ["E28", "E29", "E30"], [54])]
    for n, (label, events, rules) in enumerate(groups):
        event_ids = [eid(e) for e in events]
        if label == "late_powder_and_mixing":
            event_ids = ["H1-E051", "H1-E052"]
        evidence = list(dict.fromkeys(ev for e in event_records if e["id"] in event_ids for ev in e["evidence_refs"]))
        observed_steps.append(base("STEP-" + str(n+1).zfill(2), "integration_candidate",
            [source_ref("independent", "/events"), source_ref("decisions", "/crosscheck")], evidence)
            | {"label": label, "event_ids": event_ids, "normative_refs": [f"SRC-R{r:02d}" for r in rules],
               "factual_progress": "OBSERVED_ACTION_CANDIDATES", "normative_completion": "UNKNOWN",
               "completion_time": None, "cancellation_time": None, "uncertainties": ["动作候选不等于规范完成或生效；精确步骤边界未审定。"]})
    relations = []
    for i, r in enumerate(global_data["relations"]):
        if r["from_id"] == r["to_id"]:
            continue
        refs = [source_ref("independent", "/relations/" + str(i))]
        row = base("V2-" + r["relation_id"], "video_model", refs, ["V2-" + e for e in r["evidence_refs"]])
        row |= {k: v for k, v in r.items() if k not in ("relation_id", "evidence_refs")}
        row |= {"from_id": oid(r["from_id"]) if r["from_id"].startswith("O") else eid(r["from_id"]),
                "to_id": oid(r["to_id"]) if r["to_id"].startswith("O") else eid(r["to_id"]),
                "event_ids": list(dict.fromkeys(eid(e) for e in r["event_ids"])),
                "basis": "MODEL_VISUAL_CHAIN_CANDIDATE", "model_claim": r, "evidence_available_from": None}
        row["uncertainties"] += ["关系仅为候选；不能由时序先后转换为必然前置依赖。"]
        if r["type"] == "uses_output_of":
            row["observability"] = "inference"
            row["uncertainties"].append("跨阶段材料连续性为推断，不声称遮挡期间完整身份跟踪。")
        relations.append(row)
    # Intermediate cup paths and later powder transfer: historical candidate evidence is explicit.
    material_paths = [("O04","O05","E016"), ("O05","O01","E018"), ("O06","O05","E022"), ("O05","O01","E023"),
                      ("O08","O05","E031"), ("O05","O01","E032"), ("O08","O01","E051")]
    for n, (a,b,event) in enumerate(material_paths):
        i = next(i for i,e in enumerate(v1["events"]) if e["id"] == event)
        evidence = historical_evidence(v1["events"][i]["evidence_ids"])
        if event == "E051":
            evidence.append("LC-599-2")
        relations.append(base("PATH-" + str(n+1).zfill(2), "integration_candidate", [source_ref("v1_events", "/events/" + str(i))], evidence)
            | {"type": "material_transferred_to", "from_id": hoid(a), "to_id": hoid(b), "event_ids": [heid(event)],
               "basis": "HISTORICAL_VISUAL_CANDIDATE_WITH_SOURCE_POINTER", "material_identity": "CANDIDATE",
               "evidence_available_from": None, "uncertainties": ["对象对应为候选；各阶段黑色量杯不得自动确认为同一只，实际材料体积未知。"]})
    rule_chains = [(13,16,[13,14,15,16],"sugar amount in this dialogue", "Explicit proceed-with-quarter-cup wording; source time is not release time"),
                   (39,41,[38,39,40,41],"lining this baking pan", "No parchment paper is a speaker claim, not an inventory measurement"),
                   (41,43,[40,41,42,43],"lining this baking pan only", "Oil permission applies to this pan context; no general recipe substitution")]
    for n, (a,b,context,scope,note) in enumerate(rule_chains):
        relations.append(base("RULE-" + str(n+1).zfill(2), "source_annotation_text", [source_ref("source_text", "/texts/" + str(r-1)) for r in context])
            | {"type": "rule_supersedes", "from_id": f"SRC-R{a:02d}", "to_id": f"SRC-R{b:02d}", "event_ids": [],
               "basis": "EXPLICIT_TEXT_AND_DIALOGUE_CONTEXT_CANDIDATE", "scope": scope, "condition": note,
               "effective_from": None, "evidence_available_from": None, "applicability": "UNCONFIRMED_ONLINE_TIMING",
               "uncertainties": ["替代关系为限定语境候选；标签本身不证明替代，公开/生效时间仍未知。"]})
    anomalies = []
    incident_specs = [("small_bowl_feedback",[4,6], [eid("E32"),eid("E1")], "容器过小只有文本反馈，缺独立容量/提前可检测规则。"),
                      ("extra_egg_feedback",[9,10,11], [eid("E2"),eid("E4")], "取蛋与实际加入不同；局部两蛋黄不能构成第三枚未破损真值或三蛋入料错误。"),
                      ("sugar_amount_feedback",[13,14,15,16], [eid("E5"),eid("E6")], "实际量不可测，且存在修订许可；不能由反馈时间生成异常时刻。"),
                      ("butter_reheat",[28,30,31], [eid("E17"),eid("E18"),eid("E19")], "部分融化与再次加热可能属于分段检查流程，不证明操作错误。"),
                      ("late_flour_addition",[47,48,49], ["H1-E051","H1-E052"], "不必加不等于禁止加；稀稠条件与实际量未知，不构成已确认违例。"),
                      ("permitted_oil_normal_candidate",[39,40,41,42,43], [eid("E24"),eid("E25")], "仅限定垫纸/黄油被允许用油替代的候选负例，不证明全区间没有其他错误。"),
                      ("reheat_normal_candidate",[30,31], [eid("E17"),eid("E18")], "分段加热检查的正常流程候选，非错误修复真值。") ]
    for n, (label, rules, events, note) in enumerate(incident_specs):
        evidence = list(dict.fromkeys(ev for e in event_records if e["id"] in events for ev in e["evidence_refs"]))
        anomalies.append(base("L5-" + str(n+1).zfill(2), "integration_candidate", [source_ref("source_text", "/texts/" + str(r-1)) for r in rules], evidence)
            | {"label": label, "candidate_kind": "NORMAL_OPERATION_CANDIDATE" if "normal_candidate" in label else "UNCONFIRMED_DEVIATION_OR_FEEDBACK",
               "normative_refs": [f"SRC-R{r:02d}" for r in rules], "related_event_ids": events,
               "error_onset": None, "detectable_from": None, "deadline": None, "resolved_at": None, "feedback_given_at": None,
               "alarm_ground_truth": False, "hard_scoring_eligible": False, "uncertainties": [note, "规范公开/生效时间缺失，不构成在线可检测错误。"],
               "candidate_observation_interval": {"start_time": 560, "end_time": 581} if label == "permitted_oil_normal_candidate" else None})
    comparisons = []
    for d in decisions["crosscheck"]:
        comparisons.append({k:v for k,v in d.items() if k != "model_event_ids"} |
                           {"v2_event_ids": historical_event_map[d["v1_event_id"]], "historical_candidate_retained_as": heid(d["v1_event_id"])})
    cross = {"annotation_status": "CANDIDATE", "method": "explicit semantic/time correspondence, not overlap-only matching",
             "v1_event_comparisons": comparisons, "category_counts": dict(Counter(d["category"] for d in comparisons)),
             "new_model_primary_event_ids": [e["id"] for e in event_records if e["id"].startswith("V2-") and not e["historical_event_ids"]],
             "novel_physical_actions_confirmed": 0, "model_granularity_refinements_are_not_new_physical_actions": True,
             "object_correspondences": [{"v1_object_id": k, "v2_object_ids": v, "identity_confirmed": False} for k,v in object_map.items()],
             "duplicate_aliases": [{"raw_event_id": k, "canonical_event_id": eid(v), "source_id": "independent"} for k,v in aliases.items()],
             "object_attribute_conflicts": [
                 {"topic": "milk_label", "risk": "MEDIUM", "note": "First pass calls carton Half & Half; focused calls Whole Milk; historical branding is uncertain. Exact product identity is not promoted."},
                 {"topic": "cup_capacity", "risk": "HIGH", "note": "First pass says standard half cup; V1 has a quarter-cup label on an earlier view. Cup continuity and actual quantities unknown."},
                 {"topic": "tool_identity", "risk": "HIGH", "note": "Focused combines butter stirring and batter scraping in O14; V1 observation labels remain unresolved, no confirmed same-object relation."},
                 {"topic": "butter_packaging_vs_material", "risk": "MEDIUM", "note": "Focused O8 covers wrapper and material; unified ID is an observation group, not one physical entity."}],
             "global_first_pass_semantic_errors_retained": ["350F display", "three cracked eggs", "completely melted butter", "missing late flour and third mixing"],
             "remaining_high_risk_gaps": ["third egg integrity/destination", "cup capacity and identity", "sugar transfer time",
                 "microwave exact duration", "butter solid phase at actual pour", "pan inner-wall coating", "tool identity",
                 "full-video missed late powder/mixing", "normative publication/effective timing"]}
    save("evidence_index.json", {"annotation_status": "CANDIDATE", "records": evidence_records})
    save("events.json", {"annotation_status": "CANDIDATE", "schema_version": "unified-candidate-v0.1", "records": event_records,
                         "historical_event_ids": [e["id"] for e in v1["events"]], "count_semantics": "39 deduplicated model records plus historical-only candidates; not a count of verified unique physical actions"})
    save("objects.json", {"annotation_status": "CANDIDATE", "records": object_records, "states": states,
                          "count_semantics": "observation IDs/material/group IDs; not verified physical-entity count"})
    save("procedure.json", {"annotation_status": "CANDIDATE", "records": procedure, "observed_steps": observed_steps,
                            "normative_actual_separation": True, "full_instruction_availability_known": False})
    save("relations.json", {"annotation_status": "CANDIDATE", "records": relations, "edge_direction": "from source/output/earlier rule to destination/consumer/later rule",
                            "mandatory_dependencies_confirmed": 0})
    save("anomaly_candidates.json", {"annotation_status": "CANDIDATE", "records": anomalies, "confirmed_error_count": 0,
                                     "confirmed_normal_episode": False, "alarm_ground_truth_count": 0})
    save("crosscheck.json", cross)
    source_specs = [("independent",OUTPUT / "global_analysis.json"), ("first_raw_candidate",RUN / "seg-global/global_analysis.json"),
                    ("focused_raw_candidate", RUN / "seg-focused/global_analysis.json"), ("v1_events",EPISODE / "annotations/v1_candidate/events.json"),
                    ("v1_objects",EPISODE / "annotations/v1_candidate/objects.json"), ("source_text",EPISODE / "source/annotations.json"),
                    ("local_checks",RUN / "local_visual_checks/manifest.json"), ("decisions",PACKAGE / "session2_integration_decisions.json")]
    stats = {"independent_model_records": len(global_data["events"]), "deduplicated_model_records": len(global_data["events"])-len(aliases),
             "unified_event_candidates": len(event_records), "historical_only_events": sum(not ids for ids in historical_event_map.values()),
             "objects_or_observation_groups": len(object_records), "model_states": len(global_data["states"]),
             "historical_state_claims": sum(len(o["state_history"]) for o in old_objects["objects"]), "snapshot_states": len(snapshot_states),
             "unified_states": len(states), "source_text_records": len(procedure), "observed_step_candidates": len(observed_steps),
             "relations": len(relations), "evidence_locators": len(evidence_records), "L5_candidates": len(anomalies),
             "confirmed_errors": 0, "gold_records": 0, "crosscheck_categories": cross["category_counts"]}
    manifest = {"episode_id": "GX010021", "version": "session2-v2.0-candidate", "annotation_status": "CANDIDATE",
                "date": "2026-10-10", "timezone": "Asia/Shanghai", "human_review": "NOT_REVIEWED", "semantic_truth_verified": False,
                "media": {k: media[k] for k in ("duration_sec","fps","fps_rational","width","height","has_audio","sha256","size_bytes")} |
                         {"source_path": "golden_episode/GX010021/source/GX010021.MP4", "full_decode_check": "PASS", "time_basis": "original_mp4_seconds"},
                "model": {"requested": config["model"], "version": config["model_version"], "returned_model": None,
                          "returned_model_note": "Native response contains no model field; requested alias does not pin weights",
                          "prompt_version": trace["prompt_version"], "sample_fps": config["sample_fps"], "max_pixels": config["video_max_pixels"],
                          "max_output_tokens": config["max_output_tokens"], "input_mode": "native_original_video_file", "sample_pts_known": False},
                "independent_raw_response_ref": (RUN / "seg-focused/attempt-000.response.json").relative_to(ROOT).as_posix(),
                "normalization_report_ref": (RUN / "normalization_report.json").relative_to(ROOT).as_posix(),
                "independent_passes": [{"pass_id": p, "raw_candidate": (RUN / f"seg-{p}/global_analysis.json").relative_to(ROOT).as_posix(),
                    "request_ref": (RUN / f"seg-{p}/request.json").relative_to(ROOT).as_posix(),
                    "response_ref": (RUN / f"seg-{p}/attempt-000.response.json").relative_to(ROOT).as_posix(),
                    "request_sha256": read_json(RUN / f"seg-{p}/request.json")["request_sha256"],
                    "raw_response_sha256": file_hash(RUN / f"seg-{p}/attempt-000.response.json")} for p in ("global","focused")],
                "sources": [{"source_id": sid, "path": p.relative_to(ROOT).as_posix(), "sha256": file_hash(p)} for sid,p in source_specs],
                "usage": usage_summary(RUN, config), "statistics": stats, "artifacts": [],
                "layers": {"L0":"native media/source tracing", "L1":"55 source text records with unknown availability; 3 scoped revision candidates",
                           "L2":"deduplicated full-video candidates plus explicitly sourced historical omissions",
                           "L3":"event-driven candidate states, unknown continuous validity, 8 actual-frame snapshots",
                           "L4":"material/temporal/output links plus scoped text revision candidates",
                           "L5":"unconfirmed feedback/deviation and scoped normal candidates; zero alarm truth"},
                "track_support": {"T1":"partial; key actions/object changes available, exact boundaries and identity unresolved",
                                  "T2":"partial; material transfer and rule-context chains available, history necessity/effective times unresolved",
                                  "T3":"limited; no confirmed positive error, onset/detectability/recovery truth"},
                "budget_stop": "2/2 inference attempts, 0.90/1.00 CNY reserved; no third live call",
                "scope": "annotations only; no task generation, Runner, Evaluator, Baseline or other episode"}
    manifest["artifacts"] = [{"path": name, "sha256": file_hash(OUTPUT / name)} for name in
        ("global_analysis.json","evidence_index.json","events.json","objects.json","procedure.json","relations.json","anomaly_candidates.json","crosscheck.json")]
    # Preserve complete Session 2 tracing when the offline integration is rebuilt.
    intervals = sorted((e["start_time"], e["end_time"]) for e in global_data["evidence"])
    merged = []
    for start, end in intervals:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    locator_seconds = sum(end - start for start, end in merged)
    manifest["coverage"] = {
        "complete_original_mp4_submitted": True, "global_start_middle_end_described": True,
        "exact_server_frames_known": False, "model_evidence_interval_union_sec": locator_seconds,
        "model_evidence_locator_fraction": locator_seconds / media["duration_sec"],
        "last_model_evidence_end_sec": max(end for _, end in intervals),
        "detail_coverage_complete": False,
        "metric_note": "Locator interval fraction is not frame coverage, recall or verified truth coverage"}
    manifest["processing"] = {"initial_raw_candidate_validation_failures": 2, "http_failures": 0,
        "retries": 0, "structural_repairs_in_focused": len(repairs), "semantic_truth_verified": False}
    manifest["usage"]["estimation_note"] = "Beijing price tiers, no cache/free-quota discount; actual billed cost unknown"
    manifest["integration_code_sha256"] = file_hash(Path(__file__))
    manifest["validation_code_sha256"] = file_hash(PACKAGE / "validate_v2.py")
    for name in ("README.md", "full_video_report.md", "first_pass_diagnosis.md", "crosscheck_report.md",
                 "validation_report.json", "integrity_report.json", "test_report.json"):
        if (OUTPUT / name).exists():
            manifest["artifacts"].append({"path": name, "sha256": file_hash(OUTPUT / name)})
    save("annotation_manifest.json", manifest)
    return stats

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
