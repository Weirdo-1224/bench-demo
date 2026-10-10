from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = Path(__file__).resolve().parent


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False).encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_new(path: Path, value):
    """Exclusive creation: never replace raw responses or candidate records."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def project_path(value: str) -> Path:
    path = Path(value)
    return (path if path.is_absolute() else ROOT / path).resolve()


def load_api_key(config: dict) -> str | None:
    """Read credentials separately from the configuration saved in run records."""
    name = config["api_key_env"]
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        raise ValueError("api_key_env must contain an environment variable NAME, never a literal API key")
    key = os.environ.get(name)
    if key and key.strip():
        return key.strip()
    path = PACKAGE / "credentials.local.json"
    if not path.exists():
        return None
    try:
        credentials = read_json(path)
    except (OSError, ValueError):
        raise ValueError("Cannot parse ignored credentials.local.json") from None
    if not isinstance(credentials, dict):
        raise ValueError("credentials.local.json must be an object indexed by environment variable name")
    key = credentials.get(name)
    if key is None:
        return None
    if not isinstance(key, str) or not key.strip():
        raise ValueError("Configured local credential must be a nonempty string")
    return key.strip()


def load_config(path: Path) -> dict:
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    defaults = yaml.safe_load((PACKAGE / "config.example.yaml").read_text(encoding="utf-8"))
    if not isinstance(config, dict) or set(config) - set(defaults):
        raise ValueError("Config must be a mapping with only documented keys")
    config = defaults | config
    # Optional environment overrides; the key VALUE is never part of config/logs.
    for env, field in (("ANNOTATION_MODEL", "model"), ("ANNOTATION_ENDPOINT", "endpoint"),
                       ("ANNOTATION_API_KEY_ENV", "api_key_env")):
        if os.environ.get(env):
            config[field] = os.environ[env]
    if not isinstance(config["api_key_env"], str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", config["api_key_env"]):
        raise ValueError("api_key_env must contain an environment variable NAME, never a literal API key")
    for field in ("window_sec", "sample_fps", "timeout_sec", "media_timeout_sec",
                  "max_cost", "cost_reserve_per_call"):
        value = config[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"{field} must be finite and positive")
    if not 0 <= config["overlap_sec"] < config["window_sec"]:
        raise ValueError("Require 0 <= overlap_sec < window_sec")
    if not 0.1 <= config["sample_fps"] <= 10:
        raise ValueError("sample_fps must be in [0.1, 10]")
    if not isinstance(config["smoke_start_sec"], (int, float)) or not math.isfinite(config["smoke_start_sec"]) or config["smoke_start_sec"] < 0:
        raise ValueError("smoke_start_sec must be finite and nonnegative")
    for field in ("smoke_segments", "max_api_calls", "max_output_tokens", "max_frames_per_segment", "max_request_bytes"):
        if type(config[field]) is not int or config[field] <= 0:
            raise ValueError(f"{field} must be a positive integer")
    if type(config["max_retries"]) is not int or not 0 <= config["max_retries"] <= 5:
        raise ValueError("max_retries must be in [0, 5]")
    for field in ("retry_backoff_sec", "temperature"):
        if not isinstance(config[field], (int, float)) or not math.isfinite(config[field]) or config[field] < 0:
            raise ValueError(f"Invalid {field}")
    for field in ("input_cost_per_million", "output_cost_per_million"):
        value = config[field]
        if value is not None and (not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
            raise ValueError(f"Invalid {field}")
    for field in ("episode_id", "model", "model_version", "api_key_env", "currency", "ffmpeg", "ffprobe"):
        if not isinstance(config[field], str) or not config[field].strip():
            raise ValueError(f"Empty {field}")
    endpoint = urlsplit(config["endpoint"])
    if endpoint.scheme != "https" or not endpoint.netloc or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment:
        raise ValueError("endpoint must be an HTTPS URL without credentials/query/fragment")
    if not all(c.isalnum() or c in "_-" for c in config["episode_id"]):
        raise ValueError("episode_id must be a safe path component")
    expected_video = ROOT / "golden_episode" / config["episode_id"] / "source" / f'{config["episode_id"]}.MP4'
    expected_output = ROOT / "golden_episode" / config["episode_id"] / "annotations" / "v2_video_model" / "runs"
    if project_path(config["video_path"]) != expected_video.resolve():
        raise ValueError("Session 1 reads only the original episode MP4")
    if project_path(config["output_dir"]) != expected_output.resolve():
        raise ValueError("Outputs must stay in this episode's v2_video_model/runs")
    return config
