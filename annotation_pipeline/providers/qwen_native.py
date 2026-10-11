"""Native whole-file video input via DashScope's controlled temporary upload.
No public hosting, SDK retries, redirects, or persisted upload credentials.
"""
import copy
import json
from pathlib import Path
from urllib.parse import urlsplit

import requests

from .base import ProviderResponse, VideoModelProvider


class QwenNativeProvider(VideoModelProvider):
    def build_request(self, video, manifest, prompt):
        return {"model": self.config["model"],
                "input": {"messages": [{"role": "user", "content": [
                    {"video": "file://" + Path(video).resolve().as_posix(),
                     "fps": self.config["sample_fps"],
                     "max_pixels": self.config["video_max_pixels"]}, {"text": prompt}]}]},
                "parameters": {"enable_thinking": False, "temperature": 0,
                               "max_tokens": self.config["max_output_tokens"],
                               "response_format": {"type": "json_object"}}}

    def invoke(self, request, api_key):
        self.network_log = []
        endpoint = self.config["endpoint"].rstrip("/")
        auth = {"Authorization": "Bearer " + api_key}
        policy = requests.get(endpoint + "/uploads", params={"action": "getPolicy", "model": request["model"]},
                              headers=auth, timeout=self.config["timeout_sec"], allow_redirects=False)
        self.network_log.append({"operation": "temporary_upload_policy", "http_status": policy.status_code})
        if policy.status_code != 200:
            # Return only safe status/code: certificates must never be logged.
            return ProviderResponse(policy.status_code, json.dumps({"stage": "upload_policy_failed"}))
        cert = policy.json()["data"]
        host = urlsplit(cert["upload_host"])
        if host.scheme != "https" or not host.hostname.endswith(".aliyuncs.com") or host.username or host.password:
            raise ValueError("Unsafe temporary upload host")
        if cert["x_oss_object_acl"] != "private":
            raise ValueError("Provider upload must use private ACL")
        video = Path(request["input"]["messages"][0]["content"][0]["video"][7:])
        fields = {"OSSAccessKeyId": cert["oss_access_key_id"], "Signature": cert["signature"],
                  "policy": cert["policy"], "key": cert["upload_dir"] + "/" + video.name,
                  "x-oss-object-acl": "private", "x-oss-forbid-overwrite": cert["x_oss_forbid_overwrite"],
                  "success_action_status": "200", "x-oss-content-type": "video/mp4"}
        with video.open("rb") as stream:
            upload = requests.post(cert["upload_host"], data=fields, files={"file": stream},
                                   timeout=self.config["timeout_sec"], allow_redirects=False)
        self.network_log.append({"operation": "private_video_upload", "http_status": upload.status_code,
                                 "bytes": video.stat().st_size, "acl": "private"})
        if upload.status_code != 200:
            return ProviderResponse(upload.status_code, json.dumps({"stage": "private_upload_failed"}))
        wire = copy.deepcopy(request)
        wire["input"]["messages"][0]["content"][0]["video"] = "oss://" + fields["key"]
        response = requests.post(endpoint + "/services/aigc/multimodal-generation/generation", json=wire,
                                 headers=auth | {"X-DashScope-OssResourceResolve": "enable"},
                                 timeout=self.config["timeout_sec"], allow_redirects=False)
        self.network_log.append({"operation": "model_inference", "http_status": response.status_code})
        return ProviderResponse(response.status_code, response.text)

    def extract_content(self, response_body):
        body = json.loads(response_body)
        choice = body["output"]["choices"][0]
        content = choice["message"]["content"]
        text = content if isinstance(content, str) else "".join(p.get("text", "") for p in content)
        return text, {"returned_model": body.get("model"), "usage": body.get("usage"),
                      "finish_reason": choice.get("finish_reason"), "request_id": body.get("request_id")}
