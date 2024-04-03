#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Literal

from camelgym.utils.yaml_model import YamlModel


class MermaidConfig(YamlModel):
    """Config for Mermaid"""

    engine: Literal["nodejs", "ink", "playwright", "pyppeteer"] = "nodejs"
    path: str = "mmdc"  # mmdc
    puppeteer_config: str = ""
    pyppeteer_path: str = "/usr/bin/google-chrome-stable"
