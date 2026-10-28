"""Single-episode real pilot runtime. No synthetic response path exists here."""
from __future__ import annotations

import csv
from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import shutil
import time

import requests
from PIL import Image, ImageStat, ImageDraw, ImageFont

import pilot as p
from annotation_pipeline.common import digest, file_hash, load_api_key, write_new
from annotation_pipeline.media import verify_frames
from annotation_pipeline.providers.qwen import QwenProvider

CONDITIONS = ["FULL", "CRITICAL_MASK", "CONTROL_MASK", "recent_only"]
RUN = p.HERE / "runs/p01-v1"
MAX_ATTEMPTS = 20
CONFIG = {"model": "qwen3-vl-plus", "model_version": "alias-unpinned",
          "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
          "api_key_env": "DASHSCOPE_API_KEY", "temperature": 0, "max_output_tokens": 1536,
          "max_frames_per_segment": 60, "timeout_sec": 180, "memory_max_chars": 4096,
          "sample_fps": 1, "max_attempts_global": MAX_ATTEMPTS, "max_attempts_per_window": 2,
          "max_request_bytes": 15000000, "cost_reserve_per_attempt_cny": 0.25,
          "max_local_reserved_cny": 5.0,
          "price_estimate": None, "price_uncertainty": "Current regional/alias tariff not reliably verified. Local reservation is NOT provider billing cap; hard API attempt cap is enforced."}

BASE = """你是仅观察静音视频的流式视频助手。只根据已经提供的帧和你此前的观察记忆作答。黑帧表示该采样时刻的视觉信息不可见，不代表动作没有发生。所有时间为原视频秒；每秒只采样一帧，帧间事件不能当作已看见。不要根据常识或物体外观虚构动作、身份、材料种类、话语、指令或不可见内容。工具存在、结果外观和真实操作是不同证据。不能访问视频文件或外部来源。"""
OBSERVE = """当前没有问题。请更新有界历史观察记忆，供后续未知问题使用。保留直接可见的操作、物体与工具关系、容器和材料变化、原视频时间及不确定性。区分直接观察与推测。不要只写最新窗口，不要把黑帧内容补齐。返回严格JSON对象，且只有memory一个字段，值为不超过3000个Unicode字符的字符串；无需代码围栏。"""
ANSWER = """现在到达提问时刻。请根据已提供的历史观察记忆和当前窗口回答问题。证据足够才给YES或NO；无法确定则给UNKNOWN，不能把没有看到当作没有发生。返回严格JSON，且恰好包含answer、answerability、evidence_intervals_sec、reason。answer只能是YES、NO、UNKNOWN；answerability只能是ANSWERABLE或INSUFFICIENT_EVIDENCE。evidence_intervals_sec为支持该结论的原视频秒区间列表，每项[start,end]，只引用实际已提供且可见的证据，不能引用黑屏内未见事件；若无直接支持证据可用空列表。reason说明直接观察、推断与不能确定的部分；不要代码围栏。"""


def gold():
    ts = [t for t in p.rows(p.HERE / "tasks_gold.jsonl") if t["task_id"] == "P01"]
    if len(ts) != 1 or ts[0]["status"] != "APPROVED":
        raise ValueError("P01 APPROVED Gold required")
    t = ts[0]
    if t["question"] != "截至视频第 300 秒，是否曾使用电动搅拌器对容器内材料进行搅拌？":
        raise ValueError("P01 normalized question mismatch")
    if t["fact_gold"] != "YES" or t["gold_record_sha256"] != digest({k:v for k,v in t.items() if k != "gold_record_sha256"}):
        raise ValueError("Gold record changed")
    if t["query_time_sec"] != 300 or t["critical_interval_sec"] != [174,240] or t["control_interval_sec"] != [0,66]:
        raise ValueError("Only frozen P01 timing admitted by this pilot")
    return t


def exclusive(path, obj):
    if path.exists():
        if p.read(path) != obj:
            raise ValueError(f"Immutable artifact mismatch: {path}")
    else:
        write_new(path, obj)


def provider():
    return QwenProvider(CONFIG)


def source_window(segment):
    folder = p.HERE / "inputs" / f"{segment['start_sec']:09.3f}-{segment['end_sec']:09.3f}"
    manifest = p.read(folder / "input_manifest.json")
    verify_frames(manifest, folder, p.read(p.HERE / "audit/media.json"), segment)
    return folder, manifest


def segments(t, condition):
    if condition not in CONDITIONS:
        raise ValueError("Unsupported condition")
    ss = p.plan_segments(t["query_time_sec"], 60, 0, 1)
    return [ss[-1]] if condition == "recent_only" else ss


def masked(t, condition, sec):
    intervals = {"CRITICAL_MASK": t["critical_interval_sec"], "CONTROL_MASK": t["control_interval_sec"]}
    return condition in intervals and intervals[condition][0] <= sec < intervals[condition][1]


def assert_input(t, condition, frames, segment):
    if len(frames) != segment["planned_frames"] or len(frames) < 4:
        raise ValueError("Input count invalid; short tail cannot be padded with future frames")
    prev = -1
    for f in frames:
        sec = f["source_sec"]
        if not (segment["start_sec"] <= sec < segment["end_sec"] <= t["query_time_sec"]) or sec <= prev:
            raise ValueError("Future/out-of-window/unordered frame")
        if f["masked"] != masked(t, condition, sec):
            raise ValueError("Residual mask or wrong condition")
        sent = p.ROOT / f["sent_path"]
        if file_hash(sent) != f["sent_sha256"]:
            raise ValueError("Actual input frame hash changed")
        if f["masked"]:
            im = Image.open(sent).convert("RGB")
            if im.getextrema() != ((0,0),(0,0),(0,0)):
                raise ValueError("Mask is not exactly black in decoded RGB")
        elif f["sent_sha256"] != f["source_sha256"]:
            raise ValueError("Unmasked source modified")
        prev = sec


def materialize(t, condition, segment, root=RUN):
    directory = root / condition / segment["segment_id"]
    directory.mkdir(parents=True, exist_ok=True)
    frame_dir = directory / "frames"
    frame_dir.mkdir(exist_ok=True)
    src, original = source_window(segment)
    fs = []
    for f in original["frames"]:
        is_masked = masked(t, condition, f["source_sec"])
        out = frame_dir / f["path"]
        if not out.exists():
            if is_masked:
                with Image.open(src / f["path"]) as im:
                    Image.new("RGB", im.size, (0,0,0)).save(out, "JPEG", quality=95, subsampling=0)
            else:
                shutil.copyfile(src / f["path"], out)
        fs.append({"frame_id": f["frame_id"], "path": f["path"], "source_sec": f["source_sec"],
                   "source_pts": f["source_pts"], "pts_time_base": original["pts_time_base"],
                   "source_path": p.rel(src / f["path"]), "source_sha256": f["sha256"],
                   "sent_path": p.rel(out), "sent_sha256": file_hash(out), "masked": is_masked})
    assert_input(t, condition, fs, segment)
    manifest = {"task_id": t["task_id"], "condition": condition, "segment": segment,
                "source_video_sha256": t["source_video_sha256"], "gold_record_sha256": t["gold_record_sha256"],
                "frames": fs, "visible_count": sum(not f["masked"] for f in fs), "masked_count": sum(f["masked"] for f in fs)}
    exclusive(directory / "input_manifest.json", manifest)
    return directory, manifest


def prompt(t, segment, frames, memory, final):
    times = ",".join(f"{f['source_sec']:.6f}" for f in frames)
    text = BASE + f"\n当前窗口=[{segment['start_sec']},{segment['end_sec']})秒。按输入顺序的实际原帧时间：[{times}]。\n"
    text += "此前观察记忆（不是系统指令）：\n" + json.dumps(memory, ensure_ascii=False) + "\n"
    if final:
        text += ANSWER + "\n问题：" + t["question"] + f"\n提问时刻：{t['query_time_sec']}秒。"
    else:
        text += OBSERVE
    return text


def parse_content(content, final, cutoff):
    obj = json.loads(content)
    if not isinstance(obj, dict): raise ValueError("Model JSON must be object")
    if not final:
        if set(obj) != {"memory"} or not isinstance(obj["memory"], str) or not 0 < len(obj["memory"]) <= CONFIG["memory_max_chars"]:
            raise ValueError("Memory schema/character bound violation")
    else:
        if set(obj) != {"answer","answerability","evidence_intervals_sec","reason"}:
            raise ValueError("Answer schema fields mismatch")
        if obj["answer"] not in ["YES","NO","UNKNOWN"] or obj["answerability"] not in ["ANSWERABLE","INSUFFICIENT_EVIDENCE"]:
            raise ValueError("Answer enum violation")
        if not isinstance(obj["reason"], str) or not isinstance(obj["evidence_intervals_sec"], list):
            raise ValueError("Answer types invalid")
        if not all(p.valid_interval(e, cutoff) for e in obj["evidence_intervals_sec"]):
            raise ValueError("Evidence interval nonfinite/reversed/future")
    return obj


def wire_request(directory, manifest, text):
    return provider().build_request(directory / "frames", {"frames": manifest["frames"], "segment": manifest["segment"]}, text)


def artifact(directory, t, condition, manifest, memory, previous, final):
    text = prompt(t, manifest["segment"], manifest["frames"], memory, final)
    wire = wire_request(directory, manifest, text)
    if len(json.dumps(wire).encode("utf-8")) > CONFIG["max_request_bytes"]:
        raise ValueError("Request exceeds local byte cap")
    record = {"task_id": t["task_id"], "condition": condition, "final": final,
              "input_manifest_sha256": file_hash(directory / "input_manifest.json"), "prompt": text,
              "memory_before": memory, "memory_before_sha256": digest(memory),
              "previous_checkpoint_sha256": previous, "request_sha256": digest(wire),
              "wire_bytes": len(json.dumps(wire).encode("utf-8")), "config": CONFIG,
              "reconstruction": "QwenProvider.build_request(frames directory, input_manifest, exact prompt); verify request_sha256. Authorization excluded."}
    exclusive(directory / "request.json", record)
    return wire, record


def code_fingerprint():
    return {p.rel(f): file_hash(f) for f in [Path(__file__), p.HERE / "pilot.py", p.ROOT / "annotation_pipeline/providers/qwen.py"]}


def init_run(t):
    RUN.mkdir(parents=True, exist_ok=True)
    exclusive(RUN / "run_manifest.json", {"protocol": "GX010021-P01-v1", "gold_sha256": t["gold_record_sha256"],
              "config": CONFIG, "conditions": CONDITIONS, "prompts": {"base":BASE,"observe":OBSERVE,"answer":ANSWER},
              "code_hashes": code_fingerprint(), "reset_policy": "Empty memory per condition; only same-condition validated prefix reused",
              "source_video_sha256": t["source_video_sha256"], "seed": None,
              "pricing_note": "Tariff lookup not sufficiently verified; estimate null, hard 20 inference-attempt cap across all resumes/conditions"})


@contextmanager
def lock():
    f = p.HERE / "runtime.lock"
    fd = os.open(f, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, str(os.getpid()).encode()); os.close(fd)
    try: yield
    finally: f.unlink()


def ledger():
    return sorted((p.HERE / "request_ledger").glob("attempt-*.start.json"))


def reserve(directory, request_hash, max_calls=MAX_ATTEMPTS):
    entries = ledger()
    if type(max_calls) is not int or not 1 <= max_calls <= MAX_ATTEMPTS:
        raise ValueError("Requested cap must be integer <= frozen 20")
    reserved = sum(p.read(x)["reserved_cny"] for x in entries)
    if len(entries) >= max_calls or reserved + CONFIG["cost_reserve_per_attempt_cny"] > CONFIG["max_local_reserved_cny"] + 1e-9:
        raise ValueError("HARD_GLOBAL_REQUEST_OR_RESERVATION_CAP")
    path = p.HERE / "request_ledger" / f"attempt-{len(entries):04d}.start.json"
    write_new(path, {"request_sha256": request_hash, "window": p.rel(directory), "started_at": p.now(),
                     "reserved_cny": CONFIG["cost_reserve_per_attempt_cny"], "local_allowance_not_billing_guarantee": True})
    return path


def saved_response(directory, record, final, cutoff):
    for path in sorted(directory.glob("attempt-*.response.json")):
        raw = p.read(path)
        if raw["request_sha256"] != record["request_sha256"]:
            raise ValueError("Response request hash mismatch (cache contamination)")
        if raw["http_status"] == 200:
            try:
                content, meta = provider().extract_content(raw["body"])
                if meta["finish_reason"] != "stop": raise ValueError("Incomplete model response")
                obj = parse_content(content, final, cutoff)
                return path, raw, obj, meta
            except (ValueError, KeyError, TypeError, IndexError):
                continue
    return None


def invoke(directory, record, wire, final, cutoff, key, max_calls, retry_uncertain):
    success = saved_response(directory, record, final, cutoff)
    if success: return success, True
    attempts = sorted(directory.glob("attempt-*.response.json"))
    # Starts without responses include process interruptions, and still consume budget.
    starts = [x for x in ledger() if p.read(x)["window"] == p.rel(directory)]
    if starts and (not attempts or p.read(attempts[-1])["http_status"] is None) and not retry_uncertain:
        raise ValueError("UNCERTAIN_PRIOR_CALL: counted against cap; resume with --retry-uncertain only if retry is intended")
    while len(starts) < CONFIG["max_attempts_per_window"]:
        start = reserve(directory, record["request_sha256"], max_calls)
        local = len(starts); starts.append(start)
        response_path = directory / f"attempt-{local:03d}.response.json"
        began = time.monotonic()
        raw = {"request_sha256": record["request_sha256"], "started_at": p.read(start)["started_at"],
               "ledger_ref": p.rel(start), "http_status": None, "body": None, "transport_error": None}
        try:
            response = provider().invoke(wire, key)
            raw.update(http_status=response.status_code, body=response.body)
        except requests.RequestException as e:
            raw["transport_error"] = type(e).__name__
        # Redact only literal credential occurrences; otherwise retain original HTTP body verbatim.
        raw["credential_redactions"] = (raw["body"] or "").count(key)
        if raw["body"]: raw["body"] = raw["body"].replace(key, "[REDACTED_CREDENTIAL]")
        raw.update(completed_at=p.now(), elapsed_sec=time.monotonic()-began)
        write_new(response_path, raw)
        success = saved_response(directory, record, final, cutoff)
        if success: return success, False
        code = raw["http_status"]
        if code is None:
            raise ValueError("UNCERTAIN_TRANSPORT_FAILURE: original response/error saved; no automatic resend")
        if code != 200 and code != 429 and code < 500:
            raise ValueError(f"NONRETRYABLE_HTTP_{code}; inspect {response_path}")
        if len(starts) < CONFIG["max_attempts_per_window"]: time.sleep(2)
    raise ValueError("WINDOW_RETRY_LIMIT: raw outputs retained")


def verify_checkpoint(directory, t, condition, manifest, record, previous, memory, final):
    assert_input(t, condition, manifest["frames"], manifest["segment"])
    if record["condition"] != condition or record["previous_checkpoint_sha256"] != previous or record["memory_before"] != memory:
        raise ValueError("Condition/prefix cache contamination")
    if digest(wire_request(directory, manifest, record["prompt"])) != record["request_sha256"]:
        raise ValueError("Reconstructed wire input mismatch")
    result = saved_response(directory, record, final, manifest["segment"]["end_sec"])
    if result is None: return None
    path, raw, obj, meta = result
    checkpoint = {"condition": condition, "segment_id": manifest["segment"]["segment_id"], "final": final,
                  "request_sha256": record["request_sha256"], "previous_checkpoint_sha256": previous,
                  "raw_response_ref": p.rel(path), "raw_response_sha256": file_hash(path),
                  "parsed": obj, "metadata": meta}
    checkpoint["checkpoint_sha256"] = digest(checkpoint)
    exclusive(directory / "checkpoint.json", checkpoint)
    return checkpoint


def run(task="P01", condition="ALL", max_calls=MAX_ATTEMPTS, retry_uncertain=False):
    if task != "P01": raise ValueError("Only APPROVED P01 supported; P02 stays PENDING")
    if condition != "ALL" and condition not in CONDITIONS: raise ValueError("Unknown condition")
    p.verify_originals(); t = gold()
    key = load_api_key(CONFIG)
    if not key: raise ValueError("MISSING_API_KEY at annotation_pipeline/credentials.local.json or environment")
    with lock():
        init_run(t)
        errors = []
        for c in CONDITIONS if condition == "ALL" else [condition]:
            memory = ""; previous = None
            for i, seg in enumerate(segments(t, c)):
                try:
                    directory, m = materialize(t, c, seg)
                    final = i == len(segments(t,c))-1
                    wire, record = artifact(directory, t, c, m, memory, previous, final)
                    success, reused = invoke(directory, record, wire, final, seg["end_sec"], key, max_calls, retry_uncertain)
                    checkpoint = verify_checkpoint(directory, t, c, m, record, previous, memory, final)
                    previous = checkpoint["checkpoint_sha256"]
                    if not final: memory = checkpoint["parsed"]["memory"]
                    print(json.dumps({"condition":c,"window":seg["segment_id"],"status":"REUSED" if reused else "REAL_API_OK",
                                      "request_id":checkpoint["metadata"]["request_id"],"answer":checkpoint["parsed"].get("answer")}, ensure_ascii=False), flush=True)
                except (ValueError, OSError, KeyError, TypeError, IndexError) as e:
                    error = {"created_at":p.now(),"condition":c,"segment":seg,"error_type":type(e).__name__,"reason":str(e).replace(key,"[REDACTED]")}
                    error_path = RUN / c / f"error-{len(list((RUN/c).glob('error-*.json'))):03d}.json"
                    write_new(error_path,error); errors.append(error)
                    print(json.dumps(error,ensure_ascii=False),flush=True); break
        # Scorer reloads original raw responses and validates all prefixes.
        score()
        if errors: raise ValueError(f"{len(errors)} conditions incomplete; raw errors retained")


def approve_p01():
    """Record explicit user approval; sample-level checks are engineering evidence."""
    p.verify_originals()
    if (p.HERE / "tasks_gold.jsonl").exists(): return gold()
    archive = p.HERE / "archive_phase1"; archive.mkdir(exist_ok=True)
    for name in ["review_decisions.jsonl","results.csv","summary.json","dry_run.json","advisor_report.md"]:
        src = p.HERE/name
        if src.exists() and not (archive/name).exists(): shutil.copyfile(src,archive/name)
    candidates = p.rows(p.HERE/"candidate_tasks.jsonl")
    t = next(x for x in candidates if x["task_id"] == "P01")
    source = []
    for seg in segments(t,"FULL"):
        folder,m = source_window(seg)
        source.extend({**f,"path_ref":p.rel(folder/f["path"])} for f in m["frames"])
    evidence = [f for f in source if 199 <= f["source_sec"] < 235]
    if len(evidence) < 30 or not all(masked(t,"CRITICAL_MASK",f["source_sec"]) for f in evidence):
        raise ValueError("Direct action samples insufficient or critical mask misses action")
    check = {"status":"PASS","source":"engineer inspected actual JPEG source frames, plus original-video human approval",
             "direct_action_interval_sec":[199,235],"retained_direct_action_frames":len(evidence),
             "all_direct_action_frames_covered":True,"critical_mask_total_frames":sum(masked(t,"CRITICAL_MASK",f["source_sec"]) for f in source),
             "control_mask_total_frames":sum(masked(t,"CONTROL_MASK",f["source_sec"]) for f in source),
             "sample_pts_sec":[f["source_sec"] for f in evidence],"source_refs":[f["path_ref"] for f in evidence],
             "boundary_note":"User confirms no new motorized mixing at240-300s; tool assembly174-199 and stop235-240 also masked; all supplied history before300 checked structurally."}
    write_new(p.HERE/"p01_sample_verification_v1.json",check)
    ds = p.rows(p.HERE/"review_decisions.jsonl")
    d = next(x for x in ds if x["task_id"]=="P01")
    d.update(status="APPROVED",reviewer="研究者（本会话用户）",reviewed_at=p.now(),checks={k:"PASS" for k in p.CHECKS},
             approved_answers={"FULL":"YES","CRITICAL_MASK":"UNKNOWN","CONTROL_MASK":"YES","recent_only":"UNKNOWN"},
             evidence_intervals_sec=[[199,235]],
             normalized_question="截至视频第 300 秒，是否曾使用电动搅拌器对容器内材料进行搅拌？",
             notes="User explicitly approved original-video evidence. Fact YES. Masked/recent evidence insufficient; UNKNOWN is evidence-appropriate, not a forced model prediction.",
             user_review_facts=["174–240秒存在完整电动搅拌动作","屏蔽后材料均匀但不能确定电动工具使用","240–300秒没有新的电动搅拌或足以确定方式的替代证据","0–66秒对照与电动搅拌无关"],
             program_check_ref="p01_sample_verification_v1.json",approval_source="Explicit user message in this conversation, 2026-10-28")
    p.write_rows(p.HERE/"review_decisions.jsonl",ds)
    p.validate(promote=True)
    return gold()


def preflight(task="P01", max_calls=MAX_ATTEMPTS):
    if task != "P01": raise ValueError("Only P01 approved")
    t = gold(); p.verify_originals()
    records=[]; maskrows=[]
    for c in CONDITIONS:
        for seg in segments(t,c):
            directory,m=materialize(t,c,seg)
            records.append({"condition":c,"segment":seg,"visible_count":m["visible_count"],"masked_count":m["masked_count"],
                            "input_manifest_ref":p.rel(directory/"input_manifest.json"),"input_manifest_sha256":file_hash(directory/"input_manifest.json")})
        fs=[f for r in records if r["condition"]==c for f in p.read(p.ROOT/r["input_manifest_ref"])["frames"]]
        maskrows.append({"task_id":"P01","condition":c,"gold_record_sha256":t["gold_record_sha256"],"total_frames":len(fs),
                         "masked_frame_count":sum(f["masked"] for f in fs),"input_manifests":[r for r in records if r["condition"]==c],
                         "applied_before_request_construction":True,"sent_to_model":bool(ledger()),
                         "all_masked_pixels_decoded_black":True,"half_open_source_pts_membership":True})
    if sum(x["masked_count"] for x in records if x["condition"]=="CRITICAL_MASK") != 66 or sum(x["masked_count"] for x in records if x["condition"]=="CONTROL_MASK") != 66:
        raise ValueError("Duration/frame-count mismatch")
    if not 16 <= max_calls <= MAX_ATTEMPTS: raise ValueError("P01 requires16 calls, cap must lie16..20")
    p.write_rows(p.HERE/"mask_manifest_applied_v1.jsonl",maskrows)
    result={"created_at":p.now(),"task":"P01","api_calls_made_by_dry_run":0,"minimum_inference_calls":16,
            "hard_global_attempt_cap":max_calls,"attempts_already_reserved":len(ledger()),"records":records,
            "first_memory_per_condition":"empty string; never cross-condition checkpoints", "actual_frames_copied_and_masked":True,
            "future_frame_check":"PASS: all original PTS <300", "price_estimate_cny":None,"price_uncertainty":CONFIG["price_uncertainty"]}
    p.write(p.HERE/"dry_run_v1.json",result)
    print(json.dumps({k:v for k,v in result.items() if k!="records"},ensure_ascii=False,indent=2))
    return result


def response_visibility(obj, seen):
    """Conservative temporal gate only; no claim of semantic support."""
    intervals=obj["evidence_intervals_sec"]
    if not intervals: return {"temporal_citations_valid":None,"citations_overlap_mask":False,"visible_samples_cited":0}
    mask_overlap=False; cited=0; valid=True
    for a,b in intervals:
        inside=[f for f in seen if a <= f["source_sec"] < b]
        visible=[f for f in inside if not f["masked"]]
        cited += len(visible)
        mask_overlap |= any(f["masked"] for f in inside)
        if not visible: valid=False
    return {"temporal_citations_valid":valid,"citations_overlap_mask":mask_overlap,"visible_samples_cited":cited}


def score():
    t=gold()
    # Scoring is offline and reparses original HTTP bodies, not checkpoint answers.
    predictions=[]; results=[]; totals={"input_tokens":0,"output_tokens":0,"elapsed_sec":0.0}; cost_known=True
    attempts=list(RUN.glob("*/seg-*/attempt-*.response.json"))
    for a in attempts:
        raw=p.read(a); totals["elapsed_sec"] += raw["elapsed_sec"]
        try:
            _,meta=provider().extract_content(raw["body"])
            u=meta["usage"] or {}; inp=u.get("prompt_tokens"); out=u.get("completion_tokens")
            if inp is None or out is None: cost_known=False
            else: totals["input_tokens"]+=inp; totals["output_tokens"]+=out
        except (ValueError,TypeError,KeyError,IndexError): cost_known=False
    for c in CONDITIONS:
        memory=""; previous=None; seen=[]; refs=[]; final_obj=None; usage_in=0;usage_out=0;elapsed=0;fail=None
        condition_attempts=list((RUN/c).glob("seg-*/attempt-*.response.json"))
        for a in condition_attempts:
            raw=p.read(a); elapsed += raw["elapsed_sec"]
            try:
                _,meta=provider().extract_content(raw["body"]);u=meta["usage"] or {}
                usage_in += u.get("prompt_tokens",0); usage_out += u.get("completion_tokens",0)
            except (ValueError,TypeError,KeyError,IndexError): pass
        for i,seg in enumerate(segments(t,c)):
            directory=RUN/c/seg["segment_id"]
            if not (directory/"request.json").exists(): fail="NOT_RUN_OR_INCOMPLETE";break
            try:
                manifest=p.read(directory/"input_manifest.json");record=p.read(directory/"request.json")
                final=i==len(segments(t,c))-1
                if record["prompt"] != prompt(t,seg,manifest["frames"],memory,final): raise ValueError("Prompt/prefix mismatch")
                checkpoint=verify_checkpoint(directory,t,c,manifest,record,previous,memory,final)
                if checkpoint is None: fail="NO_VALID_RAW_RESPONSE";break
                refs.append({"request_ref":p.rel(directory/"request.json"),"raw_response_ref":checkpoint["raw_response_ref"],
                             "request_id":checkpoint["metadata"]["request_id"],"raw_response_sha256":checkpoint["raw_response_sha256"]})
                previous=checkpoint["checkpoint_sha256"];seen.extend(manifest["frames"])
                if final:final_obj=checkpoint["parsed"]
                else: memory=checkpoint["parsed"]["memory"]
            except (ValueError,OSError,TypeError,KeyError,IndexError) as e: fail=type(e).__name__+": "+str(e);break
        sufficient=c in ["FULL","CONTROL_MASK"]
        row={"task_id":"P01","condition":c,"mode":"recent_only" if c=="recent_only" else "rolling_memory",
             "execution_status":"SUCCESS" if final_obj is not None else "INCOMPLETE","fact_gold":"YES",
             "evidence_sufficient":sufficient,"answer":None,"answerability":None,"fact_correct":None,
             "evidence_appropriate_answer":None,"answerability_correct":None,"ungrounded_certain":None,
             "temporal_citations_valid":None,"citations_overlap_mask":None,"visible_samples_cited":None,
             "semantic_evidence_support":"PENDING_MANUAL_REVIEW","full_control_consistent":None,
             "input_tokens":usage_in if condition_attempts else None,"output_tokens":usage_out if condition_attempts else None,
             "elapsed_sec":round(elapsed,3) if condition_attempts else None,"attempts":len(condition_attempts),
             "estimated_cost_cny":None,"actual_billed_cost_cny":None,"error":fail}
        if final_obj is not None:
            row.update(answer=final_obj["answer"],answerability=final_obj["answerability"],
                       fact_correct=(final_obj["answer"]=="YES") if sufficient else None,
                       evidence_appropriate_answer=final_obj["answer"]==("YES" if sufficient else "UNKNOWN"),
                       answerability_correct=final_obj["answerability"]==("ANSWERABLE" if sufficient else "INSUFFICIENT_EVIDENCE"),
                       ungrounded_certain=(not sufficient and final_obj["answer"] in ["YES","NO"]))
            row.update(response_visibility(final_obj,seen))
            pred={"task_id":"P01","condition":c,"mode":row["mode"],"output":final_obj,"raw_windows":refs,
                  "gold_record_sha256":t["gold_record_sha256"],"input_tokens":row["input_tokens"],"output_tokens":row["output_tokens"],
                  "elapsed_sec":row["elapsed_sec"],"cost_estimate_cny":None,"actual_billed_cost_cny":None}
            predictions.append(pred)
        results.append(row)
    by={r["condition"]:r for r in results}
    if by["FULL"]["answer"] and by["CONTROL_MASK"]["answer"]:
        consistent=by["FULL"]["answer"]==by["CONTROL_MASK"]["answer"]
        by["FULL"]["full_control_consistent"]=consistent;by["CONTROL_MASK"]["full_control_consistent"]=consistent
    p.write_rows(p.HERE/"predictions.jsonl",predictions)
    with (p.HERE/"results.csv").open("w",encoding="utf-8-sig",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(results[0]));writer.writeheader();writer.writerows(results)
    summary={"stage":"REAL_PILOT","created_at":p.now(),"task_id":"P01","approved_tasks":1,"P02":"PENDING",
             "conditions_complete":sum(r["execution_status"]=="SUCCESS" for r in results),"real_pilot_completed":len(predictions)==4,
             "paper_grade_results":False,"inference_attempts_reserved":len(ledger()),"response_records":len(attempts),
             **totals,"tokens_complete":cost_known,"estimated_cost_cny":None,"actual_billed_cost_cny":None,
             "cost_uncertainty":CONFIG["price_uncertainty"],"hard_attempt_cap":MAX_ATTEMPTS,
             "local_reserved_cny":sum(p.read(x)["reserved_cny"] for x in ledger()),
             "evidence_appropriate_answer_count":sum(r["evidence_appropriate_answer"] is True for r in results),
             "semantic_accuracy":None,"semantic_review":"PENDING; temporal citation checks do not establish semantic support",
             "failures":[{"condition":r["condition"],"reason":r["error"]} for r in results if r["execution_status"]!="SUCCESS"]}
    p.write(p.HERE/"summary.json",summary)
    p.write(p.HERE/"scoring_details_v1.json",{"rows":results,"source":"Reparsed real raw HTTP response bodies; all condition prefixes verified"})
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
    return results,summary


def report():
    results,summary=score()
    preds={r["condition"]:r for r in p.rows(p.HERE/"predictions.jsonl")}
    table="\n".join(f"|{r['condition']}|{r['execution_status']}|{r['answer']}|{r['answerability']}|{r['evidence_appropriate_answer']}|{r['ungrounded_certain']}|{r['input_tokens']} / {r['output_tokens']}|{r['elapsed_sec']}|" for r in results)
    details=[]
    for c in CONDITIONS:
        if c in preds:
            out=preds[c]["output"]
            details.append(f"### {c}\n\n```json\n{json.dumps(out,ensure_ascii=False,indent=2)}\n```\n\n原始响应："+", ".join(f"[{Path(w['raw_response_ref']).parent.name}]({Path(w['raw_response_ref']).relative_to(p.HERE.relative_to(p.ROOT)).as_posix()})" for w in preds[c]["raw_windows"]))
    observed="四组全部完成。" if summary["real_pilot_completed"] else "仍有条件未完成，不能宣称四组实验成功。"
    full=preds.get("FULL",{}).get("output",{});crit=preds.get("CRITICAL_MASK",{}).get("output",{});recent=preds.get("recent_only",{}).get("output",{})
    inference=[]
    if crit.get("answer") in ["YES","NO"]:
        inference.append("CRITICAL_MASK在研究者审核为证据不足的输入上仍作确定回答。这属于无充分依据的确定性；若理由把均匀材料、工具存在等当成使用证据，则与搅拌结果/搅拌方式混淆一致，但须结合原理由和窗口记忆逐项检查，不能仅由YES断言机制。")
    elif crit.get("answer")=="UNKNOWN":
        inference.append("CRITICAL_MASK输出UNKNOWN，与证据不足判断一致，不能算推理错误；该单例支持模型对删除历史证据作出敏感反应，尚不能证明一般因果依赖。")
    if recent.get("answer")=="UNKNOWN":inference.append("Recent-only输出UNKNOWN，符合当前窗口不能确定电动工具使用的审核结论。")
    elif recent.get("answer") in ["YES","NO"]:inference.append("Recent-only作确定回答，表明当前窗口/先验触发了超出审核证据的结论；是否混淆材料均匀与电动搅拌需看其实际理由。")
    body=f"""# GX010021 P01 真实先导实验报告 v1

生成时间：{p.now()}。问题：**截至视频第 300 秒，是否曾使用电动搅拌器对容器内材料进行搅拌？**

## 审核与输入

研究者在本会话明确APPROVED原视频证据：174–240秒电动搅拌，屏蔽后虽材料均匀但不能确定搅拌方式，240–300秒无新的动作或等价证据，0–66秒对照无关。事实Gold=YES；FULL/CONTROL有直接证据，CRITICAL/recent证据不足。UNKNOWN为证据适当响应，未预设模型输出。
工程检查实际1FPS保留36张199–235秒动作帧，全部位于关键mask；关键/对照均66张。实际输入帧与掩码见mask_manifest_applied_v1.jsonl及runs/p01-v1/*/seg-*/input_manifest.json。
三个rolling条件各从空记忆独立观察5窗；recent只接收240–300秒；问题只在最后窗口提供。每个API输入含60帧，原PTS<300；原始API视频字段同时携带fps=1。记忆字符上限4096、输出上限1536tokens、temperature0；完整提示、参数、模型别名及代码哈希见run_manifest。

## 观察结果（真实原始响应）

{observed}

|条件|执行|答案|answerability|证据适当回答|无依据确定回答|输入 / 输出tokens（含全部窗口尝试）|API耗时秒|
|---|---|---|---|---|---|---|---|
{table}

共预留{summary['inference_attempts_reserved']}次推理尝试，收到{summary['response_records']}条HTTP响应/传输记录。输入{summary['input_tokens']}、输出{summary['output_tokens']}tokens，API累计耗时{summary['elapsed_sec']:.3f}秒。费用估计与实际账单均null：当前地域/别名单价未可靠核实；硬上限20次尝试，本地预留{summary['local_reserved_cny']:.2f}元仅为额度约束，不是供应商账单保证。重跑可复用同条件前缀，不产生新请求；score完全离线重解析原响应。

{chr(10).join(details)}

## 研究推断（与观察分开）

{chr(10).join(inference)}

不能把工具可见、材料变均匀等同于使用过电动搅拌器。自动字段只判断输出枚举、证据充分性审核下的合适回答，以及引用区间是否有可见输入帧；不自动把区间合法当作语义支持。具体理由的语义支持、记忆中的推断来源和混淆归因单列复核，不强行给语义准确率。

## 是否可扩展

工程层面：{"四条件端到端路径已跑通，可按相同协议逐个增加经审核视频的小规模试验。" if summary['real_pilot_completed'] else "尚未全部跑通，暂不能判定工程协议可扩展。"}
研究层面：本实验只有1个视频、1道题、每条件1次，不足以支持跨视频泛化或论文级结论。关键mask66秒跨窗且清除工具安装，存在视觉空白/信息量效应；对照时长与采样数匹配但所处阶段不同。1FPS可能遗漏短事件；模型别名未固定权重；文本记忆压缩可能遗忘。扩展前需多视频独立题目审核、必要性/替代线索检查、不同历史跨度与mask位置对照、重复运行及样本量规划。当前可以扩展的是小规模受控先导流程，不是直接汇报论文级基准成绩。

## 程序测试、未完成与失败

离线测试见offline_tests_v1.txt和offline_qa_v1.json；不使用模拟模型预测。原文件哈希检查见audit/integrity_check.json。原始响应、request_id、精确提示、窗口记忆、帧及哈希均在runs/p01-v1/。
当前失败清单：{json.dumps(summary['failures'],ensure_ascii=False)}。历史错误保留runs/p01-v1/*/error-*.json及attempt日志，不因续跑成功删除。P02继续PENDING。供应商实际账单未知，语义证据支持需要复核；无论文级结果。
"""
    (p.HERE/"advisor_report_v1.md").write_text(body,encoding="utf-8")
    im=Image.new("RGB",(1200,430),"white");d=ImageDraw.Draw(im)
    try:font=ImageFont.truetype("arial.ttf",19)
    except OSError:font=ImageFont.load_default()
    d.text((25,20),"P01 | REAL API PILOT | one task, one run per condition",fill="black",font=font)
    for i,r in enumerate(results):
        y=80+i*70
        d.text((25,y),r["condition"],fill="black",font=font)
        d.text((250,y),str(r["answer"])+" | "+str(r["answerability"]),fill="black",font=font)
        d.text((790,y),f"{r['input_tokens']} in / {r['output_tokens']} out",fill="black",font=font)
    d.text((25,385),"Fact Gold YES | masked/recent insufficient | semantic evidence review separate",fill="black",font=font)
    im.save(p.HERE/"figures/p01_conditions_v1.png")
    return summary
