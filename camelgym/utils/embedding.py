#!/usr/bin/env python
# -*- coding: utf-8 -*-
from langchain_community.embeddings import OpenAIEmbeddings

from camelgym.call_config import config


def get_embedding():
    llm = config.get_openai_llm()
    embedding = OpenAIEmbeddings(openai_api_key=llm.api_key, openai_api_base=llm.base_url)
    return embedding
