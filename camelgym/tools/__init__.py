

from enum import Enum
from camelgym.tools import libs  # this registers all tools
from camelgym.tools.tool_registry import TOOL_REGISTRY

_ = libs, TOOL_REGISTRY  # Avoid pre-commit error


class SearchEngineType(Enum):
    SERPAPI_GOOGLE = "serpapi"
    SERPER_GOOGLE = "serper"
    DIRECT_GOOGLE = "google"
    DUCK_DUCK_GO = "ddg"
    CUSTOM_ENGINE = "custom"


class WebBrowserEngineType(Enum):
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    CUSTOM = "custom"

    @classmethod
    def __missing__(cls, key):
        """Default type conversion"""
        return cls.CUSTOM
