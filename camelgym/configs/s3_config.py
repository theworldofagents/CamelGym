#!/usr/bin/env python
# -*- coding: utf-8 -*-
from camelgym.utils.yaml_model import YamlModelWithoutDefault


class S3Config(YamlModelWithoutDefault):
    access_key: str
    secret_key: str
    endpoint: str
    bucket: str
