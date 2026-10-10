from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import subprocess

from .common import file_hash, project_path


def inspect_video(path: Path, ffprobe="ffprobe", ffmpeg="ffmpeg", timeout=180) -> dict:
    if not path.is_file():
        raise ValueError(f"Missing original MP4: {path}")
    result = subprocess.run([ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                            capture_output=True, check=True, timeout=timeout)
    probe = json.loads(result.stdout)
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    duration = float(video.get("duration", probe["format"]["duration"]))
    if duration <= 0:
        raise ValueError("Video duration must be positive")
    # A short decode is sufficient for inspect; smoke decodes its actual windows.
    subprocess.run([ffmpeg, "-hide_banner", "-v", "error", "-xerror", "-i", str(path),
                    "-map", "0:v:0", "-t", "1", "-f", "null", "-"],
                   capture_output=True, check=True, timeout=timeout)
    return {"path": path.as_posix(), "sha256": file_hash(path), "size_bytes": path.stat().st_size,
            "width": int(video["width"]), "height": int(video["height"]),
            "fps": float(Fraction(video["avg_frame_rate"])), "fps_rational": video["avg_frame_rate"],
            "duration_sec": duration, "time_base": video["time_base"],
            "stream_start_sec": float(video.get("start_time", 0)),
            "has_audio": any(s["codec_type"] == "audio" for s in probe["streams"]),
            "codec": video["codec_name"], "decode_check": "PASS_FIRST_SECOND", "ffprobe": probe}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video", nargs="?", default="golden_episode/GX010021/source/GX010021.MP4")
    args = parser.parse_args()
    print(json.dumps(inspect_video(project_path(args.video)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
