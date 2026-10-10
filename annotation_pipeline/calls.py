"""Persistent attempt ledger: reserve before sending; reuse saved success."""
from datetime import datetime, timezone
import time

import requests

from .common import read_json, write_new


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class Blocked(RuntimeError):
    pass


def ledger(run_dir):
    return [read_json(p) for p in sorted(run_dir.glob("seg-*/attempt-*.start.json"))]


def call_or_reuse(provider, request, segment_dir, run_dir, config, api_key,
                  reparse_only=False, retry_uncertain=False):
    request_hash = read_json(segment_dir / "request.json")["request_sha256"]
    responses = sorted(segment_dir.glob("attempt-*.response.json"))
    for path in responses:
        raw = read_json(path)
        if raw["request_sha256"] != request_hash:
            raise ValueError("Saved response belongs to a different request")
        if raw["status_code"] is not None and 200 <= raw["status_code"] < 300:
            return path, raw, True
    if reparse_only:
        raise Blocked("REPARSE_ONLY: no saved successful response; no API call allowed")
    if not api_key:
        raise Blocked(f'MISSING_API_KEY: set {config["api_key_env"]} in environment or ignored credentials.local.json; no request sent')
    starts = sorted(segment_dir.glob("attempt-*.start.json"))
    if starts:
        latest = starts[-1]
        response_path = latest.with_name(latest.name.replace(".start.json", ".response.json"))
        previous = read_json(response_path) if response_path.exists() else None
        if (previous is None or previous["status_code"] is None) and not retry_uncertain:
            raise Blocked("UNCERTAIN_PRIOR_CALL: may have been billed; explicit --retry-uncertain required")
        if previous and previous["status_code"] is not None and previous["status_code"] != 429 and previous["status_code"] < 500:
            raise Blocked("PRIOR_NONRETRYABLE_HTTP_ERROR: inspect raw response; corrected config needs a new run")
    while len(starts) < 1 + config["max_retries"]:
        records = ledger(run_dir)
        reserved = sum(r["cost_reserved"] for r in records)
        if len(records) >= config["max_api_calls"]:
            raise Blocked("MAX_API_CALLS reached, including previous attempts")
        if reserved + config["cost_reserve_per_call"] > config["max_cost"] + 1e-9:
            raise Blocked("MAX_COST reservation reached, including previous attempts")
        attempt = len(starts)
        prefix = segment_dir / f"attempt-{attempt:03d}"
        start_path = prefix.with_suffix(".start.json")
        write_new(start_path, {"request_sha256": request_hash, "started_at": utc_now(),
                              "cost_reserved": config["cost_reserve_per_call"], "currency": config["currency"],
                              "frame_count": len(read_json(segment_dir / "request.json")["frames"])})
        starts.append(start_path)
        began = time.monotonic()
        try:
            result = provider.invoke(request, api_key)
            raw = {"status_code": result.status_code, "body": result.body, "transport_error": None}
        except requests.RequestException as error:
            # Exception messages can include payloads/headers; only retain its type.
            raw = {"status_code": None, "body": None, "transport_error": type(error).__name__}
        raw |= {"request_sha256": request_hash, "completed_at": utc_now(), "elapsed_sec": time.monotonic() - began}
        response_path = prefix.with_suffix(".response.json")
        write_new(response_path, raw)
        code = raw["status_code"]
        if code is None:
            raise Blocked("UNCERTAIN_TRANSPORT_FAILURE: response saved, no automatic resubmission")
        if 200 <= code < 300:
            return response_path, raw, False
        if code != 429 and code < 500:
            raise Blocked(f"NONRETRYABLE_HTTP_{code}: raw response saved")
        if len(starts) < 1 + config["max_retries"]:
            time.sleep(min(config["retry_backoff_sec"] * 2 ** attempt, 30))
    raise Blocked("RETRY_LIMIT reached; all raw responses retained")
