from importlib import import_module

from .base import VideoModelProvider
from .qwen import QwenProvider


def get_provider(config) -> VideoModelProvider:
    """Use qwen, or module:Class for an explicitly configured replacement."""
    if config["provider"] == "qwen":
        return QwenProvider(config)
    module, name = config["provider"].split(":", 1)
    provider = getattr(import_module(module), name)(config)
    if not isinstance(provider, VideoModelProvider):
        raise ValueError("Custom provider must implement VideoModelProvider")
    return provider
