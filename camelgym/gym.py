
from pydantic import BaseModel, Field

from camelgym.actions import UserRequirement
from camelgym.environment import Environment
from camelgym.logs import logger
from camelgym.schema import Message


class Gym(BaseModel):

    environment: Environment = Field(default_factory=Environment)
    idea: str = Field(default="")

    class Config:
        arbitrary_types_allowed = True

    def start_project(self, idea):
        """Start a project"""
        self.idea = idea
        self.environment.publish_message(Message(role="User", content=idea, cause_by=UserRequirement))

    def _save(self):
        logger.info(self.json())

    async def run(self, n_round=3):
        while n_round > 0:
            # self._save()
            n_round -= 1
            logger.debug(f"{n_round=}")
            self._check_balance()
            await self.environment.run()
        return self.environment.history
    