import asyncio
import platform
import fire
import random
# import sys
# sys.path.append("..")
# sys.path.insert(1, os.path.join(sys.path[0], '..'))

from camelgym.logs import logger
from camelgym.team import Team
from camelgym.environment.werewolf_env.werewolf_env import WerewolfEnv
# from werewolf_game.werewolf_game import WerewolfGame
from roles import Moderator, Villager, Werewolf, Guard, Seer, Witch
from roles.human_player import prepare_human_player
from camelgym.actions import UserRequirement
from camelgym.schema import Message

def init_game_setup(
        shuffle=True, add_human=False,
        use_reflection=True, use_experience=False, use_memory_selection=False,
        new_experience_version="",
    ):
    roles = [
        Villager,
        Villager,
        Werewolf,
        Werewolf,
        Guard,
        Seer,
        Witch
    ]
    if shuffle:
        # random.seed(2023)
        random.shuffle(roles)
    if add_human:
        assigned_role_idx = random.randint(0, len(roles) - 1)
        assigned_role = roles[assigned_role_idx]
        roles[assigned_role_idx] = prepare_human_player(assigned_role)

    players = [
        role(
            name=f"Player{i+1}",
            use_reflection=use_reflection, use_experience=use_experience, use_memory_selection=use_memory_selection,
            new_experience_version=new_experience_version
        ) for i, role in enumerate(roles)
    ]

    if add_human:
        logger.info(f"You are assigned {players[assigned_role_idx].name}({players[assigned_role_idx].profile})")

    game_setup = ["Game setup:"] + [f"{player.name}: {player.profile}," for player in players]
    game_setup = "\n".join(game_setup)

    return game_setup, players

async def start_game(
    investment: float = 3.0, n_round: int = 5, shuffle : bool = True, add_human: bool = False,
    use_reflection: bool = True, use_experience: bool = False, use_memory_selection: bool = False,
    new_experience_version: str = "",
):

    env = WerewolfEnv(desc="werewolf game")
    game_setup, players = init_game_setup(
        shuffle=shuffle, add_human=add_human, use_reflection=use_reflection, use_experience=use_experience,
        use_memory_selection=use_memory_selection, new_experience_version=new_experience_version,
    )
    players = [Moderator()] + players
    env.add_roles(players)
    for p in players:
        env.set_addresses(p, p.addresses)
    env.pub_mes(
            Message(role="User", content=game_setup, cause_by=UserRequirement, restricted_to="Moderator")
        )
    game = Team(investment=investment, env=env, roles=players)
    await game.run(n_round=n_round)

def main(investment: float = 20.0, n_round: int = 100, shuffle : bool = True, add_human: bool = False,
         use_reflection: bool = True, use_experience: bool = False, use_memory_selection: bool = False,
         new_experience_version: str = ""):

    asyncio.run(start_game(investment, n_round, shuffle, add_human,
                           use_reflection, use_experience, use_memory_selection, new_experience_version))


if __name__ == '__main__':
    fire.Fire(main)
