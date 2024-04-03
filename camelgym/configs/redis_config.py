#!/usr/bin/env python
# -*- coding: utf-8 -*-
from camelgym.utils.yaml_model import YamlModelWithoutDefault


class RedisConfig(YamlModelWithoutDefault):
    host: str
    port: int
    username: str = ""
    password: str
    db: str

    def to_url(self):
        return f"redis://{self.host}:{self.port}"

    def to_kwargs(self):
        return {
            "username": self.username,
            "password": self.password,
            "db": self.db,
        }
