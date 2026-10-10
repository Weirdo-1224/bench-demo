"""End-to-end SYNTHETIC fixtures, stored only in a TemporaryDirectory."""
from argparse import Namespace
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from annotation_pipeline.annotate_segments import run
from annotation_pipeline.common import PACKAGE, file_hash, load_config, read_json, write_new
from annotation_pipeline.providers.base import ProviderResponse
from annotation_pipeline.providers.qwen import QwenProvider
from annotation_pipeline.validate_output import validate_candidate


class SyntheticProvider(QwenProvider):
    calls = 0

    def invoke(self, request, key):
        self.calls += 1
        value = {"time_basis": "clip_local_seconds", "unknowns": ["SYNTHETIC TEST ONLY"], "events": [{
            "local_event_id": "e1", "start_sec": 0, "end_sec": 2, "actor": "unknown",
            "action": "SYNTHETIC TEST ONLY", "objects": [], "visual_change": None,
            "evidence": {"start_sec": 0, "end_sec": 2, "frame_ids": ["frame-0000", "frame-0001"]},
            "observability": "partial", "uncertainties": ["synthetic"], "annotation_status": "CANDIDATE"}]}
        body = {"model": "SYNTHETIC_TEST_MODEL", "usage": {"prompt_tokens": 10, "completion_tokens": 20},
                "choices": [{"finish_reason": "stop", "message": {"content": json.dumps(value)}}]}
        return ProviderResponse(200, json.dumps(body))


def synthetic_frames(video, media, segment, directory, config):
    cached = directory / "input_manifest.json"
    if cached.exists():
        return read_json(cached)
    directory.mkdir()
    frames = []
    for i in range(segment["planned_frames"]):
        path = directory / f"frame-{i:04d}.jpg"
        path.write_bytes(b"SYNTHETIC_JPEG_TEST_ONLY")
        sec = segment["start_sec"] + i
        frames.append({"frame_id": f"frame-{i:04d}", "path": path.name, "source_pts": sec * 30,
                       "source_sec": sec, "clip_local_sec": i, "sha256": file_hash(path)})
    manifest = {"source_sha256": media["sha256"], "segment": segment, "pts_time_base": "1/30",
                "input_mode": "sampled_video_frames", "frames": frames}
    write_new(cached, manifest)
    return manifest


class IntegrationTests(unittest.TestCase):
    def test_dry_run_smoke_resume_and_trace_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            video = root / "SYNTHETIC.mp4"
            video.write_bytes(b"SYNTHETIC_VIDEO_TEST_ONLY")
            media = {"path": video.as_posix(), "sha256": file_hash(video), "duration_sec": 100,
                     "width": 32, "height": 32, "fps": 30, "time_base": "1/30", "stream_start_sec": 0, "has_audio": False}
            config = load_config(PACKAGE / "config.example.yaml")
            config["window_sec"] = 30
            provider = SyntheticProvider(config)
            args = Namespace(config=PACKAGE / "config.example.yaml", dry_run=True, smoke=True,
                             run_id="SYNTHETIC_TEST_ONLY", reparse_only=False, retry_uncertain=False)
            with patch("annotation_pipeline.annotate_segments.load_config", return_value=config), \
                 patch("annotation_pipeline.annotate_segments.project_path", side_effect=lambda v: video if v == config["video_path"] else root / "runs"), \
                 patch("annotation_pipeline.annotate_segments.inspect_video", return_value=media), \
                 patch("annotation_pipeline.annotate_segments.extract_frames", side_effect=synthetic_frames), \
                 patch("annotation_pipeline.annotate_segments.get_provider", return_value=provider), \
                 patch.dict("os.environ", {config["api_key_env"]: "SYNTHETIC_KEY"}):
                result, code = run(args)
                self.assertEqual((code, result["status"], provider.calls), (0, "DRY_RUN_PASS", 0))
                args.dry_run = False
                result, code = run(args)
                self.assertEqual((code, result["status"], provider.calls), (0, "SMOKE_PASS", 2))
                self.assertEqual(result["segments"][0]["status"], "ANNOTATED")
                self.assertEqual(result["usage"]["input_tokens_reported"], 20)
                first_path = root / "runs" / args.run_id / "seg-0000" / "candidate.json"
                candidate = read_json(first_path)
                digest_before = file_hash(first_path)
                result, code = run(args)
                self.assertEqual(result["network_requests"], 0)
                self.assertEqual(result["segments"][0]["status"], "REUSED_CANDIDATE")
                self.assertEqual(provider.calls, 2)
                self.assertEqual(file_hash(first_path), digest_before)
                # A saved raw response can be re-parsed after local output is removed in TEST ONLY.
                first_path.unlink()
                (first_path.parent / "validation.json").unlink()
                args.reparse_only = True
                result, code = run(args)
                self.assertEqual((code, result["network_requests"], provider.calls), (0, 0, 2))
                self.assertEqual(result["segments"][0]["status"], "REPARSED")
                for mutate in [lambda c: c["events"][0].update(start_sec=99),
                               lambda c: c["events"][0]["evidence"]["frame_refs"][0].update(source_pts=9),
                               lambda c: c["provenance"].update(raw_response_ref="../outside.json"),
                               lambda c: c["events"][0].update(action="ALTERED OBSERVATION")]:
                    bad = deepcopy(candidate)
                    mutate(bad)
                    with self.assertRaises(Exception):
                        validate_candidate(bad, first_path.parent)

    def test_full_video_live_is_refused(self):
        args = Namespace(config=PACKAGE / "config.example.yaml", dry_run=False, smoke=False)
        with self.assertRaises(ValueError):
            run(args)


if __name__ == "__main__":
    unittest.main()
