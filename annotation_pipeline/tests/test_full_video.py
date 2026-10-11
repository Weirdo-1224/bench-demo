from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock

from annotation_pipeline.common import PACKAGE, read_json
from annotation_pipeline.full_video import load_full_config, validate_global
from annotation_pipeline.providers.qwen_native import QwenNativeProvider


def fixture():
    return {"schema_version": "full-video-v0.1", "time_basis": "original_mp4_seconds",
            "annotation_status": "CANDIDATE", "summary": "SYNTHETIC",
            "coverage": {"observed_start_time": 0, "observed_end_time": 10, "limitations": []},
            "stages": [], "evidence": [{"evidence_id": "v1", "start_time": 1, "end_time": 2,
                "description": "SYNTHETIC", "observability": "direct_visual"}],
            "objects": [{"object_id": "o1", "label": "TEST", "appearance": "TEST",
                "identity_status": "uncertain", "evidence_refs": ["v1"], "confidence": 0.5, "uncertainties": []}],
            "events": [{"event_id": "e1", "action": "TEST", "actor": "unknown", "objects": ["o1"],
                "start_time": 1, "end_time": 2, "evidence_sufficient_time": 2, "execution_status": "executed",
                "observability": "direct_visual", "evidence_refs": ["v1"], "confidence": 0.5, "uncertainties": []}],
            "states": [], "relations": [], "unknowns": []}


class FullVideoTests(unittest.TestCase):
    def test_ref_time_and_maturity_rejections(self):
        validate_global(fixture(), 10)
        mutations = [lambda d: d["events"][0].update(objects=["missing"]),
                     lambda d: d["events"][0].update(end_time=11),
                     lambda d: d["events"][0].update(evidence_sufficient_time=1),
                     lambda d: d.update(annotation_status="GOLD"),
                     lambda d: d["events"].append(deepcopy(d["events"][0]))]
        for mutate in mutations:
            d = fixture(); mutate(d)
            with self.assertRaises(Exception):
                validate_global(d, 10)

    def test_null_event_boundary_preserved(self):
        d = fixture(); d["events"][0].update(start_time=None, end_time=None, evidence_sufficient_time=None)
        validate_global(d, 10)

    def test_native_upload_is_private_single_inference_no_redirect(self):
        config = load_full_config(PACKAGE / "config.full_video.yaml")
        provider = QwenNativeProvider(config)
        with tempfile.TemporaryDirectory() as tmp:
            video = Path(tmp) / "test.mp4"; video.write_bytes(b"SYNTHETIC")
            request = provider.build_request(video, {}, "NEUTRAL")
            policy = Mock(status_code=200)
            policy.json.return_value = {"data": {"upload_host": "https://test.oss-cn-beijing.aliyuncs.com",
                "x_oss_object_acl": "private", "oss_access_key_id": "TEST", "signature": "TEST",
                "policy": "TEST", "upload_dir": "test", "x_oss_forbid_overwrite": "true"}}
            with (patch("annotation_pipeline.providers.qwen_native.requests.get", return_value=policy) as get,
                 patch("annotation_pipeline.providers.qwen_native.requests.post", side_effect=[Mock(status_code=200), Mock(status_code=200, text="RAW")]) as post):
                self.assertEqual(provider.invoke(request, "TEST_KEY").body, "RAW")
                self.assertEqual(post.call_count, 2)
                self.assertTrue(all(c.kwargs["allow_redirects"] is False for c in post.call_args_list))
                self.assertEqual(post.call_args_list[0].kwargs["data"]["x-oss-object-acl"], "private")
                self.assertTrue(request["input"]["messages"][0]["content"][0]["video"].startswith("file://"))
                self.assertEqual(post.call_args_list[1].kwargs["json"]["input"]["messages"][0]["content"][0]["video"], "oss://test/test.mp4")

    def test_public_acl_rejected_before_upload(self):
        provider = QwenNativeProvider(load_full_config(PACKAGE / "config.full_video.yaml"))
        policy = Mock(status_code=200)
        policy.json.return_value = {"data": {"upload_host": "https://test.aliyuncs.com", "x_oss_object_acl": "public-read"}}
        with (patch("annotation_pipeline.providers.qwen_native.requests.get", return_value=policy),
             patch("annotation_pipeline.providers.qwen_native.requests.post") as post):
            with self.assertRaises(ValueError):
                provider.invoke({"model": "TEST"}, "TEST")
            post.assert_not_called()


class NormalizationTests(unittest.TestCase):
    def test_structural_repair_retains_raw_facts_and_does_not_invent_time(self):
        from annotation_pipeline.normalize_full_video import normalize
        d = fixture()
        d["events"][0]["evidence_sufficient_time"] = 1
        d["stages"] = [{"stage_id": "s1", "label": "TEST", "start_time": 0, "end_time": 10, "event_ids": ["missing"]}]
        original = deepcopy(d)
        value, repairs = normalize(d)
        self.assertEqual(d, original)
        self.assertEqual(value["events"][0]["action"], original["events"][0]["action"])
        self.assertIsNone(value["events"][0]["evidence_sufficient_time"])
        self.assertEqual(value["stages"][0]["event_ids"], ["e1"])
        validate_global(value, 10)
        self.assertEqual(len(repairs), 2)

if __name__ == "__main__":
    unittest.main()
