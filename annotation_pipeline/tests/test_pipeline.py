"""Synthetic unit fixtures are NOT video model observations."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import requests

from annotation_pipeline.calls import Blocked, call_or_reuse, ledger
from annotation_pipeline.common import PACKAGE, digest, load_api_key, load_config, read_json, write_new
from annotation_pipeline.media import plan_segments
from annotation_pipeline.providers.base import ProviderResponse
from annotation_pipeline.providers.qwen import QwenProvider
from annotation_pipeline.validate_output import structure, validate_model


def fixture():
    segment = {"segment_id": "seg-0000", "start_sec": 50, "end_sec": 110,
               "planned_frames": 60, "sample_fps": 1}
    manifest = {"frames": [{"frame_id": "frame-0000", "source_sec": 51.017633333,
                            "clip_local_sec": 1.017633333, "path": "frame-0001.jpg",
                            "source_pts": 1530529, "sha256": "a" * 64}]}
    value = {"time_basis": "clip_local_seconds", "unknowns": ["SYNTHETIC UNIT TEST"], "events": [{
        "local_event_id": "e1", "start_sec": 1, "end_sec": 2, "actor": "unknown",
        "action": "SYNTHETIC_TEST_ACTION", "objects": [{"local_track_id": "o1", "label": "test",
         "role": "object", "identity_uncertainty": ["synthetic"]}], "visual_change": None,
        "evidence": {"start_sec": 1, "end_sec": 2, "frame_ids": ["frame-0000"]},
        "observability": "partial", "uncertainties": ["SYNTHETIC"], "annotation_status": "CANDIDATE"}]}
    return segment, manifest, value


class PlanTests(unittest.TestCase):
    def test_continuity_overlap_tail(self):
        segments = plan_segments(696.929567, 60, 10, 1)
        self.assertEqual(len(segments), 14)
        self.assertEqual(segments[-1]["end_sec"], 696.929567)
        self.assertEqual(segments[1]["start_sec"], 50)
        self.assertTrue(all(a["end_sec"] >= b["start_sec"] for a, b in zip(segments, segments[1:])))

    def test_short_and_exact_tail(self):
        self.assertEqual(len(plan_segments(60, 60, 10, 1)), 1)
        self.assertEqual(plan_segments(3, 60, 10, 1)[0]["planned_frames"], 3)
        self.assertEqual(len(plan_segments(110, 60, 10, 1)), 2)

    def test_reject_bad_plan(self):
        for parameters in [(60, 60, 60, 1), (60, 60, -1, 1), (60, 60, 10, 0), (float("nan"), 60, 10, 1)]:
            with self.subTest(parameters=parameters), self.assertRaises(ValueError):
                plan_segments(*parameters)

    def test_config_safety(self):
        config = load_config(PACKAGE / "config.example.yaml")
        self.assertNotIn("api_key", config)
        with tempfile.TemporaryDirectory() as tmp:
            for field, value in [("output_dir", "golden_episode/GX010021/annotations/v1_candidate"),
                                 ("endpoint", "https://x.test/?api_key=secret"),
                                 ("video_path", "golden_episode/GX010021/source/annotations.json"),
                                 ("max_cost", 0), ("unknown_key", True)]:
                path = Path(tmp) / "config.yaml"
                path.write_text(json.dumps(config | {field: value}), encoding="utf-8")
                with self.subTest(field=field), self.assertRaises(ValueError):
                    load_config(path)

    def test_literal_key_is_rejected_without_exposing_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.yaml"
            path.write_text('api_key_env: sk-SYNTHETIC_SECRET\n', encoding="utf-8")
            with self.assertRaises(ValueError) as raised:
                load_config(path)
            self.assertNotIn("sk-SYNTHETIC_SECRET", str(raised.exception))

    def test_local_credentials_and_environment_precedence(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            config = {"api_key_env": "TEST_ANNOTATION_KEY"}
            with patch("annotation_pipeline.common.PACKAGE", package), patch.dict("os.environ", {}, clear=True):
                self.assertIsNone(load_api_key(config))
                write_new(package / "credentials.local.json", {"TEST_ANNOTATION_KEY": "SYNTHETIC_LOCAL"})
                self.assertEqual(load_api_key(config), "SYNTHETIC_LOCAL")
                with patch.dict("os.environ", {"TEST_ANNOTATION_KEY": "SYNTHETIC_ENV"}):
                    self.assertEqual(load_api_key(config), "SYNTHETIC_ENV")


class ValidationTests(unittest.TestCase):
    def test_mapping_nonzero_window(self):
        segment, manifest, value = fixture()
        validate_model(value, segment, manifest)
        media = {k: None for k in ("path", "sha256", "duration_sec", "width", "height", "fps", "time_base", "stream_start_sec", "has_audio")}
        output = structure(value, media, segment, manifest, {"run_id": "TEST_ONLY"}, "TEST")
        event = output["events"][0]
        self.assertEqual(event["start_sec"], 51)
        self.assertEqual(event["clip_local_start_sec"], 1)
        self.assertEqual(event["evidence"]["frame_refs"][0]["source_pts"], 1530529)
        self.assertEqual(output["deferred_layers"], {"L1": None, "L3": None, "L4": None, "L5": None})

    def test_reject_temporal_and_evidence_corruption(self):
        segment, manifest, original = fixture()
        mutations = [lambda e: e.update(start_sec=-1), lambda e: e.update(end_sec=61),
                     lambda e: e.update(start_sec=3), lambda e: e["evidence"].update(frame_ids=["UNSENT"]),
                     lambda e: e["evidence"].update(start_sec=1.5),
                     lambda e: e.update(start_sec=float("nan")),
                     lambda e: e.update(uncertainties=[]), lambda e: e.update(annotation_status="GOLD"),
                     lambda e: e.update(action="   ")]
        for mutation in mutations:
            value = deepcopy(original)
            mutation(value["events"][0])
            with self.subTest(mutation=mutation), self.assertRaises(Exception):
                validate_model(value, segment, manifest)

    def test_empty_and_duplicate_events(self):
        segment, manifest, value = fixture()
        validate_model(value | {"events": []}, segment, manifest)
        value["events"].append(deepcopy(value["events"][0]))
        with self.assertRaises(ValueError):
            validate_model(value, segment, manifest)


class FakeProvider:
    """Deterministic transport test double, never used by the production CLI."""
    def __init__(self, outcomes):
        self.outcomes = iter(outcomes)
        self.calls = 0

    def invoke(self, request, key):
        self.calls += 1
        result = next(self.outcomes)
        if isinstance(result, Exception):
            raise result
        return ProviderResponse(result, '{"test_fixture": true}')


class CallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run_dir = Path(self.temp.name)
        self.segment_dir = self.run_dir / "seg-0000"
        self.segment_dir.mkdir()
        self.config = load_config(PACKAGE / "config.example.yaml")
        self.config["retry_backoff_sec"] = 0
        self.request = {"unit_test": True}
        write_new(self.segment_dir / "request.json", {"request_sha256": digest(self.request), "frames": [1, 2, 3, 4]})

    def call(self, provider, key="TEST_KEY", **kwargs):
        return call_or_reuse(provider, self.request, self.segment_dir, self.run_dir, self.config, key, **kwargs)

    def test_success_reused_even_without_key(self):
        provider = FakeProvider([200])
        first = self.call(provider)
        second = self.call(provider, key=None)
        self.assertFalse(first[2])
        self.assertTrue(second[2])
        self.assertEqual(provider.calls, 1)

    def test_missing_key_and_reparse_never_call(self):
        provider = FakeProvider([])
        for options in [{"key": None}, {"reparse_only": True}]:
            with self.assertRaises(Blocked):
                self.call(provider, **options)
        self.assertEqual(provider.calls, 0)
        self.assertEqual(len(ledger(self.run_dir)), 0)

    def test_invalid_saved_content_does_not_trigger_paid_repair(self):
        # Success transport with malformed JSON remains reusable for local diagnosis.
        provider = FakeProvider([200])
        path, raw, reused = self.call(provider)
        self.assertFalse(reused)
        for _ in range(2):
            _, raw_again, reused = self.call(provider)
            self.assertTrue(reused)
            with self.assertRaises(KeyError):
                QwenProvider(self.config).extract_content(raw_again["body"])
        self.assertEqual(provider.calls, 1)

    def test_retries_saved_and_counted(self):
        provider = FakeProvider([429, 503, 200])
        self.call(provider)
        self.assertEqual(provider.calls, 3)
        self.assertEqual(len(list(self.segment_dir.glob("*.response.json"))), 3)
        self.assertEqual(sum(r["cost_reserved"] for r in ledger(self.run_dir)), .75)

    def test_unauthorized_does_not_retry(self):
        provider = FakeProvider([401])
        with self.assertRaises(Blocked):
            self.call(provider)
        with self.assertRaises(Blocked):
            self.call(provider)
        self.assertEqual(provider.calls, 1)

    def test_timeout_never_automatically_resubmits(self):
        provider = FakeProvider([requests.Timeout(), 200])
        with self.assertRaises(Blocked):
            self.call(provider)
        with self.assertRaises(Blocked):
            self.call(provider)
        self.assertEqual(provider.calls, 1)
        self.call(provider, retry_uncertain=True)
        self.assertEqual(provider.calls, 2)

    def test_interrupted_pending_call_reserved(self):
        write_new(self.segment_dir / "attempt-000.start.json", {"cost_reserved": .25, "frame_count": 4})
        provider = FakeProvider([])
        with self.assertRaises(Blocked):
            self.call(provider)
        self.assertEqual(provider.calls, 0)

    def test_persistent_call_and_cost_caps(self):
        provider = FakeProvider([503, 200])
        self.config["max_api_calls"] = 1
        with self.assertRaises(Blocked):
            self.call(provider)
        self.assertEqual(provider.calls, 1)
        with self.assertRaises(Blocked):
            self.call(provider)
        self.assertEqual(provider.calls, 1)
        self.config["max_api_calls"] = 4
        self.config["max_cost"] = .25
        with self.assertRaises(Blocked):
            self.call(provider)
        self.assertEqual(provider.calls, 1)

    def test_raw_records_cannot_be_overwritten(self):
        self.call(FakeProvider([200]))
        path = next(self.segment_dir.glob("*.response.json"))
        with self.assertRaises(FileExistsError):
            write_new(path, {"changed": True})


class ProviderTests(unittest.TestCase):
    def test_qwen_http_contract(self):
        config = load_config(PACKAGE / "config.example.yaml")
        provider = QwenProvider(config)
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "frame.jpg").write_bytes(b"SYNTHETIC_JPEG_FIXTURE")
            request = provider.build_request(directory, {"frames": [{"path": "frame.jpg"}] * 4,
                                                        "segment": {"sample_fps": 1}}, "TEST_PROMPT")
            part = request["messages"][0]["content"][0]
            self.assertEqual(part["type"], "video")
            self.assertEqual(part["fps"], 1)
            self.assertEqual(len(part["video"]), 4)
            self.assertNotIn("TEST_KEY", json.dumps(request))
            with patch("annotation_pipeline.providers.qwen.requests.post") as post:
                post.return_value.status_code = 200
                post.return_value.text = "RAW"
                self.assertEqual(provider.invoke(request, "TEST_KEY").body, "RAW")
                self.assertFalse(post.call_args.kwargs["allow_redirects"])
                self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer TEST_KEY")


if __name__ == "__main__":
    unittest.main()
