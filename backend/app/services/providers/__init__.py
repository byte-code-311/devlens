from ...config import get_settings
from .baseline import BaselineProvider
from .base import TriageProvider
from .openai_provider import OpenAIProvider


def get_provider() -> TriageProvider:
    settings = get_settings()
    if settings.openai_api_key:
        return OpenAIProvider(settings.openai_api_key, settings.openai_model)
    return BaselineProvider()
