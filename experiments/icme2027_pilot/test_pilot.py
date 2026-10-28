"""Offline safety tests. No simulated predictions and no network calls."""
import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("pilot", Path(__file__).with_name("pilot.py"))
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


class SafetyTests(unittest.TestCase):
    def test_fractional_query_never_includes_future_window(self):
        windows = pilot.plan_segments(300.123, 60, 0, 1)
        self.assertEqual(windows[-1]["end_sec"], 300.123)
        self.assertEqual(windows[-1]["start_sec"], 300)
        self.assertTrue(all(w["end_sec"] <= 300.123 for w in windows))

    def test_current_window_and_history_masks_are_separate(self):
        for t in pilot.definitions():
            a, b = t["critical_interval_sec"], t["control_interval_sec"]
            self.assertEqual(a[1]-a[0], b[1]-b[0])
            self.assertLessEqual(a[1], t["recent_interval_sec"][0])
            self.assertLessEqual(b[1], t["recent_interval_sec"][0])
            self.assertEqual(t["status"], "PENDING")
            self.assertIsNone(t["gold_answers"])

    def test_tampered_definition_rejected_before_promotion(self):
        original = pilot.rows
        def edited(path):
            rs = original(path)
            if Path(path).name == "candidate_tasks.jsonl":
                rs[0]["query_time_sec"] += 1
            return rs
        with patch.object(pilot, "rows", side_effect=edited), patch.object(pilot, "write"):
            with self.assertRaisesRegex(ValueError, "Definition/source hash mismatch"):
                pilot.validate(promote=True)

    def test_approved_without_all_checks_cannot_promote(self):
        original = pilot.rows
        def edited(path):
            rs = original(path)
            if Path(path).name == "review_decisions.jsonl":
                rs[0]["status"] = "APPROVED"
                rs[0]["checks"]["sampled_1fps_sufficient"] = "PENDING"
            return rs
        with patch.object(pilot, "rows", side_effect=edited), patch.object(pilot, "write"), patch.object(pilot, "write_rows") as output:
            with self.assertRaisesRegex(ValueError, "APPROVED requires"):
                pilot.validate(promote=True)
            output.assert_not_called()

    def test_pending_does_not_create_gold(self):
        original = pilot.rows
        def pending(path):
            rs = original(path)
            if Path(path).name == "review_decisions.jsonl":
                for r in rs: r["status"] = "PENDING"
            if Path(path).name == "tasks_gold.jsonl": return []
            return rs
        with patch.object(pilot, "rows", side_effect=pending), patch.object(pilot, "write"), patch.object(pilot, "write_rows") as output:
            result = pilot.validate(promote=True)
            self.assertEqual(result["approved"], 0)
            output.assert_not_called()

    def test_mask_membership_matches_critical_and_control(self):
        records = pilot.mask_records(pilot.definitions())
        for tid in ["P01", "P02"]:
            rs = {r["condition"]: r for r in records if r["task_id"] == tid}
            self.assertEqual(rs["FULL"]["masked_frame_count"], 0)
            self.assertEqual(rs["CRITICAL_MASK"]["masked_frame_count"], rs["CONTROL_MASK"]["masked_frame_count"])
            self.assertFalse(any(r["applied_to_model"] for r in rs.values()))


if __name__ == "__main__":
    unittest.main()
