import asyncio
from typing import Iterable

from pydantic import BaseModel, Field

from camelgym.memory import Memory
from camelgym.roles import Role
from camelgym.schema import Message


class Environment(BaseModel):
    """
       Environment, hosting a batch of roles, roles can publish messages to the environment, and can be observed by other roles
    
    """

    roles: dict[str, Role] = Field(default_factory=dict)
    memory: Memory = Field(default_factory=Memory)
    history: str = Field(default='')

    class Config:
        arbitrary_types_allowed = True

    def add_role(self, role: Role):
        """
           Add a role in the current environment
        """
        role.set_env(self)
        self.roles[str(role._setting)] = role

    def add_roles(self, roles: Iterable[Role]):
        """
            Add a batch of characters in the current environment
        """
        for role in roles:
            self.add_role(role)

    def publish_message(self, message: Message):
        """
          Post information to the current environment
        """
        # self.message_queue.put(message)
        self.memory.add(message)
        self.history += f"\n{message}"

    async def run(self, k=1):
        """
        Process all Role runs at once
        """
        # while not self.message_queue.empty():
        # message = self.message_queue.get()
        # rsp = await self.manager.handle(message, self)
        # self.message_queue.put(rsp)
        for _ in range(k):
            futures = []
            for role in self.roles.values():
                future = role.run()
                futures.append(future)

            await asyncio.gather(*futures)

    def get_roles(self) -> dict[str, Role]:
        """
           Process all Role runs at once
        """
        return self.roles

    def get_role(self, role_setting: str) -> Role:
        """
           get all the environment roles
        """
        return self.roles.get(role_setting, None)
