"""Structural/source/temporal validation for unified CANDIDATE annotations."""
from __future__ import annotations
import json
import jsonschema
from pathlib import Path
from .common import ROOT, file_hash, read_json
from .full_video import validate_global

OUTPUT = ROOT / "golden_episode/GX010021/annotations/v2_video_model"

def validate(directory=OUTPUT):
    manifest = read_json(directory / "annotation_manifest.json")
    if manifest["annotation_status"] != "CANDIDATE":
        raise ValueError("Unified annotations must remain CANDIDATE")
    duration = manifest["media"]["duration_sec"]
    video = ROOT / manifest["media"]["source_path"]
    if file_hash(video) != manifest["media"]["sha256"]:
        raise ValueError("Media hash mismatch")
    for ref in manifest["sources"]:
        p = (ROOT / ref["path"]).resolve()
        if not p.is_relative_to(ROOT) or file_hash(p) != ref["sha256"]:
            raise ValueError("Source path/hash mismatch")
    independent = read_json(directory / "global_analysis.json")
    raw = read_json(ROOT / manifest["independent_raw_response_ref"])
    from .providers.qwen_native import QwenNativeProvider
    content, metadata = QwenNativeProvider({}).extract_content(raw["body"])
    from .normalize_full_video import normalize
    normalized, repairs = normalize(json.loads(content))
    if independent != normalized or metadata["finish_reason"] != "stop":
        raise ValueError("Independent output differs from raw model response")
    independent_result = validate_global(independent, duration)
    entities = {}; evidence = {}
    containers = {name: read_json(directory / (name + ".json")) for name in
                  ("events", "objects", "procedure", "relations", "anomaly_candidates")}
    for name, doc in containers.items():
        jsonschema.Draft202012Validator(read_json(ROOT / "annotation_pipeline/schemas/unified_candidate.schema.json")).validate(doc)
        if doc["annotation_status"] != "CANDIDATE":
            raise ValueError("File maturity mismatch")
        for row in doc["records"] + (doc.get("states", []) if name == "objects" else doc.get("observed_steps", []) if name == "procedure" else []):
            rid = row["id"]
            if rid in entities or row["annotation_status"] != "CANDIDATE":
                raise ValueError("Duplicate ID or promoted record")
            entities[rid] = row
            if not row["source_refs"]:
                raise ValueError("Missing source provenance")
            for ref in row["source_refs"]:
                if ref["source_id"] not in {s["source_id"] for s in manifest["sources"]}:
                    raise ValueError("Unknown source")
                docsource = read_json(ROOT / next(s["path"] for s in manifest["sources"] if s["source_id"] == ref["source_id"]))
                target = docsource
                for bit in ref["json_pointer"].strip("/").split("/") if ref["json_pointer"] else []:
                    bit = bit.replace("~1", "/").replace("~0", "~")
                    target = target[int(bit)] if isinstance(target, list) else target[bit]
            for field in ("start_time", "end_time", "valid_from", "valid_to", "evidence_sufficient_time", "source_timestamp"):
                t = row.get(field)
                if t is not None and (isinstance(t, bool) or not isinstance(t, (int, float)) or not 0 <= t <= duration):
                    raise ValueError("Time outside media")
            a, b = row.get("start_time", row.get("valid_from")), row.get("end_time", row.get("valid_to"))
            if a is not None and b is not None and a > b:
                raise ValueError("Reversed interval")
    evdoc = read_json(directory / "evidence_index.json")
    for row in evdoc["records"]:
        if row["id"] in evidence or not 0 <= row["start_time"] <= row["end_time"] <= duration:
            raise ValueError("Invalid evidence interval or duplicate ID")
        evidence[row["id"]] = row
    def check_row(row):
        for field in ("objects", "event_ids", "related_event_ids", "normative_refs"):
            if any(ref not in entities for ref in row.get(field, [])):
                raise ValueError("Unknown entity reference")
        for field in ("object_id", "transition_event_id", "from_id", "to_id"):
            if row.get(field) is not None and row[field] not in entities:
                raise ValueError("Unknown relation/state reference")
        if any(ref not in evidence for ref in row.get("evidence_refs", [])):
            raise ValueError("Unknown evidence reference")
        if row.get("source_type") == "video_model" and not row.get("evidence_refs"):
            raise ValueError("Video fact has no evidence")
        if row.get("evidence_sufficient_time") is not None:
            if row["evidence_sufficient_time"] < max(evidence[e]["end_time"] for e in row["evidence_refs"]):
                raise ValueError("Future evidence used")
        if row.get("source_type") == "source_annotation_text":
            if row.get("effective_from") is not None or row.get("issued_at") is not None:
                raise ValueError("Source single-point timestamp promoted to instruction visibility")
        if row.get("type") in ("requires_step_completed", "requires_object_state", "rule_supersedes") and row.get("basis") == "temporal_order_only":
            raise ValueError("Order alone cannot establish dependencies")
    for row in entities.values():
        check_row(row)
    for row in containers["objects"].get("states", []):
        if row["annotation_status"] != "CANDIDATE":
            raise ValueError("State maturity mismatch")
        check_row(row)
        for field in ("valid_from", "valid_to"):
            if row[field] is not None and not 0 <= row[field] <= duration:
                raise ValueError("State outside media")
        if row["valid_from"] is not None and row["valid_to"] is not None and row["valid_from"] > row["valid_to"]:
            raise ValueError("Reversed state interval")
        eid = row["transition_event_id"]
        if eid is not None:
            event = entities[eid]
            if row["valid_from"] is not None and event.get("start_time") is not None and row["valid_from"] < event["start_time"] - 2:
                raise ValueError("State precedes transition")
    for row in containers["anomaly_candidates"]["records"]:
        if row["confirmation_status"] != "UNCONFIRMED" or row["alarm_ground_truth"] is not False:
            raise ValueError("Unverified anomaly promoted to alarm truth")
        if any(row.get(k) is not None for k in ("detectable_from", "deadline", "resolved_at", "error_onset", "feedback_given_at")):
            raise ValueError("Unverified anomaly timing asserted")
    cross = read_json(directory / "crosscheck.json")
    v1ids = set(containers["events"]["historical_event_ids"])
    if {r["v1_event_id"] for r in cross["v1_event_comparisons"]} != v1ids:
        raise ValueError("Incomplete V1 comparison")
    if any(r not in entities for row in cross["v1_event_comparisons"] for r in row["v2_event_ids"]):
        raise ValueError("Invalid cross-check target")
    graph = {}
    for r in containers["relations"]["records"]:
        if r["type"] in ("temporal_precedes", "uses_output_of", "requires_step_completed", "rule_supersedes"):
            graph.setdefault(r["from_id"], []).append(r["to_id"])
        if r["type"] == "temporal_precedes":
            a, b = entities[r["from_id"]], entities[r["to_id"]]
            if a.get("start_time") is None or b.get("start_time") is None or a["start_time"] > b["start_time"]:
                raise ValueError("Invalid temporal precedence")
    visiting, visited = set(), set()
    def visit(node):
        if node in visiting:
            raise ValueError("Dependency/rule graph cycle")
        if node in visited:
            return
        visiting.add(node)
        for child in graph.get(node, []):
            visit(child)
        visiting.remove(node)
        visited.add(node)
    for node in graph:
        visit(node)
    for e in evidence.values():
        if e.get("frame_path"):
            p = (ROOT / e["frame_path"]).resolve()
            if not p.is_relative_to(directory.resolve()) or file_hash(p) != e["frame_sha256"]:
                raise ValueError("Snapshot frame hash/path mismatch")
            if abs(e["source_pts"] / 30000 - e["start_time"]) > 1e-6:
                raise ValueError("Snapshot PTS mapping mismatch")
    for artifact in manifest["artifacts"]:
        if file_hash(directory / artifact["path"]) != artifact["sha256"]:
            raise ValueError("Artifact hash mismatch")
    return {"status": "PASS", "annotation_status": "CANDIDATE", "semantic_truth_verified": False,
            "independent": independent_result, "entity_count": len(entities), "evidence_count": len(evidence),
            "checks": ["documented_normalization_of_raw_output", "source_and_artifact_hashes", "maturity", "time_bounds",
                       "all_entity_and_source_pointers", "state_transition_times", "no_future_evidence",
                       "normative_observation_separation", "no_unconfirmed_alarm_truth", "complete_V1_comparison", "temporal_relation_order", "acyclic_dependency_and_rule_graph"]}

if __name__ == "__main__":
    print(json.dumps(validate(), ensure_ascii=False, indent=2))
