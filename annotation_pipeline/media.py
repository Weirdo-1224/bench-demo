from __future__ import annotations

from fractions import Fraction
import math
from pathlib import Path
import re
import subprocess

from .common import file_hash, read_json, write_new


def plan_segments(duration, window, overlap, fps, start=0):
    if not all(math.isfinite(x) for x in (duration, window, overlap, fps, start)):
        raise ValueError("Nonfinite segment parameter")
    if duration <= 0 or window <= 0 or fps <= 0 or not 0 <= overlap < window or not 0 <= start < duration:
        raise ValueError("Invalid segment parameters")
    segments = []
    cursor = start
    while cursor < duration:
        end = min(cursor + window, duration)
        segments.append({"segment_id": f"seg-{len(segments):04d}", "start_sec": round(cursor, 9),
                         "end_sec": round(end, 9), "planned_frames": math.ceil((end - cursor) * fps),
                         "sample_fps": fps})
        if end == duration:
            break
        cursor += window - overlap
    return segments


def verify_frames(manifest, directory: Path, media, segment):
    if manifest["source_sha256"] != media["sha256"] or manifest["segment"] != segment:
        raise ValueError("Frame cache source/segment mismatch")
    frames = manifest["frames"]
    if len(frames) != segment["planned_frames"]:
        raise ValueError("Incomplete sampling grid (missing input frames)")
    base = Fraction(manifest["pts_time_base"])
    previous = -1.0
    for i, frame in enumerate(frames):
        source_sec = float(frame["source_pts"] * base) - media["stream_start_sec"]
        target = segment["start_sec"] + i / segment["sample_fps"]
        # For CFR, selected source frames must be at/just after each grid point.
        # Reject irregular/undersampled media rather than inventing coverage.
        if not segment["start_sec"] <= source_sec < segment["end_sec"] or source_sec <= previous:
            raise ValueError("PTS outside source window or out of order")
        if abs(source_sec - frame["source_sec"]) > 1e-7 or abs(source_sec - segment["start_sec"] - frame["clip_local_sec"]) > 1e-7:
            raise ValueError("PTS mapping mismatch")
        if source_sec < target - 1e-7 or source_sec - target > 1 / media["fps"] + 1e-6:
            raise ValueError("Sampling grid drift exceeds one source frame")
        path = (directory / frame["path"]).resolve()
        if not path.is_relative_to(directory.resolve()) or not path.is_file() or file_hash(path) != frame["sha256"]:
            raise ValueError("Missing/changed/unsafe frame path")
        if frame["frame_id"] != f"frame-{i:04d}":
            raise ValueError("Invalid frame identity")
        previous = source_sec
    return frames


def extract_frames(video: Path, media, segment, directory: Path, config):
    manifest_path = directory / "input_manifest.json"
    if manifest_path.exists():
        manifest = read_json(manifest_path)
        verify_frames(manifest, directory, media, segment)
        return manifest
    # Reuse is allowed only for a complete, hashed manifest; never overwrite partial files.
    if directory.exists():
        raise ValueError(f"Incomplete frame extraction at {directory}; preserve it and use a new run ID")
    directory.mkdir(parents=True)
    start = segment["start_sec"] + media["stream_start_sec"]
    end = segment["end_sec"] + media["stream_start_sec"]
    fps = segment["sample_fps"]
    select = (f"gte(t,{start})*lt(t,{end})*"
              f"if(isnan(prev_selected_t),1,gt(floor((t-{start})*{fps}),floor((prev_selected_t-{start})*{fps})))")
    command = [config["ffmpeg"], "-hide_banner", "-nostdin", "-n", "-xerror", "-copyts", "-t", str(segment["end_sec"] + 1), "-i", str(video),
               "-map", "0:v:0", "-an",
               "-vf", f"select='{select}',showinfo", "-fps_mode", "vfr", "-q:v", "2",
               str(directory / "frame-%04d.jpg")]
    result = subprocess.run(command, capture_output=True, timeout=config["media_timeout_sec"])
    log = result.stderr.decode("utf-8", errors="replace")
    (directory / "ffmpeg.log").write_text(log, encoding="utf-8")
    if result.returncode:
        raise ValueError("Frame extraction failed; inspect ffmpeg.log")
    match = re.search(r"config in time_base:\s*(\d+/\d+)", log)
    if not match:
        raise ValueError("Missing decoded frame time base")
    time_base = match.group(1)
    pts = [int(p) for p in re.findall(r"\bn:\s*\d+\s+pts:\s*(-?\d+)\s+pts_time:", log)]
    files = sorted(directory.glob("frame-*.jpg"))
    if len(pts) != len(files):
        raise ValueError("Decoded PTS and frame file count disagree")
    frames = []
    for i, (point, path) in enumerate(zip(pts, files)):
        sec = float(point * Fraction(time_base)) - media["stream_start_sec"]
        frames.append({"frame_id": f"frame-{i:04d}", "path": path.name, "source_pts": point,
                       "source_sec": sec, "clip_local_sec": sec - segment["start_sec"],
                       "sha256": file_hash(path)})
    manifest = {"source_sha256": media["sha256"], "segment": segment, "pts_time_base": time_base,
                "input_mode": "sampled_video_frames", "command": command, "frames": frames,
                "coverage": "ONLY_LISTED_FRAMES; intervals between samples unobserved"}
    verify_frames(manifest, directory, media, segment)
    write_new(manifest_path, manifest)
    return manifest
