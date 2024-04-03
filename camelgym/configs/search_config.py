#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Callable, Optional

from camelgym.tools import SearchEngineType
from camelgym.utils.yaml_model import YamlModel


class SearchConfig(YamlModel):
    """Config for Search"""

    api_type: SearchEngineType = SearchEngineType.DUCK_DUCK_GO
    api_key: str = ""
    cse_id: str = ""  # for google
    search_func: Optional[Callable] = None
