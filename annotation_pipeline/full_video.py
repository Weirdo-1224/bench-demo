"""Full-video-first independent observation; historical inputs are excluded."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import re
import sys
from uuid import uuid4
from urllib.parse import urlsplit
import yaml
import jsonschema

from .common import PACKAGE, ROOT, digest, file_hash, load_api_key, project_path, read_json, write_new
from .calls import Blocked, call_or_reuse, ledger, utc_now
from .inspect_video import inspect_video
from .providers.qwen_native import QwenNativeProvider
from .normalize_full_video import normalize

SCHEMA = PACKAGE / "schemas/full_video.schema.json"
PROMPT = PACKAGE / "prompts/full_video_observation.md"


def load_full_config(path):
    defaults = yaml.safe_load((PACKAGE / "config.full_video.yaml").read_text(encoding="utf-8"))
    supplied = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(supplied, dict) or set(supplied) - set(defaults):
        raise ValueError("Unknown full-video configuration field")
    config = defaults | supplied
    if config["mode"] != "full_video" or config["episode_id"] != "GX010021" or config["provider"] != "qwen":
        raise ValueError("Session 2 scope is GX010021 full_video with Qwen")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", config["api_key_env"]):
        raise ValueError("api_key_env must be an environment variable NAME")
    url = urlsplit(config["endpoint"])
    if url.scheme != "https" or not url.hostname or url.username or url.password or url.query or url.fragment:
        raise ValueError("Unsafe native endpoint")
    if project_path(config["video_path"]) != ROOT / "golden_episode/GX010021/source/GX010021.MP4":
        raise ValueError("Only the original MP4 is allowed")
    if project_path(config["output_dir"]) != ROOT / "golden_episode/GX010021/annotations/v2_video_model/runs":
        raise ValueError("Output must stay in V2 runs")
    for name in ("sample_fps", "video_max_pixels", "max_video_bytes", "max_video_duration_sec",
                 "max_context_tokens", "max_input_tokens_estimate", "max_output_tokens", "timeout_sec",
                 "max_api_calls", "max_cost", "cost_reserve_per_call", "media_timeout_sec"):
        v = config[name]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0:
            raise ValueError("Invalid " + name)
    if not 0.1 <= config["sample_fps"] <= 10 or config["max_output_tokens"] > 32768:
        raise ValueError("FPS/output exceeds supported limits")
    for name in ("video_max_pixels", "max_video_bytes", "max_context_tokens", "max_input_tokens_estimate", "max_output_tokens", "max_api_calls"):
        if type(config[name]) is not int:
            raise ValueError("Integer required for " + name)
    if config["max_retries"] != 0:
        raise ValueError("Full-video calls have no automatic retry")
    for name in ("input_cost_per_million", "output_cost_per_million"):
        if not isinstance(config[name], (int, float)) or not math.isfinite(config[name]) or config[name] < 0:
            raise ValueError("Invalid configured rate")
    return config


def validate_global(value, duration):
    jsonschema.Draft202012Validator(read_json(SCHEMA)).validate(value)
    entities = {}
    for collection, field in (("stages", "stage_id"), ("evidence", "evidence_id"), ("objects", "object_id"),
                              ("events", "event_id"), ("states", "state_id"), ("relations", "relation_id")):
        for row in value[collection]:
            if row[field] in entities:
                raise ValueError("Duplicate entity ID")
            entities[row[field]] = collection
            for name in ("start_time", "end_time", "valid_from", "valid_to", "evidence_sufficient_time"):
                t = row.get(name)
                if t is not None and (not math.isfinite(t) or not 0 <= t <= duration):
                    raise ValueError("Time outside original media")
            a, b = row.get("start_time", row.get("valid_from")), row.get("end_time", row.get("valid_to"))
            if a is not None and b is not None and a > b:
                raise ValueError("Reversed interval")
    evidence = {r["evidence_id"]: r for r in value["evidence"]}
    events = {r["event_id"]: r for r in value["events"]}
    for collection in ("objects", "events", "states", "relations"):
        for row in value[collection]:
            if not row["evidence_refs"] or any(r not in evidence for r in row["evidence_refs"]):
                raise ValueError("Missing evidence reference")
            if collection == "events":
                if any(entities.get(r) != "objects" for r in row["objects"]):
                    raise ValueError("Unknown event object")
                t = row["evidence_sufficient_time"]
                if t is not None and t < max(evidence[r]["end_time"] for r in row["evidence_refs"]):
                    raise ValueError("Evidence sufficient time uses future evidence")
            if collection == "states":
                if entities.get(row["object_id"]) != "objects":
                    raise ValueError("Unknown state object")
                event_id = row["transition_event_id"]
                if event_id is not None:
                    if event_id not in events:
                        raise ValueError("Unknown state transition event")
                    e = events[event_id]
                    if row["valid_from"] is not None and e["start_time"] is not None and row["valid_from"] < e["start_time"] - 2:
                        raise ValueError("State precedes transition event")
            if collection == "relations":
                if row["from_id"] not in entities or row["to_id"] not in entities or any(r not in events for r in row["event_ids"]):
                    raise ValueError("Invalid relation reference")
                if row["type"] == "temporal_precedes":
                    a, b = events.get(row["from_id"]), events.get(row["to_id"])
                    if a is None or b is None or (a["start_time"] is not None and b["start_time"] is not None and a["start_time"] > b["start_time"]):
                        raise ValueError("Invalid temporal precedence")
    for s in value["stages"]:
        if any(r not in events for r in s["event_ids"]):
            raise ValueError("Unknown stage event")
    c = value["coverage"]
    if not 0 <= c["observed_start_time"] <= c["observed_end_time"] <= duration:
        raise ValueError("Invalid coverage")
    return {"status": "PASS", "checks": ["schema", "unique_ids", "media_times", "references",
            "transition_times", "evidence_availability"], "semantic_truth_verified": False,
            "counts": {k: len(value[k]) for k in ("stages", "events", "objects", "states", "relations", "evidence")}}


def usage_summary(run_dir, config):
    records = ledger(run_dir)
    entries = []
    for p in sorted(run_dir.glob("seg-*/attempt-*.response.json")):
        r = read_json(p)
        body = json.loads(r["body"]) if r["body"] else {}
        entries.append({"path": p.relative_to(run_dir).as_posix(), "status_code": r["status_code"],
                        "elapsed_sec": r["elapsed_sec"], "usage": body.get("usage"),
                        "transport_operations": r.get("transport_operations", [])})
    inputs = sum((e["usage"] or {}).get("input_tokens", 0) for e in entries)
    outputs = sum((e["usage"] or {}).get("output_tokens", 0) for e in entries)
    costs = []
    for e in entries:
        u = e["usage"]
        if u:
            i, o = u["input_tokens"], u["output_tokens"]
            ri, ro = (1, 10) if i <= 32000 else ((1.5, 15) if i <= 128000 else (3, 30))
            costs.append((i * ri + o * ro) / 1e6)
    return {"attempts_reserved": len(records), "completed_responses": len(entries),
            "reserved_cost": sum(r["cost_reserved"] for r in records), "currency": "CNY",
            "input_tokens_reported": inputs, "output_tokens_reported": outputs,
            "estimated_cost": sum(costs), "usage_complete": len(costs) == len(records),
            "actual_billed_cost": None, "price_source": config["price_source"], "calls": entries}


def run(args):
    config = load_full_config(args.config)
    media = inspect_video(project_path(config["video_path"]), config["ffprobe"], config["ffmpeg"], config["media_timeout_sec"])
    frames = math.ceil(media["duration_sec"] * config["sample_fps"])
    # Conservative patch estimate; server-selected PTS/pixels are not exposed.
    estimate = frames * (math.ceil(config["video_max_pixels"] / (28 * 28)) + 16) + 8000
    ceiling_cost = (config["max_input_tokens_estimate"] * config["input_cost_per_million"] +
                    config["max_output_tokens"] * config["output_cost_per_million"]) / 1e6
    if media["size_bytes"] > config["max_video_bytes"] or media["duration_sec"] > config["max_video_duration_sec"]:
        raise Blocked("NATIVE_VIDEO_FILE_LIMIT: no automatic segment fallback")
    if estimate > config["max_input_tokens_estimate"] or config["max_input_tokens_estimate"] + config["max_output_tokens"] > config["max_context_tokens"]:
        raise Blocked("CONTEXT_ESTIMATE_LIMIT: no automatic segment fallback")
    if ceiling_cost > config["cost_reserve_per_call"]:
        raise Blocked("Cost estimate exceeds per-call reservation")
    template = PROMPT.read_text(encoding="utf-8")
    if args.focus:
        template += "\n本轮专题焦点：" + args.focus
    prompt = template + "\n原视频时长(秒): " + str(media["duration_sec"]) + "\n严格遵循此 JSON Schema:\n" + json.dumps(read_json(SCHEMA), ensure_ascii=False)
    provider = QwenNativeProvider(config)
    request = provider.build_request(project_path(config["video_path"]), {}, prompt)
    meta = {"config": config, "media": media, "prompt_sha256": digest(prompt), "schema_sha256": file_hash(SCHEMA),
            "code_sha256": digest({p.relative_to(PACKAGE).as_posix(): file_hash(p) for p in sorted(PACKAGE.rglob("*.py"))}),
            "request_sha256": digest(request), "input_policy": "ORIGINAL_MP4_AND_NEUTRAL_PROMPT_ONLY",
            "input_mode": "native_video_file", "prompt_version": "full-video-observation-v0.1",
            "annotation_status": "CANDIDATE", "sample_pts_known": False}
    run_id = args.run_id or "session2-full-video"
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", run_id):
        raise ValueError("Unsafe run ID")
    run_dir = project_path(config["output_dir"]) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    plan = {"mode": "full_video", "run_id": run_id, "media": {k: media[k] for k in ("duration_sec", "size_bytes", "fps", "width", "height", "has_audio", "sha256")},
            "estimated_sample_frames": frames, "estimated_input_tokens": estimate,
            "input_token_ceiling": config["max_input_tokens_estimate"], "output_token_ceiling": config["max_output_tokens"],
            "estimated_ceiling_cost": ceiling_cost, "cost_reserve_per_call": config["cost_reserve_per_call"],
            "max_cost": config["max_cost"], "max_api_calls": config["max_api_calls"], "network_requests": 0}
    if args.dry_run:
        write_new(run_dir / ("dry_run-" + uuid4().hex + ".json"), plan)
        return plan
    lock = run_dir / ".active.lock"
    with lock.open("x", encoding="utf-8") as handle:
        handle.write(utc_now())
    try:
        # All focused passes use the same run ledger, so the budget cannot reset.
        pass_id = args.pass_id
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,60}", pass_id):
            raise ValueError("Unsafe pass ID")
        directory = run_dir / ("seg-" + pass_id)
        directory.mkdir(exist_ok=True)
        trace = meta | {"frames": [], "planned_frame_count": frames, "prompt": prompt, "request": request}
        saved = directory / "request.json"
        if saved.exists():
            prior = read_json(saved)
            if args.reparse_only and not args.focus:
                if prior["config"] != config or prior["media"]["sha256"] != media["sha256"]:
                    raise ValueError("Reparse config/media mismatch")
                request = prior["request"]
                trace = prior
            elif any(prior[k] != trace[k] for k in trace if k != "code_sha256"):
                raise ValueError("Immutable request changed; use a distinct pass ID")
            meta = prior
        else:
            write_new(saved, trace)
        if not (run_dir / "run_manifest.json").exists():
            write_new(run_dir / "run_manifest.json", {"run_id": run_id, "first_pass": meta})
        print(json.dumps({"pre_call_budget": plan, "prior_usage": usage_summary(run_dir, config)}, ensure_ascii=False), flush=True)
        raw_path, raw, reused = call_or_reuse(provider, request, directory, run_dir, config, load_api_key(config), args.reparse_only, False)
        content, response_meta = provider.extract_content(raw["body"])
        if response_meta["finish_reason"] != "stop":
            raise ValueError("Output truncated/non-stop; raw retained, no automatic repair call")
        value = json.loads(content)
        # Store independent output before local validation; no historical data read.
        candidate_path = directory / "global_analysis.json"
        if not candidate_path.exists():
            write_new(candidate_path, value)
        elif read_json(candidate_path) != value:
            raise ValueError("Saved candidate differs from raw response")
        normalized, repairs = normalize(value)
        try:
            validation = validate_global(normalized, media["duration_sec"])
        except Exception as error:
            write_new(directory / ("validation_failure-" + uuid4().hex + ".json"),
                      {"error_type": type(error).__name__, "raw_response_ref": raw_path.name,
                       "raw_response_sha256": file_hash(raw_path), "new_api_call": not reused})
            raise
        canonical_path = directory / "canonical_analysis.json"
        if not canonical_path.exists():
            write_new(canonical_path, normalized)
        elif read_json(canonical_path) != normalized:
            raise ValueError("Canonical normalization changed")
        diagnostic = {**validation, "response": response_meta, "usage": usage_summary(run_dir, config),
                      "raw_response_ref": raw_path.relative_to(run_dir).as_posix(),
                      "raw_response_sha256": file_hash(raw_path), "source_sha256": media["sha256"],
                      "claimed_coverage": value["coverage"], "server_sample_pts_available": False,
                      "reused_response": reused, "structural_repairs": repairs,
                      "parser_code_sha256": digest({p.relative_to(PACKAGE).as_posix(): file_hash(p) for p in sorted(PACKAGE.rglob("*.py"))})}
        write_new(directory / ("diagnostic-" + uuid4().hex + ".json"), diagnostic)
        return diagnostic
    finally:
        lock.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["full_video", "segment"], default="full_video")
    parser.add_argument("--config", type=Path, default=PACKAGE / "config.full_video.yaml")
    parser.add_argument("--run-id")
    parser.add_argument("--pass-id", default="global")
    parser.add_argument("--focus")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--reparse-only", action="store_true")
    args = parser.parse_args()
    if args.mode == "segment":
        parser.error("Use annotation_pipeline.annotate_segments explicitly for local inspection; no full-episode fallback")
    try:
        print(json.dumps(run(args), ensure_ascii=False, indent=2))
    except Exception as error:
        # Do not dump provider/transport exception strings or transient certificates.
        print(json.dumps({"status": "FAILED", "error_type": type(error).__name__,
                          "reason": str(error) if isinstance(error, (Blocked, jsonschema.ValidationError)) else "Local processing failed; inspect retained artifacts"}, ensure_ascii=False))
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
