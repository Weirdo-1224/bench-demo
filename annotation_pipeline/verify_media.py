"""Offline QA: independently match sampled frame PTS against ffprobe's decode."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import subprocess
from uuid import uuid4

from .common import read_json, write_new
from .media import verify_frames


def verify_run(run_dir: Path):
    run = read_json(run_dir / "run_manifest.json")
    media, config = run["media"], run["config"]
    end = max(s["end_sec"] for s in run["segments"])
    command = [config["ffprobe"], "-v", "error", "-select_streams", "v:0",
               "-read_intervals", f"%+{end + 1}", "-show_frames",
               "-show_entries", "frame=best_effort_timestamp,best_effort_timestamp_time", "-of", "json", media["path"]]
    result = subprocess.run(command, capture_output=True, check=True, timeout=config["media_timeout_sec"])
    decoded = json.loads(result.stdout)["frames"]
    actual_pts = {int(f["best_effort_timestamp"]) for f in decoded}
    segments = []
    for segment in run["segments"]:
        directory = run_dir / segment["segment_id"] / "input"
        manifest = read_json(directory / "input_manifest.json")
        frames = verify_frames(manifest, directory, media, segment)
        base = Fraction(manifest["pts_time_base"])
        original_base = Fraction(media["time_base"])
        for frame in frames:
            original_pts = frame["source_pts"] * base / original_base
            if original_pts.denominator != 1 or int(original_pts) not in actual_pts:
                raise ValueError("Sampled PTS absent from independently decoded original video")
        drift = max(f["source_sec"] - (segment["start_sec"] + i / segment["sample_fps"]) for i, f in enumerate(frames))
        segments.append({"segment_id": segment["segment_id"], "source_range": [segment["start_sec"], segment["end_sec"]],
                         "frame_count": len(frames), "first_frame": frames[0], "last_frame": frames[-1],
                         "max_grid_drift_sec": drift, "pts_match": "PASS"})
    report = {"status": "PASS", "run_id": run["run_id"], "source_sha256": media["sha256"],
              "independent_decoded_frames": len(decoded), "segments": segments,
              "limitation": "PTS/frame lineage verified; model event semantics and temporal boundaries require real response + review"}
    path = run_dir / f"media_qa-{uuid4().hex}.json"
    write_new(path, report)
    return report | {"report_path": path.as_posix()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    print(json.dumps(verify_run(parser.parse_args().run_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
