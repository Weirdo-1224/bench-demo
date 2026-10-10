from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ProviderResponse:
    status_code: int
    body: str


class VideoModelProvider(ABC):
    """One call per invoke. The caller owns retries, budgets, and persistence."""

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def build_request(self, frame_directory, manifest, prompt) -> dict:
        pass

    @abstractmethod
    def invoke(self, request, api_key) -> ProviderResponse:
        pass

    @abstractmethod
    def extract_content(self, response_body: str) -> tuple[str, dict]:
        """Return content and metadata (usage, returned_model, finish_reason)."""
        pass
