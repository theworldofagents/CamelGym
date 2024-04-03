import sys
sys.path.append("..")
from actions import InstructSpeak, Speak, Save, Poison
from .base_player import BasePlayer
from camelgym.const import MESSAGE_ROUTE_TO_ALL

class Witch(BasePlayer):
    def __init__(
        self,
        name: str = "",
        profile: str = "Witch",
        special_action_names: list[str] = ["Save", "Poison"],
        **kwargs,
    ):
        super().__init__(name, profile, special_action_names, **kwargs)

    async def _think(self):
        news = self.rc.news[0]
        assert news.cause_by == InstructSpeak or news.cause_by == "actions.moderator_actions.InstructSpeak" # 消息为来自Moderator的指令时，才去做动作
        if MESSAGE_ROUTE_TO_ALL in news.send_to:
            # If the scope of message reception is for all roles, make a public statement (expressing voting views is also counted as speaking)
            self.rc.todo = Speak()
        elif self.profile in news.send_to:
            # FIXME: hard code to split, restricted to "Moderator" or "Moderator, profile"
            # Moderator is encrypted to himself, meaning to perform the role's specific actions
            if "save" in news.content.lower():
                self.rc.todo = Save()
            elif "poison" in news.content.lower():
                self.rc.todo = Poison()
            else:
                raise ValueError("Moderator's instructions must include save or poison keyword")
