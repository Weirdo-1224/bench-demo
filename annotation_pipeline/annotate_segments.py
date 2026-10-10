from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from uuid import uuid4

from . import __version__
from .calls import Blocked, call_or_reuse, ledger, utc_now
from .common import PACKAGE, digest, file_hash, load_api_key, load_config, project_path, read_json, write_new
from .inspect_video import inspect_video
from .media import extract_frames, plan_segments
from .providers import get_provider
from .validate_output import SCHEMA_PATH, model_schema, structure, validate_candidate


def code_hash():
    return digest({p.relative_to(PACKAGE).as_posix(): file_hash(p) for p in sorted(PACKAGE.rglob("*.py"))})


def render_prompt(template, segment, manifest):
    # Neutral requirements + schema + this MP4's timestamps only. No V1 access.
    return (template + "\n" + json.dumps(model_schema(), ensure_ascii=False) +
            "\n片段长度（秒）: " + str(segment["end_sec"] - segment["start_sec"]) +
            "\n实际送入的帧时间表:\n" + json.dumps([
                {k: f[k] for k in ("frame_id", "clip_local_sec", "source_sec", "source_pts")}
                for f in manifest["frames"]], ensure_ascii=False))


def usage_summary(run_dir, config):
    records = ledger(run_dir)
    usages = []
    for path in sorted(run_dir.glob("seg-*/attempt-*.response.json")):
        raw = read_json(path)
        if raw["body"]:
            try:
                body = json.loads(raw["body"])
                if isinstance(body, dict) and isinstance(body.get("usage"), dict):
                    usages.append(body["usage"])
            except json.JSONDecodeError:
                pass
    input_tokens = sum(u.get("prompt_tokens", 0) for u in usages)
    output_tokens = sum(u.get("completion_tokens", 0) for u in usages)
    rates = (config["input_cost_per_million"], config["output_cost_per_million"])
    complete_usage = len(usages) == len(records)
    estimate = None
    if complete_usage and all(r is not None for r in rates):
        estimate = (input_tokens * rates[0] + output_tokens * rates[1]) / 1_000_000
    return {"attempts_reserved": len(records), "submitted_frame_count": sum(r["frame_count"] for r in records),
            "reserved_cost": sum(r["cost_reserved"] for r in records), "currency": config["currency"],
            "usage_records": usages, "usage_complete": complete_usage, "input_tokens_reported": input_tokens,
            "output_tokens_reported": output_tokens, "estimated_cost_from_configured_rates": estimate,
            "actual_billed_cost": None,
            "budget_note": "Reservation caps local attempts; service billing is unknown until provider reconciliation"}


def process_segment(provider, config, media, segment, run_dir, run_meta, template, args):
    directory = run_dir / segment["segment_id"]
    directory.mkdir(exist_ok=True)
    candidate_path = directory / "candidate.json"
    if candidate_path.exists():
        result = validate_candidate(read_json(candidate_path), directory)
        return {**result, "segment_id": segment["segment_id"], "status": "REUSED_CANDIDATE"}
    manifest = extract_frames(project_path(config["video_path"]), media, segment, directory / "input", config)
    prompt = render_prompt(template, segment, manifest)
    request = provider.build_request(directory / "input", manifest, prompt)
    request_bytes = len(json.dumps(request).encode("utf-8"))
    if request_bytes > config["max_request_bytes"]:
        raise ValueError("Request exceeds max_request_bytes; no API call sent")
    request_hash = digest(request)
    trace = {"request_sha256": request_hash, "input_manifest_ref": "input/input_manifest.json",
             "endpoint": config["endpoint"], "model": config["model"], "provider": config["provider"],
             "input_mode": manifest["input_mode"], "frames": manifest["frames"], "prompt": prompt,
             "parameters": {k: v for k, v in request.items() if k != "messages"},
             "request_bytes": request_bytes}
    request_path = directory / "request.json"
    if request_path.exists():
        if read_json(request_path) != trace:
            raise ValueError("Saved request differs; refusing cache reuse")
    else:
        write_new(request_path, trace)
    raw_path, raw, reused = call_or_reuse(provider, request, directory, run_dir, config,
                                         load_api_key(config), args.reparse_only,
                                         args.retry_uncertain)
    content, metadata = provider.extract_content(raw["body"])
    if metadata["finish_reason"] != "stop":
        raise ValueError("Model response incomplete/non-stop; preserve raw response and adjust config")
    value = json.loads(content)
    provenance = {"run_id": run_meta["run_id"], "provider": config["provider"], "model_id": config["model"],
                  "model_version": config["model_version"], "returned_model": metadata["returned_model"],
                  "endpoint": config["endpoint"], "prompt_version": "segment-observation-v0.1",
                  "prompt_sha256": run_meta["prompt_sha256"], "schema_sha256": run_meta["schema_sha256"],
                  "config_sha256": run_meta["config_sha256"], "request_sha256": request_hash,
                  "raw_response_ref": raw_path.name, "raw_response_sha256": file_hash(raw_path),
                  "input_mode": "sampled_video_frames"}
    candidate = structure(value, media, segment, manifest, provenance, config["episode_id"])
    validation = validate_candidate(candidate, directory)
    write_new(candidate_path, candidate)
    write_new(directory / "validation.json", validation)
    return {**validation, "segment_id": segment["segment_id"], "status": "REPARSED" if reused else "ANNOTATED"}


def run(args):
    config = load_config(args.config)
    if not args.dry_run and not args.smoke:
        raise ValueError("Session 1 allows live processing only with --smoke; full-video calls are disabled")
    media = inspect_video(project_path(config["video_path"]), config["ffprobe"], config["ffmpeg"], config["media_timeout_sec"])
    if args.smoke:
        if not 30 <= config["window_sec"] <= 60 or not 1 <= config["smoke_segments"] <= 2:
            raise ValueError("Smoke requires 1-2 windows of 30-60 seconds")
    segments = plan_segments(media["duration_sec"], config["window_sec"], config["overlap_sec"], config["sample_fps"],
                             config["smoke_start_sec"] if args.smoke else 0)
    if args.smoke:
        segments = segments[:config["smoke_segments"]]
        if any(s["end_sec"] - s["start_sec"] < 30 for s in segments):
            raise ValueError("Smoke window truncated below 30 seconds; select an earlier start")
    if any(s["planned_frames"] > config["max_frames_per_segment"] or s["planned_frames"] < 4 for s in segments):
        raise ValueError("Sampling plan exceeds provider/configured frame limits")
    template_path = PACKAGE / "prompts" / "segment_observation.md"
    template = template_path.read_text(encoding="utf-8")
    hashes = {"config_sha256": digest(config), "prompt_sha256": file_hash(template_path),
              "schema_sha256": file_hash(SCHEMA_PATH), "code_sha256": code_hash()}
    fingerprint = digest({**hashes, "media_sha256": media["sha256"], "segments": segments, "pipeline_version": __version__})
    run_id = args.run_id or "session1-" + fingerprint[:20]
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", run_id):
        raise ValueError("Unsafe run_id")
    run_dir = project_path(config["output_dir"]) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    plan = {"run_id": run_id, "mode": "smoke" if args.smoke else "planning_only",
            "media": {k: media[k] for k in ("sha256", "duration_sec", "width", "height", "fps", "has_audio")},
            "segments": segments, "planned_initial_calls": len(segments),
            "worst_case_attempts": len(segments) * (1 + config["max_retries"]),
            "max_api_calls": config["max_api_calls"], "max_cost_reservation": config["max_cost"],
            "network_requests": 0, "api_key_present": bool(load_api_key(config)),
            "annotation_status": "CANDIDATE", "input_policy": "ORIGINAL_MP4_AND_NEUTRAL_PROMPT_ONLY"}
    if args.dry_run:
        plan["status"] = "DRY_RUN_PASS"
        path = run_dir / f"dry_run-{uuid4().hex}.json"
        write_new(path, plan)
        return plan | {"report_path": path.as_posix()}, 0
    lock = run_dir / ".active.lock"
    try:
        handle = lock.open("x", encoding="utf-8")
    except FileExistsError:
        raise Blocked(f"Run is locked: {lock}; inspect interrupted process before removing its lock")
    try:
        with handle:
            handle.write(f"pid={os.getpid()} started={utc_now()}\n")
        manifest_path = run_dir / "run_manifest.json"
        meta = {"run_id": run_id, "fingerprint": fingerprint, **hashes, "pipeline_version": __version__,
                "config": config, "media": media, "segments": segments,
                "annotation_status": "CANDIDATE", "input_policy": plan["input_policy"]}
        if manifest_path.exists():
            if read_json(manifest_path) != meta:
                raise ValueError("Run manifest changed; use a new run ID (original run is immutable)")
        else:
            write_new(manifest_path, meta)
            write_new(run_dir / "prompt_snapshot.json", {"template": template, "schema": model_schema()})
        provider = get_provider(config)
        before = len(ledger(run_dir))
        results = []
        for segment in segments:
            try:
                results.append(process_segment(provider, config, media, segment, run_dir, meta, template, args))
            except (Blocked, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
                # Error text from our code/JSON parser contains no key; provider exception messages are excluded.
                if isinstance(error, Blocked):
                    message = str(error)
                    status = "BLOCKED"
                else:
                    message = f"{type(error).__name__}: local processing/validation failed; raw records retained"
                    status = "FAILED"
                item = {"segment_id": segment["segment_id"], "status": status, "reason": message}
                write_new(run_dir / segment["segment_id"] / f"error-{uuid4().hex}.json", item)
                results.append(item)
            except Exception as error:
                # Includes JSON Schema failures; retain type but never dump provider payloads into console.
                item = {"segment_id": segment["segment_id"], "status": "FAILED", "reason": type(error).__name__}
                write_new(run_dir / segment["segment_id"] / f"error-{uuid4().hex}.json", item)
                results.append(item)
        summary = plan | {"status": "SMOKE_PASS" if all(r["status"] not in ("BLOCKED", "FAILED") for r in results) else "SMOKE_INCOMPLETE",
                          "segments": results, "network_requests": len(ledger(run_dir)) - before,
                          "usage": usage_summary(run_dir, config), "completed_at": utc_now()}
        path = run_dir / f"summary-{uuid4().hex}.json"
        write_new(path, summary)
        return summary | {"report_path": path.as_posix()}, 0 if summary["status"] == "SMOKE_PASS" else 2
    finally:
        lock.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Session 1: independently observe at most 2 short video windows")
    parser.add_argument("--config", type=Path, default=PACKAGE / "config.example.yaml")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--run-id")
    parser.add_argument("--reparse-only", action="store_true", help="Reuse saved success; never send a request")
    parser.add_argument("--retry-uncertain", action="store_true", help="Explicitly allow reattempt after unknown billing outcome")
    args = parser.parse_args()
    try:
        result, code = run(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return code
    except (ValueError, Blocked, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({"status": "FAILED", "reason": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
