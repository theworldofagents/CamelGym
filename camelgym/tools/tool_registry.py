
from __future__ import annotations

import inspect
import os
import re
from collections import defaultdict

import yaml
from pydantic import BaseModel, field_validator

from camelgym.const import TOOL_SCHEMA_PATH
from camelgym.logs import logger
from camelgym.tools.tool_convert import convert_code_to_tool_schema
from camelgym.tools.tool_data_type import Tool, ToolSchema, ToolTypeDef
from camelgym.tools.tool_type import ToolType


class ToolRegistry(BaseModel):
    tools: dict = {}
    tool_types: dict = {}
    tools_by_types: dict = defaultdict(dict)  # two-layer k-v, {tool_type: {tool_name: {...}, ...}, ...}

    @field_validator("tool_types", mode="before")
    @classmethod
    def init_tool_types(cls, tool_types: ToolType):
        return {tool_type.type_name: tool_type.value for tool_type in tool_types}

    def register_tool(
        self,
        tool_name,
        tool_path,
        schema_path="",
        tool_code="",
        tool_type="other",
        tool_source_object=None,
        include_functions=[],
        verbose=False,
    ):
        if self.has_tool(tool_name):
            return

        if tool_type not in self.tool_types:
            # register new tool type on the fly
            logger.warning(
                f"{tool_type} not previously defined, will create a temporary tool type with just a name. This tool type is only effective during this runtime. You may consider add this tool type with more configs permanently at camelgym.tools.tool_type"
            )
            temp_tool_type_obj = ToolTypeDef(name=tool_type)
            self.tool_types[tool_type] = temp_tool_type_obj
            if verbose:
                logger.info(f"tool type {tool_type} registered")

        schema_path = schema_path or TOOL_SCHEMA_PATH / tool_type / f"{tool_name}.yml"

        schemas = make_schema(tool_source_object, include_functions, schema_path)

        if not schemas:
            return

        schemas["tool_path"] = tool_path  # corresponding code file path of the tool
        try:
            ToolSchema(**schemas)  # validation
        except Exception:
            pass
            # logger.warning(
            #     f"{tool_name} schema not conforms to required format, but will be used anyway. Mismatch: {e}"
            # )

        tool = Tool(name=tool_name, path=tool_path, schemas=schemas, code=tool_code)
        self.tools[tool_name] = tool
        self.tools_by_types[tool_type][tool_name] = tool
        if verbose:
            logger.info(f"{tool_name} registered")
            logger.info(f"schema made at {str(schema_path)}, can be used for checking")

    def has_tool(self, key: str) -> Tool:
        return key in self.tools

    def get_tool(self, key) -> Tool:
        return self.tools.get(key)

    def get_tools_by_type(self, key) -> dict[str, Tool]:
        return self.tools_by_types.get(key, {})

    def has_tool_type(self, key) -> bool:
        return key in self.tool_types

    def get_tool_type(self, key) -> ToolType:
        return self.tool_types.get(key)

    def get_tool_types(self) -> dict[str, ToolType]:
        return self.tool_types


# Registry instance
TOOL_REGISTRY = ToolRegistry(tool_types=ToolType)


def register_tool(tool_type: str = "other", schema_path: str = "", **kwargs):
    """register a tool to registry"""

    def decorator(cls):
        # Get the file path where the function / class is defined and the source code
        file_path = inspect.getfile(cls)
        if "camelgym" in file_path:
            file_path = re.search("camelgym.+", file_path).group(0)
        source_code = inspect.getsource(cls)

        TOOL_REGISTRY.register_tool(
            tool_name=cls.__name__,
            tool_path=file_path,
            schema_path=schema_path,
            tool_code=source_code,
            tool_type=tool_type,
            tool_source_object=cls,
            **kwargs,
        )
        return cls

    return decorator


def make_schema(tool_source_object, include, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)  # Create the necessary directories
    try:
        schema = convert_code_to_tool_schema(tool_source_object, include=include)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(schema, f, sort_keys=False)
        # import json
        # with open(str(path).replace("yml", "json"), "w", encoding="utf-8") as f:
        #     json.dump(schema, f, ensure_ascii=False, indent=4)
    except Exception as e:
        schema = {}
        logger.error(f"Fail to make schema: {e}")

    return schema


def validate_tool_names(tools: list[str], return_tool_object=False) -> list[str]:
    valid_tools = []
    for tool_name in tools:
        if not TOOL_REGISTRY.has_tool(tool_name):
            logger.warning(
                f"Specified tool {tool_name} not found and was skipped. Check if you have registered it properly"
            )
        else:
            valid_tool = TOOL_REGISTRY.get_tool(tool_name) if return_tool_object else tool_name
            valid_tools.append(valid_tool)
    return valid_tools
