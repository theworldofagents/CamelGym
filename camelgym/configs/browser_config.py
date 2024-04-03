#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Literal

from camelgym.tools import WebBrowserEngineType
from camelgym.utils.yaml_model import YamlModel


class BrowserConfig(YamlModel):
    """Config for Browser"""

    engine: WebBrowserEngineType = WebBrowserEngineType.PLAYWRIGHT
    browser_type: Literal["chromium", "firefox", "webkit", "chrome", "firefox", "edge", "ie"] = "chromium"
    """If the engine is Playwright, the value should be one of "chromium", "firefox", or "webkit". If it is Selenium, the value
    should be either "chrome", "firefox", "edge", or "ie"."""
