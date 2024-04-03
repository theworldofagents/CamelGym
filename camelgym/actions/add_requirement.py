
from camelgym.actions import Action


class UserRequirement(Action):
    async def run(self, *args, **kwargs):
        raise NotImplementedError
