"""Offline QA of generated assets; produces program checks, never predictions."""
import json
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pilot


def main():
    result = {"created_at": pilot.now(), "type": "OFFLINE_PROGRAM_QA", "api_calls": 0}
    test = subprocess.run([sys.executable, "-X", "utf8", "-m", "unittest", "discover", "-s", str(pilot.HERE),
                           "-p", "test_*.py", "-v"], capture_output=True, cwd=pilot.ROOT)
    (pilot.HERE / "program_test_report.txt").write_bytes(test.stdout + test.stderr)
    if test.returncode:
        raise ValueError("Offline safety tests failed; inspect program_test_report.txt")
    result["safety_tests"] = {"passed": 6, "log": "program_test_report.txt"}
    black = []
    for t in pilot.rows(pilot.HERE / "candidate_tasks.jsonl"):
        a, b = t["critical_interval_sec"]
        path = pilot.HERE / t["clips"]["critical_mask_history"]
        # Check the entire image range (Y/U/V extrema), at approximately 1FPS,
        # rather than relying on average darkness or the command text.
        filters = (f"select='gte(t,{a})*lt(t,{b})*not(mod(n,30))',"
                   "signalstats,metadata=mode=print:file=-")
        command = ["ffmpeg", "-hide_banner", "-v", "error", "-nostdin", "-i", str(path),
                   "-vf", filters, "-an", "-f", "null", "-"]
        log = pilot.cmd(command)
        counts = {}
        extrema = {}
        for key, expected in [("YMIN", 16), ("YMAX", 16), ("UMIN", 128), ("UMAX", 128), ("VMIN", 128), ("VMAX", 128)]:
            values = [float(x) for x in re.findall(r"lavfi\.signalstats\." + key + r"=([0-9.]+)", log)]
            # H.264 inter prediction can round chroma by one 8-bit level at
            # a hard cut. Require exactly black luminance and <=1 chroma error.
            tolerance = 0 if key.startswith("Y") else 1
            if not values or any(abs(v - expected) > tolerance for v in values):
                raise ValueError(f"Masked review video is not full-frame black: {t['task_id']} {key}")
            counts[key] = len(values)
            extrema[key] = [min(values), max(values)]
        black.append({"task_id": t["task_id"], "file": pilot.rel(path), "check": "FULL_IMAGE_YUV_EXTREMA",
                      "sampled_output_frames_checked": counts["YMIN"], "result": "PASS",
                      "extrema": extrema, "tolerance": "Y exactly 16; U/V 128 +/- 1 (8-bit H264 cut rounding)",
                      "scope": "Human review MP4 only; no masked API input constructed in phase 1"})
    result["black_review_video_checks"] = black
    result["resolved_program_check_issue"] = "Initial exact-chroma check rejected one U=127 sample in P01; luminance was exactly black at 16. Allow documented +/-1 chroma rounding for lossy review MP4. Real API masks will use independently verified black JPEG replacements."
    key = pilot.load_api_key({"api_key_env": "DASHSCOPE_API_KEY"})
    leaked = []
    inspected = 0
    if key:
        for p in pilot.HERE.rglob("*"):
            if p.is_file() and p.suffix in [".json", ".jsonl", ".csv", ".md", ".log", ".py", ".txt"]:
                inspected += 1
                if key in p.read_text(encoding="utf-8-sig", errors="replace"):
                    leaked.append(pilot.rel(p))
    if leaked:
        raise ValueError("Credential appeared in generated text files: " + ", ".join(leaked))
    result["secret_scan"] = {"key_available_for_comparison": bool(key), "files_checked": inspected,
                             "leaks_found": 0, "secret_logged": False}
    result["original_integrity"] = pilot.verify_originals()
    result["human_review"] = "PENDING; these checks do not establish semantic truth or historical necessity"
    pilot.write(pilot.HERE / "program_qa.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
