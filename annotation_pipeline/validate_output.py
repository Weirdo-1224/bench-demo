from __future__ import annotations

import argparse
from copy import deepcopy
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator

from .common import PACKAGE, file_hash, read_json
from .media import verify_frames

SCHEMA_PATH = PACKAGE / "schemas" / "segment_observation.schema.json"


def model_schema():
    schema = read_json(SCHEMA_PATH)
    return {"$schema": schema["$schema"], "$ref": "#/$defs/model_response", "$defs": schema["$defs"]}


def finite_numbers(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Nonfinite numeric output")
    if isinstance(value, dict):
        for item in value.values():
            finite_numbers(item)
    if isinstance(value, list):
        for item in value:
            finite_numbers(item)


def validate_model(value, segment, manifest):
    finite_numbers(value)
    Draft202012Validator(model_schema()).validate(value)
    frames = {f["frame_id"]: f for f in manifest["frames"]}
    duration = segment["end_sec"] - segment["start_sec"]
    ids = set()
    for event in value["events"]:
        if event["local_event_id"] in ids:
            raise ValueError("Duplicate local_event_id")
        ids.add(event["local_event_id"])
        if not 0 <= event["start_sec"] <= event["end_sec"] <= duration:
            raise ValueError("Event outside clip-local time range")
        evidence = event["evidence"]
        if not event["start_sec"] <= evidence["start_sec"] <= evidence["end_sec"] <= event["end_sec"]:
            raise ValueError("Evidence must be within its event")
        for frame_id in evidence["frame_ids"]:
            if frame_id not in frames:
                raise ValueError("Evidence refers to a frame not supplied to model")
            if not evidence["start_sec"] - 1e-6 <= frames[frame_id]["clip_local_sec"] <= evidence["end_sec"] + 1e-6:
                raise ValueError("Evidence frame outside evidence range")
        if event["observability"] != "direct" and not event["uncertainties"]:
            raise ValueError("Partial/unobservable observations must explain uncertainty")


def structure(value, media, segment, manifest, provenance, episode_id):
    validate_model(value, segment, manifest)
    frames = {f["frame_id"]: f for f in manifest["frames"]}
    events = []
    offset = segment["start_sec"]
    for original in value["events"]:
        event = deepcopy(original)
        # Unique within a run, explicitly not a fused global identity.
        event["event_id"] = f'{provenance["run_id"]}:{segment["segment_id"]}:{event["local_event_id"]}'
        event["clip_local_start_sec"] = event["start_sec"]
        event["clip_local_end_sec"] = event["end_sec"]
        event["start_sec"] += offset
        event["end_sec"] += offset
        event["time_precision"] = "APPROXIMATE_SAMPLED"
        event["provenance"] = deepcopy(provenance)
        evidence = event["evidence"]
        evidence["clip_local_start_sec"] = evidence["start_sec"]
        evidence["clip_local_end_sec"] = evidence["end_sec"]
        evidence["start_sec"] += offset
        evidence["end_sec"] += offset
        evidence["frame_refs"] = [deepcopy(frames[f]) for f in evidence["frame_ids"]]
        events.append(event)
    fields = ("path", "sha256", "duration_sec", "width", "height", "fps", "time_base", "stream_start_sec", "has_audio")
    return {"schema_version": "0.1", "episode_id": episode_id, "annotation_status": "CANDIDATE",
            "media": {k: media[k] for k in fields}, "segment": segment,
            "input_manifest_ref": "input/input_manifest.json", "provenance": provenance,
            "events": events, "unknowns": value["unknowns"],
            "deferred_layers": {"L1": None, "L3": None, "L4": None, "L5": None}}


def safe_ref(directory: Path, ref: str) -> Path:
    path = (directory / ref).resolve()
    if not path.is_relative_to(directory.resolve()) or not path.is_file():
        raise ValueError(f"Missing or unsafe artifact ref: {ref}")
    return path


def validate_candidate(value, directory: Path):
    finite_numbers(value)
    Draft202012Validator(read_json(SCHEMA_PATH)).validate(value)
    segment, media, provenance = value["segment"], value["media"], value["provenance"]
    if not 0 <= segment["start_sec"] < segment["end_sec"] <= media["duration_sec"]:
        raise ValueError("Segment outside original video")
    source = Path(media["path"])
    if not source.is_file() or file_hash(source) != media["sha256"]:
        raise ValueError("Original video missing or changed")
    manifest_path = safe_ref(directory, value["input_manifest_ref"])
    manifest = read_json(manifest_path)
    verify_frames(manifest, manifest_path.parent, media, segment)
    raw = safe_ref(directory, provenance["raw_response_ref"])
    if file_hash(raw) != provenance["raw_response_sha256"]:
        raise ValueError("Raw response hash mismatch")
    response = read_json(raw)
    if not 200 <= response["status_code"] < 300 or response["request_sha256"] != provenance["request_sha256"]:
        raise ValueError("Candidate lacks a matching successful response")
    request = read_json(safe_ref(directory, "request.json"))
    if request["request_sha256"] != provenance["request_sha256"] or request["frames"] != manifest["frames"]:
        raise ValueError("Request/input trace mismatch")
    run = read_json(safe_ref(directory.parent, "run_manifest.json"))
    for key in ("run_id", "prompt_sha256", "schema_sha256", "config_sha256"):
        if run[key] != provenance[key]:
            raise ValueError(f"Run provenance mismatch: {key}")
    for key, field in (("model", "model_id"), ("model_version", "model_version"), ("provider", "provider"), ("endpoint", "endpoint")):
        if run["config"][key] != provenance[field]:
            raise ValueError("Provider/model provenance mismatch")
    model_events = []
    original_frames = {f["frame_id"]: f for f in manifest["frames"]}
    ids = set()
    for event in value["events"]:
        if event["event_id"] in ids or event["provenance"] != provenance:
            raise ValueError("Duplicate event identity or altered provenance")
        ids.add(event["event_id"])
        expected_id = f'{provenance["run_id"]}:{segment["segment_id"]}:{event["local_event_id"]}'
        if event["event_id"] != expected_id:
            raise ValueError("Invalid run-scoped event identity")
        for item in (event, event["evidence"]):
            for side in ("start", "end"):
                if abs(item[f"{side}_sec"] - segment["start_sec"] - item[f"clip_local_{side}_sec"]) > 1e-7:
                    raise ValueError("Clip-local/source mapping mismatch")
        refs = event["evidence"]["frame_refs"]
        if refs != [original_frames[f] for f in event["evidence"]["frame_ids"]]:
            raise ValueError("Evidence frame refs do not match actual model input")
        model_event = {k: deepcopy(event[k]) for k in read_json(SCHEMA_PATH)["$defs"]["model_event"]["required"]}
        model_event["start_sec"], model_event["end_sec"] = event["clip_local_start_sec"], event["clip_local_end_sec"]
        ev = event["evidence"]
        model_event["evidence"] = {"start_sec": ev["clip_local_start_sec"], "end_sec": ev["clip_local_end_sec"], "frame_ids": ev["frame_ids"]}
        model_events.append(model_event)
    reconstructed = {"time_basis": "clip_local_seconds", "events": model_events, "unknowns": value["unknowns"]}
    validate_model(reconstructed, segment, manifest)
    # Verify that the structured observations actually come from the retained response.
    from .providers import get_provider
    content, metadata = get_provider(run["config"]).extract_content(response["body"])
    if reconstructed != json.loads(content) or metadata["returned_model"] != provenance["returned_model"]:
        raise ValueError("Candidate content differs from retained model response")
    return {"status": "PASS", "event_count": len(value["events"]), "input_frames": len(manifest["frames"]),
            "semantic_verification": "NOT_REVIEWED; structural and trace validation only"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate_candidate(read_json(args.candidate), args.candidate.parent), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
