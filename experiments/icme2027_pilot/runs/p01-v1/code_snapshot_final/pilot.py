"""GX010021 only: preparation, approved P01 real API run and offline scoring.

Run from repository root: python experiments/icme2027_pilot/pilot.py --help
Only the explicit run command can make paid API calls.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone, timedelta
from fractions import Fraction
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from annotation_pipeline.common import file_hash, digest, load_api_key
from annotation_pipeline.inspect_video import inspect_video
from annotation_pipeline.media import extract_frames, plan_segments

EP = ROOT / "golden_episode/GX010021"
VIDEO = EP / "source/GX010021.MP4"
V1 = EP / "tasks/v1_candidates/pilot_task_candidates.json"
V2 = EP / "tasks/v2_candidates/task_candidates.json"
CHECKS = ["A_video_verifiable", "B_history_required", "C_recent_no_leak",
          "D_critical_interval", "E_no_alternative_evidence", "F_control_irrelevant",
          "sampled_1fps_sufficient", "masked_history_inspected"]


def now():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def rows(path):
    p = Path(path)
    return [json.loads(s) for s in p.read_text(encoding="utf-8-sig").splitlines() if s.strip()] if p.exists() else []


def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def write_rows(path, data):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("".join(json.dumps(x, ensure_ascii=False, allow_nan=False) + "\n" for x in data), encoding="utf-8")
    tmp.replace(path)


def cmd(args, timeout=180):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, timeout=timeout)
    if result.returncode:
        raise ValueError(f"Local command failed ({args[0]}): {result.stderr.decode('utf-8', errors='replace')[-1800:]}")
    return result.stdout.decode("utf-8", errors="replace")


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def original_paths():
    tracked = cmd(["git", "ls-files"]).splitlines()
    paths = {ROOT / x for x in tracked if not x.startswith("experiments/icme2027_pilot/")}
    paths.update([VIDEO, ROOT / "annotation_pipeline/credentials.local.json"])
    # Also protect ignored original model responses and local evidence manifests.
    paths.update((EP / "annotations/v2_video_model/runs").rglob("*.json"))
    return sorted(p for p in paths if p.is_file())


def verify_originals():
    baseline = read(HERE / "audit/original_hashes.json")
    changed = [p for p, h in baseline.items() if not (ROOT / p).is_file() or file_hash(ROOT / p) != h]
    if changed:
        raise ValueError("Original asset integrity changed: " + ", ".join(changed))
    if cmd(["git", "rev-parse", "HEAD"]).strip() != read(HERE / "audit/audit.json")["git_head"]:
        raise ValueError("Git HEAD changed since frozen audit; review required")
    return {"protected_files": len(baseline), "all_hashes_match": True, "checked_at": now()}


def audit():
    out = HERE / "audit"
    out.mkdir(exist_ok=True)
    if (out / "original_hashes.json").exists():
        result = verify_originals()
        write(out / "integrity_check.json", result)
        print(json.dumps(result)); return
    media = inspect_video(VIDEO)
    declared = read(EP / "annotations/v2_video_model/annotation_manifest.json")["media"]
    if media["sha256"] != declared["sha256"] or media["has_audio"]:
        raise ValueError("Original video hash/audio differs from declared silent-video asset")
    write(out / "original_hashes.json", {rel(p): file_hash(p) for p in original_paths()})
    versions = {x: cmd([x, "-version"]).splitlines()[0] for x in ["ffmpeg", "ffprobe"]}
    assets = [VIDEO, V1, V2, EP / "annotations/v2_video_model/annotation_manifest.json",
              EP / "annotations/v2_video_model/full_video_report.md",
              EP / "annotations/v2_video_model/crosscheck_report.md",
              ROOT / "annotation_pipeline/providers/qwen.py", ROOT / "annotation_pipeline/providers/qwen_native.py",
              ROOT / "annotation_pipeline/media.py", ROOT / "annotation_pipeline/common.py"]
    # Never serialize the credential mapping or API key.
    credential = {"path": "annotation_pipeline/credentials.local.json",
                  "exists": (ROOT / "annotation_pipeline/credentials.local.json").exists(),
                  "loadable_key": bool(load_api_key({"api_key_env": "DASHSCOPE_API_KEY"})),
                  "network_verified": False}
    task_counts = {}
    for name, path in [("v1", V1), ("v2", V2)]:
        ts = read(path)["tasks"]
        task_counts[name] = {"total": len(ts), "T1": sum(t["track"] == "T1" for t in ts),
                             "T3": sum(t["track"] == "T3" for t in ts), "human_gold": 0}
    write(out / "media.json", media)
    result = {"created_at": now(), "git_head": cmd(["git", "rev-parse", "HEAD"]).strip(),
              "git_status_before": cmd(["git", "status", "--short"]),
              "assets": [{"path": rel(p), "exists": p.exists(), "sha256": file_hash(p)} for p in assets],
              "credentials": credential, "task_sources": task_counts,
              "python": sys.version, "executables": {x: shutil.which(x) for x in versions}, "versions": versions,
              "dependencies": {x: bool(importlib.util.find_spec(x)) for x in ["requests", "yaml", "PIL", "jsonschema"]},
              "api_calls_this_phase": 0, "cost_estimate_this_phase_cny": 0,
              "reusable": {"frame_provider": "annotation_pipeline.providers.qwen.QwenProvider",
                           "native_provider": "annotation_pipeline.providers.qwen_native.QwenNativeProvider (not needed for exact-PTS frames)",
                           "frames": "annotation_pipeline.media.extract_frames / verify_frames / plan_segments",
                           "credentials": "annotation_pipeline.common.load_api_key",
                           "media": "annotation_pipeline.inspect_video.inspect_video"}}
    write(out / "audit.json", result)
    write(out / "integrity_check.json", verify_originals())
    print(json.dumps({"audit": str(out), "media_sha256": media["sha256"], "credentials": credential}))


def definitions():
    """Adapt two T1 definitions; source questions/Schema remain unchanged."""
    specs = [
        ("P01", "GX010021-V2-T1-001", "GX010021-T1-001", 300.0, [174.0, 240.0], [0.0, 66.0],
         "截至当前视频时刻，操作者是否已经完成过一轮电动搅拌动作（搅拌头进入主容器内操作，随后提离并放置搅拌器）？只判断动作段结束，不判断混合均匀程度或食谱要求。",
         [[199.0, 235.0], [235.0, 239.0]],
         "原检查点239.3秒延后至300秒；屏蔽174–240秒含安装、搅拌、提离及放置，避免仅删静态锚点。",
         "当前窗口仍可能见搅拌器静置或液体外观；仅凭这些不能证明完整动作链。若人工认为已明显泄露或有等价证据，必须INVALID。"),
        ("P02", "GX010021-V2-T1-002", "GX010021-T1-002", 540.0, [390.0, 462.0], [0.0, 72.0],
         "截至当前视频时刻，在微波加热后取出并查看或搅动玻璃容器内黄色材料的过程中，是否曾清楚看到液体与固态块共存？只判断曾经可见的相态，不判断倒入时是否完全融化。",
         [[430.0, 433.0], [444.0, 447.0]],
         "原相态检查点431.2308/445.211433秒延后至540秒；屏蔽390–462秒覆盖两次取出检查、再加热及搅动至转移前后。",
         "检查390秒前首次入炉过程是否已显示符合题意的加热后共存；检查462秒以后是否仍有同样的玻璃容器共存画面。若存在须INVALID，不能以常识判断。")]
    ts = []
    for tid, src2, src1, q, critical, control, question, evidence, adaptation, risk in specs:
        t = {"task_id": tid, "episode_id": "GX010021", "track": "T1", "status": "PENDING",
             "source_task_ids": [src2, src1], "source_paths": [rel(V2), rel(V1)],
             "query_time_sec": q, "recent_interval_sec": [q - 60, q], "question": question,
             "critical_interval_sec": critical, "control_interval_sec": control,
             "candidate_visible_evidence_intervals_sec": evidence,
             "proposed_answers": {"FULL": "YES", "CRITICAL_MASK": "UNKNOWN", "CONTROL_MASK": "YES", "recent_only": "UNKNOWN"},
             "gold_answers": None, "adaptation": adaptation,
             "known_risk_to_review": risk, "semantic_review": {k: "PENDING" for k in CHECKS},
             "clips": {role: f"clips/{tid}/{role}.mp4" for role in ["critical", "current", "control", "critical_mask_history"]},
             "review_1fps": f"review_frames/{tid}/index.md", "source_video_sha256": read(HERE / "audit/media.json")["sha256"]}
        t["definition_sha256"] = digest(t)
        ts.append(t)
    return ts


def selection_audit():
    decisions = []
    reasons = {
        "GX010021-T1-001": "ADAPTED_P01", "GX010021-T1-002": "ADAPTED_P02",
        "GX010021-T1-003": "EXCLUDED:终态光滑证据不足；晚期证据与可用延后窗口太近，暂不扩展",
        "GX010021-T1-004": "EXCLUDED:预热完成不可视频核验，UNKNOWN不构成历史必要性",
        "GX010021-T3-001": "EXCLUDED:油许可/指导语的公开及生效时刻不可从静音视频核验",
        "GX010021-V2-T1-001": "ADAPTED_P01", "GX010021-V2-T1-002": "ADAPTED_P02",
        "GX010021-V2-T1-003": "EXCLUDED:680秒近期可见入模与残留；片尾不够留出60秒历史间隔",
        "GX010021-V2-T1-004": "EXCLUDED:光滑终态尚缺连续证据；不增加第三道高风险题",
        "GX010021-V2-T3-001": "EXCLUDED:用油许可依赖无音轨无法核验的对话与规则",
        "GX010021-V2-T3-002": "EXCLUDED:正常性依赖未确认规范及加热时长，不能造负例真值",
        "GX010021-V2-T3-003": "EXCLUDED:第三枚蛋破损/入料事实不明，不能确认错误",
        "GX010021-V2-T3-004": "EXCLUDED:无已确认偏差或恢复事实"}
    for path in [V1, V2]:
        for i, t in enumerate(read(path)["tasks"]):
            if t["track"] in ["T1", "T3"]:
                decisions.append({"source_path": rel(path), "json_pointer": f"/tasks/{i}",
                                  "task_id": t["task_id"], "title": t["title"],
                                  "decision": reasons[t["task_id"]]})
    return decisions


def make_clip(task, role, interval, masked=False):
    path = HERE / task["clips"][role]
    path.parent.mkdir(parents=True, exist_ok=True)
    record = path.with_suffix(".manifest.json")
    start, end = interval
    filters = f"trim=start={start}:end={end},setpts=PTS-STARTPTS"
    if masked:
        a, b = task["critical_interval_sec"]
        filters += f",drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='gte(t,{a})*lt(t,{b})'"
    command = ["ffmpeg", "-hide_banner", "-v", "error", "-nostdin", "-n", "-i", str(VIDEO),
               "-map", "0:v:0", "-an", "-sn", "-dn", "-vf", filters,
               "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-fps_mode", "vfr", "-movflags", "+faststart", str(path)]
    params = {"source_sha256": task["source_video_sha256"], "source_interval_sec": interval,
              "role": role, "mask_interval_sec": task["critical_interval_sec"] if masked else None,
              "purpose": "HUMAN_REVIEW_ONLY; agent will receive audited 1fps source frames",
              "definition_sha256": task["definition_sha256"]}
    if path.exists():
        old = read(record)
        if any(old.get(k) != v for k, v in params.items()) or file_hash(path) != old["sha256"]:
            raise ValueError(f"Review clip changed or stale: {path}")
        return old
    cmd(command)
    # Decode every output frame and inspect timestamps/duration; never just trust ffmpeg exit status.
    cmd(["ffmpeg", "-hide_banner", "-v", "error", "-xerror", "-i", str(path), "-map", "0:v:0", "-f", "null", "-"])
    probe = json.loads(cmd(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]))
    v = next(s for s in probe["streams"] if s["codec_type"] == "video")
    duration = float(v["duration"])
    if abs(duration - (end - start)) > 2 / 29.97 or any(s["codec_type"] == "audio" for s in probe["streams"]):
        raise ValueError(f"Unexpected clip time/audio: {path}")
    result = params | {"path": rel(path), "sha256": file_hash(path), "duration_sec": duration,
                       "frames": int(v["nb_frames"]), "command": command, "full_decode": "PASS",
                       "local_to_source": f"source_sec approximately local_sec + {start}; CFR boundary within one source frame"}
    write(record, result)
    return result


def sample_review(task):
    """Reuse original timestamp-audited extraction. Contact sheets are review only."""
    from PIL import Image, ImageDraw, ImageFont
    media = read(HERE / "audit/media.json")
    q = task["query_time_sec"]
    segments = plan_segments(q, 60, 0, 1)
    frames = []
    for seg in segments:
        folder = HERE / "inputs" / f"{seg['start_sec']:09.3f}-{seg['end_sec']:09.3f}"
        man = extract_frames(VIDEO, media, seg, folder, {"ffmpeg": "ffmpeg", "media_timeout_sec": 180})
        frames.extend({**f, "absolute_path": folder / f["path"]} for f in man["frames"])
    out = HERE / "review_frames" / task["task_id"]
    out.mkdir(parents=True, exist_ok=True)
    links = ["# Actual 1 FPS review frames", "", "All timestamps below are original source PTS; thumbnails are not agent inputs.", ""]
    for start in range(0, int(q), 60):
        subset = [f for f in frames if start <= f["source_sec"] < start + 60]
        sheet = Image.new("RGB", (5 * 256, math.ceil(len(subset) / 5) * 164), "#eeeeee")
        draw = ImageDraw.Draw(sheet)
        for i, f in enumerate(subset):
            im = Image.open(f["absolute_path"]); im.thumbnail((256, 144))
            x, y = i % 5 * 256, i // 5 * 164
            sheet.paste(im, (x, y))
            mask = task["critical_interval_sec"][0] <= f["source_sec"] < task["critical_interval_sec"][1]
            draw.text((x + 4, y + 145), f"{f['source_sec']:.3f}s" + (" [CRITICAL MASK]" if mask else ""), fill="red" if mask else "black")
        name = f"{start:04d}-{min(start+60,int(q)):04d}.jpg"
        sheet.save(out / name, quality=88)
        links.append(f"- [{start}–{min(start+60,int(q))}s]({name})")
    (out / "index.md").write_text("\n".join(links) + "\n", encoding="utf-8")
    write(out / "sampling_manifest.json", {"source_sha256": media["sha256"], "query_time_sec": q,
          "frames": [{k: rel(v) if k == "absolute_path" else v for k, v in f.items()} for f in frames]})


def mask_records(ts):
    result = []
    for t in ts:
        for condition in ["FULL", "CRITICAL_MASK", "CONTROL_MASK"]:
            interval = [] if condition == "FULL" else [t["critical_interval_sec"] if condition == "CRITICAL_MASK" else t["control_interval_sec"]]
            manifests = []
            masked = []
            total = 0
            for seg in plan_segments(t["query_time_sec"], 60, 0, 1):
                p = HERE / "inputs" / f"{seg['start_sec']:09.3f}-{seg['end_sec']:09.3f}" / "input_manifest.json"
                m = read(p)
                manifests.append({"path": rel(p), "sha256": file_hash(p)})
                total += len(m["frames"])
                masked.extend({"source_sec": f["source_sec"], "source_pts": f["source_pts"], "source_frame_sha256": f["sha256"]}
                              for f in m["frames"] if any(a <= f["source_sec"] < b for a, b in interval))
            result.append({"task_id": t["task_id"], "definition_sha256": t["definition_sha256"], "condition": condition,
                           "status": "PENDING_HUMAN_REVIEW", "intervals_sec": interval,
                           "method": "replace decoded JPEG with solid black at same dimensions before request construction",
                           "time_convention": "half-open [start,end); mask membership uses actual source PTS",
                           "sample_fps": 1, "total_frames": total, "masked_frame_count": len(masked),
                           "masked_frames": masked, "source_manifests": manifests,
                           "memory_reset": "REQUIRED from empty independently per condition",
                           "applied_to_model": False, "semantic_residual_review": "PENDING"})
    return result


def prepare():
    verify_originals()
    ts = definitions()
    path = HERE / "candidate_tasks.jsonl"
    if path.exists() and rows(path) != ts:
        raise ValueError("Existing candidates differ; preserve reviewed definitions and use an explicitly revised preparation")
    write_rows(path, ts)
    write_rows(HERE / "selection_audit.jsonl", selection_audit())
    for t in ts:
        for role, interval in [("critical", t["critical_interval_sec"]), ("current", t["recent_interval_sec"]),
                               ("control", t["control_interval_sec"]), ("critical_mask_history", [0, t["query_time_sec"]])]:
            make_clip(t, role, interval, masked=role == "critical_mask_history")
        sample_review(t)
        print(f"Prepared {t['task_id']}: 3 source clips + masked history + actual 1fps contact sheets", flush=True)
    write_rows(HERE / "mask_manifest.jsonl", mask_records(ts))
    if not (HERE / "review_decisions.jsonl").exists():
        write_rows(HERE / "review_decisions.jsonl", [{"task_id": t["task_id"], "definition_sha256": t["definition_sha256"],
            "status": "PENDING", "reviewer": "", "reviewed_at": "", "checks": {k: "PENDING" for k in CHECKS},
            "approved_answers": {"FULL": "PENDING", "CRITICAL_MASK": "PENDING", "CONTROL_MASK": "PENDING", "recent_only": "PENDING"},
            "evidence_intervals_sec": [], "notes": ""} for t in ts])
    for name in ["predictions.jsonl"]:
        if not (HERE / name).exists():
            (HERE / name).touch()
    write(HERE / "audit/integrity_check.json", verify_originals())
    validate(promote=False)
    report()


def valid_interval(x, limit):
    return (isinstance(x, list) and len(x) == 2 and all(type(v) in [int, float] and math.isfinite(v) for v in x)
            and 0 <= x[0] < x[1] <= limit)


def validate(promote=False):
    integrity = verify_originals()
    ts = rows(HERE / "candidate_tasks.jsonl")
    decisions = rows(HERE / "review_decisions.jsonl")
    if len(ts) > 5 or len({t["task_id"] for t in ts}) != len(ts):
        raise ValueError("At most five unique candidates required")
    if len({d["task_id"] for d in decisions}) != len(decisions) or {d["task_id"] for d in decisions} != {t["task_id"] for t in ts}:
        raise ValueError("Reviews must match candidates exactly (no duplicate/extra/missing IDs)")
    checks = []
    approved = []
    media = read(HERE / "audit/media.json")
    clip_hashes = {}
    for t in ts:
        payload = {k: v for k, v in t.items() if k != "definition_sha256"}
        if digest(payload) != t["definition_sha256"] or t["source_video_sha256"] != media["sha256"]:
            raise ValueError(f"Definition/source hash mismatch: {t['task_id']}")
        q = t["query_time_sec"]
        a, b = t["critical_interval_sec"], t["control_interval_sec"]
        if not (valid_interval(a, q-60) and valid_interval(b, q-60) and abs((a[1]-a[0])-(b[1]-b[0])) < 1e-6
                and (a[1] <= b[0] or b[1] <= a[0]) and 60 < q <= media["duration_sec"]):
            raise ValueError(f"Invalid critical/control/history boundaries: {t['task_id']}")
        for role, name in t["clips"].items():
            p = HERE / name
            m = read(p.with_suffix(".manifest.json"))
            if not p.is_file() or file_hash(p) != m["sha256"] or m["definition_sha256"] != t["definition_sha256"]:
                raise ValueError(f"Changed or missing clip: {p}")
            clip_hashes[name] = m["sha256"]
        sampling = read(HERE / "review_frames" / t["task_id"] / "sampling_manifest.json")
        fs = sampling["frames"]
        if len(fs) != math.ceil(q) or not all(0 <= f["source_sec"] < q for f in fs):
            raise ValueError("Future frames or incomplete sampling")
        for f in fs:
            if file_hash(ROOT / f["absolute_path"]) != f["sha256"]:
                raise ValueError("Sampled frame changed")
        counts = [sum(x[0] <= f["source_sec"] < x[1] for f in fs) for x in [a, b]]
        if counts[0] != counts[1]:
            raise ValueError("Critical/control masks must also match sampled frame counts")
        d = next(d for d in decisions if d["task_id"] == t["task_id"])
        if d["definition_sha256"] != t["definition_sha256"] or d["status"] not in ["PENDING", "APPROVED", "REJECTED", "INVALID"]:
            raise ValueError("Review definition hash/status invalid")
        if set(d["checks"]) != set(CHECKS) or any(v not in ["PENDING", "PASS", "FAIL"] for v in d["checks"].values()):
            raise ValueError("Review checks must be exactly the documented PENDING/PASS/FAIL fields")
        if d["status"] == "APPROVED":
            if not all(v == "PASS" for v in d["checks"].values()) or not d["reviewer"].strip() or not d["reviewed_at"].strip():
                raise ValueError(f"APPROVED requires named, dated reviewer and every check PASS: {t['task_id']}")
            try:
                datetime.fromisoformat(d["reviewed_at"])
            except ValueError:
                raise ValueError("reviewed_at must use ISO datetime") from None
            ans = d["approved_answers"]
            if ans != {"FULL": "YES", "CRITICAL_MASK": "UNKNOWN", "CONTROL_MASK": "YES", "recent_only": "UNKNOWN"}:
                raise ValueError("This preparation only admits verified YES/UNKNOWN/YES/UNKNOWN; changed findings require revised candidate")
            evidence = d["evidence_intervals_sec"]
            if not evidence or not all(valid_interval(e, q-60) and a[0] <= e[0] < e[1] <= a[1] for e in evidence):
                raise ValueError("Human evidence intervals must be nonempty and entirely inside critical history")
            if not all(any(e[0] <= f["source_sec"] < e[1] for f in fs) for e in evidence):
                raise ValueError("Each approved evidence interval needs a supplied 1fps source frame")
            item = t | {"status": "APPROVED", "semantic_review": d["checks"], "gold_answers": ans,
                                 "gold_evidence_intervals_sec": evidence, "human_review": d,
                                 "review_record_sha256": digest(d)}
            if d.get("normalized_question"):
                item["source_candidate_question"] = t["question"]
                item["question"] = d["normalized_question"]
                item["fact_gold"] = "YES"
                item["scoring_policy"] = "Fact YES; sufficient conditions YES; insufficient conditions UNKNOWN is appropriate, not a forced prediction."
                item["gold_record_sha256"] = digest(item)
            approved.append(item)
        checks.append({"task_id": t["task_id"], "structural_status": "PASS", "human_status": d["status"],
                       "critical_mask_frames": counts[0], "control_mask_frames": counts[1],
                       "semantic_truth_verified_by_program": False})
    if rows(HERE / "mask_manifest.jsonl") != mask_records(ts):
        raise ValueError("Mask manifest differs from source frame PTS/definitions")
    if promote:
        gold_path = HERE / "tasks_gold.jsonl"
        existing = rows(gold_path)
        if existing and existing != approved:
            raise ValueError("Existing Gold differs; preserve it and explicitly version the experiment")
        if approved:
            write_rows(gold_path, approved)
        # With zero approved records, never create a Gold file.
    result = {"created_at": now(), "integrity": integrity, "tasks": checks, "approved": len(approved),
              "pending": sum(c["human_status"] == "PENDING" for c in checks), "clip_sha256": clip_hashes,
              "api_calls": 0, "semantic_validation": "HUMAN_ONLY"}
    write(HERE / "validation.json", result)
    print(json.dumps({k: result[k] for k in ["approved", "pending", "api_calls", "semantic_validation"]}))
    return result


def execution_plan(t):
    return {"task_id": t["task_id"], "query_time_sec": t["query_time_sec"],
            "rolling_windows": plan_segments(t["query_time_sec"], 60, 0, 1),
            "recent_only_interval_sec": t["recent_interval_sec"],
            "calls_per_rolling_condition": len(plan_segments(t["query_time_sec"], 60, 0, 1)),
            "rolling_conditions": ["FULL", "CRITICAL_MASK", "CONTROL_MASK"],
            "rolling_calls_total": 3 * len(plan_segments(t["query_time_sec"], 60, 0, 1)),
            "recent_only_calls": 1, "sampling_fps": 1,
            "note": "Each historical window updates memory; final window answers with question delivered for first time. No extra answer call."}


def dry_run(task=None):
    validate()
    ts = [t for t in rows(HERE / "candidate_tasks.jsonl") if task is None or t["task_id"] == task]
    if not ts:
        raise ValueError("No matching task")
    plans = [execution_plan(t) for t in ts]
    result = {"created_at": now(), "plan_only": True, "api_calls_made": 0, "tasks": plans,
              "total_calls_without_retries": sum(p["rolling_calls_total"] + 1 for p in plans),
              "price_estimate_cny": None, "price_uncertainty": "Not quoted/verified; no model tokens billed in preparation. Runtime must enforce hard attempt cap.",
              "run_gate": "APPROVED Gold + implemented/reviewed phase-2 runner + explicit request cap required"}
    write(HERE / "dry_run.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def report():
    ts = rows(HERE / "candidate_tasks.jsonl")
    ds = {d["task_id"]: d for d in rows(HERE / "review_decisions.jsonl")}
    preds = rows(HERE / "predictions.jsonl")
    if preds:
        raise ValueError("Phase-1 report does not score predictions; continue with real phase-2 scorer")
    with (HERE / "results.csv").open("w", encoding="utf-8-sig", newline="") as f:
        fields = ["task_id", "review_status", "condition", "execution_status", "answer", "expected_answer",
                  "correct", "answerability_correct", "ungrounded_certain", "visible_evidence_supported",
                  "full_control_consistent", "input_tokens", "output_tokens", "elapsed_sec", "estimated_cost_cny", "manual_review"]
        writer = csv.DictWriter(f, fields); writer.writeheader()
        for t in ts:
            for condition in ["FULL", "CRITICAL_MASK", "CONTROL_MASK", "recent_only"]:
                writer.writerow({"task_id": t["task_id"], "review_status": ds[t["task_id"]]["status"], "condition": condition,
                                 "execution_status": "NOT_RUN", "manual_review": "PENDING"})
    summary = {"stage": "PREPARATION_ONLY", "created_at": now(), "candidate_tasks": len(ts),
               "approved_tasks": sum(d["status"] == "APPROVED" for d in ds.values()),
               "prediction_records": 0, "real_pilot_completed": False, "paper_grade_results": False,
               "api_calls": 0, "input_tokens": 0, "output_tokens": 0, "cost_incurred_cny": 0,
               "future_cost_estimate_cny": None, "accuracy": None,
               "failures": ["Human review pending; no new Gold created", "Real API validity/network not tested in this phase",
                            "Phase-2 harness/run/score intentionally deferred until human confirmation"]}
    write(HERE / "summary.json", summary)
    # An honest status plot; no fake accuracy/performance bars. PIL avoids adding a plotting dependency.
    from PIL import Image, ImageDraw, ImageFont
    fig = HERE / "figures"; fig.mkdir(exist_ok=True)
    im = Image.new("RGB", (1000, 330), "white"); draw = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    draw.text((30, 25), "GX010021 | PREPARATION STATUS | NOT EXPERIMENTAL RESULTS", fill="black", font=font)
    for i, t in enumerate(ts):
        y = 85 + i * 85
        draw.text((30, y), f"{t['task_id']} | q={t['query_time_sec']:.0f}s | {ds[t['task_id']]['status']}", fill="black", font=font)
        draw.rectangle((360, y, 800, y+25), fill="#dddddd")
        draw.text((365, y+2), "FULL / CRITICAL / CONTROL: NOT RUN", fill="black", font=font)
    draw.text((30, 285), "0 predictions | 0 API calls | accuracy undefined | human Gold required", fill="black", font=font)
    im.save(fig / "preparation_status.png")
    table = "\n".join(f"|{t['task_id']}|{t['query_time_sec']:.0f}|{t['critical_interval_sec']}|{t['control_interval_sec']}|{ds[t['task_id']]['status']}|NOT_RUN|" for t in ts)
    body = f"""# GX010021 ICME 2027 最小实验：准备阶段报告

本报告只包含审计、候选适配和媒体准备。**真实先导实验尚未运行；无论文级结果，无正确率。**
本轮新增API调用0，输入/输出Token均0，产生API费用0；下一阶段费用未知。Session1/2既有返回仅为资产，不能算作本实验预测。

|任务|query秒|关键屏蔽秒|等时长对照秒|人工状态|执行状态|
|---|---:|---|---|---|---|
{table}

两题均来自T1。筛选明细见 selection_audit.jsonl；T3被排除，原因包括依赖无音轨不能核验的许可对话、第三枚蛋事实不明和没有确认的错误恢复。
延后检查点及YES/NO/UNKNOWN改写仅存在于本实验目录，原任务Schema和原文件保持不变。两题均有风险项，不能仅凭模型历史报告晋升Gold。

## 一次人工入口

打开 [review_checklist.md](review_checklist.md)。先看每题三个原始片段，再看已黑屏的历史和实际1FPS缩略图，核对无替代证据、无近期泄露。
可直接在聊天回复审核结论及证据区间，由工程师写入 review_decisions.jsonl；也可自己编辑该文件，再运行 validate --promote。
每项都通过才可APPROVED；否则REJECTED或INVALID。PENDING不会进入Gold。

## 程序验证与实际边界

本地ffprobe确认视频696.929567秒、854×480、30000/1001fps、无音轨；视频SHA-256与annotation_manifest一致。
所有裁剪MP4逐帧解码检查；实际1FPS采样复用原提取器和PTS校验。关键/对照掩码不仅时长相等，实际抽样帧数也一致。
原始文件保护哈希、Git HEAD及检查结果见 audit/。程序只能证明结构/文件/时间合法，不能证明答案、历史必要性或屏蔽充分性。
figures/preparation_status.png 为准备状态图，无模拟预测。
另见 [program_qa.json](program_qa.json) 与 [program_test_report.txt](program_test_report.txt)：6项离线门禁测试通过；201个既有资产哈希一致；黑屏历史的66/72个采样画面亮度全黑，H.264色度允许1级舍入；生成文本实际密钥扫描无泄露。首次严格色度检查的误拒及修正记录也保留在program_qa.json。
[audit_notes.md](audit_notes.md) 记录具体复用函数、历史API记录与当前限制。所有这些仍属于程序验证。

## 未完成与阻塞清单

1. 两题尚待研究者核验：A–F、1FPS可见性及屏蔽后全部历史无替代证据。
2. 尚无本实验人工Gold；tasks_gold.jsonl在至少一道APPROVED后才创建。
3. 凭据已存在且可加载，但未联网验证，不宣称API有效。
4. 按本轮先审计/准备再确认的要求，真实Agent harness、run、score在确认后继续实现和实测；当前CLI对run/score明确拒绝，不会伪造输出。
5. 下一阶段先跑一题三条件及recent_only，成功且原日志齐全后才扩展。不得将CRITICAL_MASK的正确UNKNOWN计为推理错误。

结果表 results.csv 中所有预测/指标均为空，execution_status=NOT_RUN；summary.json 的accuracy=null。
"""
    (HERE / "advisor_report.md").write_text(body, encoding="utf-8")
    print(str(HERE / "advisor_report.md"))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    for name in ["audit", "prepare", "validate", "dry-run", "report", "run", "score"]:
        s = sub.add_parser(name)
        if name == "validate": s.add_argument("--promote", action="store_true")
        if name in ["dry-run", "run"]: s.add_argument("--task", default="P01")
        if name == "run":
            s.add_argument("--condition", default="ALL", choices=["ALL","FULL","CRITICAL_MASK","CONTROL_MASK","recent_only"])
            s.add_argument("--max-calls", type=int, default=20)
            s.add_argument("--retry-uncertain", action="store_true")
    args = p.parse_args()
    try:
        if args.command == "audit": audit()
        elif args.command == "prepare": prepare()
        elif args.command == "validate": validate(args.promote)
        elif args.command == "dry-run":
            if (HERE / "tasks_gold.jsonl").exists():
                import runtime
                runtime.preflight(args.task)
            else: dry_run(args.task)
        elif args.command in ["report", "score", "run"]:
            if args.command == "report" and not (HERE / "tasks_gold.jsonl").exists(): report()
            else:
                import runtime
                if args.command == "run": runtime.run(args.task,args.condition,args.max_calls,args.retry_uncertain)
                elif args.command == "score": runtime.score()
                else: runtime.report()
    except (ValueError, OSError, subprocess.SubprocessError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
