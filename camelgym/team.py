#!/usr/bin/env python
# -*- coding: utf-8 -*-

import warnings
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from camelgym.actions import UserRequirement
from camelgym.const import MESSAGE_ROUTE_TO_ALL, SERDESER_PATH
from camelgym.context import Context
from camelgym.environment import Environment
from camelgym.logs import logger
from camelgym.roles import Role
from camelgym.schema import Message
from camelgym.utils.common import (
    NoMoneyException,
    read_json_file,
    serialize_decorator,
    write_json_file,
)


class Team(BaseModel):
    """
    Team: Possesses one or more roles (agents), SOP (Standard Operating Procedures), and a env for instant messaging,
    dedicated to env any multi-agent activity, such as collaboratively writing executable code.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    env: Optional[Environment] = None
    investment: float = Field(default=10.0)
    idea: str = Field(default="")

    def __init__(self, context: Context = None, **data: Any):
        super(Team, self).__init__(**data)
        ctx = context or Context()
        if not self.env:
            self.env = Environment(context=ctx)
        else:
            self.env.context = ctx  # The `env` object is allocated by deserialization
        if "roles" in data:
            self.hire(data["roles"])
        if "env_desc" in data:
            self.env.desc = data["env_desc"]

    def serialize(self, stg_path: Path = None):
        stg_path = SERDESER_PATH.joinpath("team") if stg_path is None else stg_path
        team_info_path = stg_path.joinpath("team.json")

        write_json_file(team_info_path, self.model_dump())

    @classmethod
    def deserialize(cls, stg_path: Path, context: Context = None) -> "Team":
        """stg_path = ./storage/team"""
        # recover team_info
        team_info_path = stg_path.joinpath("team.json")
        if not team_info_path.exists():
            raise FileNotFoundError(
                "recover storage meta file `team.json` not exist, " "not to recover and please start a new project."
            )

        team_info: dict = read_json_file(team_info_path)
        ctx = context or Context()
        team = Team(**team_info, context=ctx)
        return team

    def hire(self, roles: list[Role]):
        """Hire roles to cooperate"""
        self.env.add_roles(roles)

    @property
    def cost_manager(self):
        """Get cost manager"""
        return self.env.context.cost_manager

    def invest(self, investment: float):
        """Invest company. raise NoMoneyException when exceed max_budget."""
        self.investment = investment
        self.cost_manager.max_budget = investment
        logger.info(f"Investment: ${investment}.")

    def _check_balance(self):
        if self.cost_manager.total_cost >= self.cost_manager.max_budget:
            raise NoMoneyException(self.cost_manager.total_cost, f"Insufficient funds: {self.cost_manager.max_budget}")

    def run_project(self, idea, send_to: str = ""):
        """Run a project from publishing user requirement."""
        self.idea = idea

        # Human requirement.
        self.env.publish_message(
            Message(role="Human", content=idea, cause_by=UserRequirement, send_to=send_to or MESSAGE_ROUTE_TO_ALL),
            peekable=False,
        )

    def start_project(self, idea, send_to: str = ""):
        """
        Deprecated: This method will be removed in the future.
        Please use the `run_project` method instead.
        """
        warnings.warn(
            "The 'start_project' method is deprecated and will be removed in the future. "
            "Please use the 'run_project' method instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.run_project(idea=idea, send_to=send_to)

    def _save(self):
        logger.info(self.model_dump_json())

    @serialize_decorator
    async def run(self, n_round=3, idea="", send_to="", auto_archive=True):
        """Run company until target round or no money"""
        if idea:
            self.run_project(idea=idea, send_to=send_to)

        while n_round > 0:
            # self._save()
            n_round -= 1
            logger.debug(f"max {n_round=} left.")
            self._check_balance()

            await self.env.run()
        self.env.archive(auto_archive)
        return self.env.history
