from .base_player import BasePlayer
import sys
sys.path.append("..")
from actions import Speak, Impersonate

class Werewolf(BasePlayer):
    def __init__(
        self,
        name: str = "",
        profile: str = "Werewolf",
        special_action_names: list[str] = ["Hunt"],
        **kwargs,
    ):
        super().__init__(name, profile, special_action_names, **kwargs)

    async def _think(self):
        await super()._think()
        if isinstance(self.rc.todo, Speak):
            self.rc.todo = Impersonate()
