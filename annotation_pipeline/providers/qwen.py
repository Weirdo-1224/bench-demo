import base64
import json

import requests

from .base import ProviderResponse, VideoModelProvider


class QwenProvider(VideoModelProvider):
    def build_request(self, frame_directory, manifest, prompt):
        frames = manifest["frames"]
        if not 4 <= len(frames) <= min(2000, self.config["max_frames_per_segment"]):
            raise ValueError("Qwen video input requires 4+ frames and must fit configured limit")
        video = ["data:image/jpeg;base64," + base64.b64encode(
            (frame_directory / f["path"]).read_bytes()).decode("ascii") for f in frames]
        return {"model": self.config["model"], "stream": False, "enable_thinking": False,
                "temperature": self.config["temperature"], "max_tokens": self.config["max_output_tokens"],
                "response_format": {"type": "json_object"},
                "messages": [{"role": "user", "content": [
                    {"type": "video", "video": video, "fps": manifest["segment"]["sample_fps"]},
                    {"type": "text", "text": prompt}]}]}

    def invoke(self, request, api_key):
        # No SDK retries and no redirects that could forward credentials.
        response = requests.post(self.config["endpoint"], json=request,
                                 headers={"Authorization": f"Bearer {api_key}"},
                                 timeout=self.config["timeout_sec"], allow_redirects=False)
        return ProviderResponse(response.status_code, response.text)

    def extract_content(self, response_body):
        body = json.loads(response_body)
        choice = body["choices"][0]
        return choice["message"]["content"], {"returned_model": body.get("model"),
                 "usage": body.get("usage"), "finish_reason": choice.get("finish_reason"),
                 "request_id": body.get("id")}
