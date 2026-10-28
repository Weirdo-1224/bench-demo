"""Offline invariants only. Never invokes provider or fabricates experiment responses."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import runtime as r
import pilot as p


class RuntimeSafety(unittest.TestCase):
    def setUp(self):
        self.t=r.gold()

    def test_all_conditions_start_with_empty_memory_and_no_question_in_history(self):
        for c in r.CONDITIONS:
            seg=r.segments(self.t,c)[0]
            directory,m=r.materialize(self.t,c,seg)
            text=r.prompt(self.t,seg,m["frames"],"",False)
            self.assertNotIn(self.t["question"],text)
            self.assertNotIn("P01",text)
            self.assertNotIn(c,text)
            self.assertIn('""',text)
            if c!="recent_only":
                self.assertEqual(seg["start_sec"],0)

    def test_final_question_is_identical_and_current_frames_unchanged(self):
        hashes=[]
        for c in r.CONDITIONS:
            seg=r.segments(self.t,c)[-1]
            directory,m=r.materialize(self.t,c,seg)
            text=r.prompt(self.t,seg,m["frames"],"",True)
            self.assertIn(self.t["question"],text)
            self.assertNotIn("事实Gold",text)
            self.assertTrue(all(not f["masked"] for f in m["frames"]))
            hashes.append([f["sent_sha256"] for f in m["frames"]])
        self.assertTrue(all(h==hashes[0] for h in hashes))

    def test_future_frame_and_wrong_mask_rejected(self):
        seg=r.segments(self.t,"FULL")[0];directory,m=r.materialize(self.t,"FULL",seg)
        fs=copy.deepcopy(m["frames"]);fs[0]["source_sec"]=300
        with self.assertRaisesRegex(ValueError,"Future"):
            r.assert_input(self.t,"FULL",fs,seg)
        fs=copy.deepcopy(m["frames"]);fs[0]["masked"]=True
        with self.assertRaisesRegex(ValueError,"Residual mask"):
            r.assert_input(self.t,"FULL",fs,seg)

    def test_critical_and_control_mask_complete_and_equal(self):
        counts={}
        for c in r.CONDITIONS[:3]:
            fs=[]
            for seg in r.segments(self.t,c):
                directory,m=r.materialize(self.t,c,seg);fs.extend(m["frames"])
            counts[c]=sum(f["masked"] for f in fs)
            if c=="CRITICAL_MASK":
                self.assertTrue(all(f["masked"] for f in fs if 199<=f["source_sec"]<235))
        self.assertEqual(counts,{"FULL":0,"CRITICAL_MASK":66,"CONTROL_MASK":66})

    def test_wire_reconstruction_and_cross_condition_cache_rejection(self):
        seg=r.segments(self.t,"FULL")[0];directory,m=r.materialize(self.t,"FULL",seg)
        text=r.prompt(self.t,seg,m["frames"],"",False)
        wire=r.wire_request(directory,m,text)
        self.assertEqual(r.digest(wire),r.digest(r.wire_request(directory,m,text)))
        with self.assertRaisesRegex(ValueError,"Condition/prefix"):
            r.verify_checkpoint(directory,self.t,"FULL",m,{"condition":"CONTROL_MASK","previous_checkpoint_sha256":None,"memory_before":""},None,"",False)

    def test_request_cap_survives_resumes(self):
        with tempfile.TemporaryDirectory(dir=p.HERE) as tmp:
            base=Path(tmp)
            directory=base/"window";directory.mkdir()
            # Keep path serialization within real ROOT while isolating ledger state.
            with patch.object(p,"HERE",base):
                for i in range(2):r.reserve(directory,"hash",2)
                self.assertEqual(len(r.ledger()),2)
                with self.assertRaisesRegex(ValueError,"HARD_GLOBAL"):
                    r.reserve(directory,"hash",2)
                self.assertEqual(len(r.ledger()),2)

    def test_memory_bound_and_nonfinite_intervals_rejected(self):
        with self.assertRaisesRegex(ValueError,"Memory schema"):
            r.parse_content(p.json.dumps({"memory":"x"*4097}),False,60)
        self.assertFalse(p.valid_interval([1,float('nan')],300))
        self.assertFalse(p.valid_interval([299,301],300))

    def test_gold_is_fact_yes_but_unknown_policy_is_not_model_input(self):
        self.assertEqual(self.t["fact_gold"],"YES")
        self.assertEqual(self.t["gold_answers"]["CRITICAL_MASK"],"UNKNOWN")
        self.assertEqual(len(r.segments(self.t,"recent_only")),1)

    def test_broad_citation_cannot_claim_unseen_early_history(self):
        seen=[{"source_sec":240.006,"masked":False},{"source_sec":299.032,"masked":False}]
        result=r.response_visibility({"evidence_intervals_sec":[[0,299.032]]},seen)
        self.assertFalse(result["temporal_citations_valid"])
        self.assertTrue(result["citations_outside_supplied_range"])

    def test_citation_spanning_mask_not_counted_fully_visible(self):
        seen=[{"source_sec":170.01,"masked":False},{"source_sec":180.01,"masked":True}]
        result=r.response_visibility({"evidence_intervals_sec":[[170,181]]},seen)
        self.assertFalse(result["temporal_citations_valid"])
        self.assertTrue(result["citations_overlap_mask"])


if __name__=="__main__":unittest.main()
