"""Deterministic structural repair only; never imports historical annotations.
Raw model facts are unchanged and remain CANDIDATE.
"""
from copy import deepcopy


def normalize(value):
    result = deepcopy(value)
    repairs = []
    evidence = {r["evidence_id"]: r for r in result["evidence"]}
    for event in result["events"]:
        refs = event["evidence_refs"]
        t = event["evidence_sufficient_time"]
        if t is not None and all(r in evidence for r in refs) and t < max(evidence[r]["end_time"] for r in refs):
            repairs.append({"entity_id": event["event_id"], "field": "evidence_sufficient_time",
                            "before": t, "after": None, "reason": "Referenced evidence includes future media; earliest sufficiency is unknown"})
            event["evidence_sufficient_time"] = None
    for stage in result["stages"]:
        old = stage["event_ids"]
        new = [e["event_id"] for e in sorted(result["events"], key=lambda x: (x["start_time"] is None, x["start_time"] or 0))
               if e["start_time"] is not None and stage["start_time"] <= e["start_time"] < stage["end_time"]]
        if old != new:
            repairs.append({"entity_id": stage["stage_id"], "field": "event_ids", "before": old, "after": new,
                            "reason": "Reindexed existing events by their claimed original-media start times; no new observation"})
            stage["event_ids"] = new
    return result, repairs
