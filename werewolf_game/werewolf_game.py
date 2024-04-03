from camelgym.gym import Gym
from camelgym.environment import Environment
from camelgym.actions import UserRequirement
from camelgym.schema import Message

class WerewolfEnvironment(Environment):

    timestamp: int = 0

    def publish_message(self, message: Message, add_timestamp: bool = True):
        """
          Post information to the current environment
        """
        # self.message_queue.put(message)
        if add_timestamp:
            message.content = f"{self.timestamp} | " + message.content
        self.memory.add(message)
        self.history += f"\n{message}"

    async def run(self, k=1):
        """
        Process all Role runs at once
        """
        for _ in range(k):
            for role in self.roles.values():
                await role.run()
            self.timestamp += 1

class WerewolfGame(Gym):

    environment = WerewolfEnvironment()

    def start_project(self, idea):
        """Start a project from user instruction."""
        self.idea = idea
        self.environment.publish_message(
            Message(role="User", content=idea, cause_by=UserRequirement, restricted_to="Moderator")
        )
