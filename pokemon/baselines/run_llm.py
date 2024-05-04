from os.path import exists
from pathlib import Path
import uuid
from red_gym_env import RedGymEnv
from pokemon.llmagent import PokeEnv
from colorama import Fore
from camel.utils import print_text_animated
from camel.types import ModelType
from stable_baselines3.common.utils import set_random_seed

import os

# Get the directory path of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory of the current directory
parent_dir = os.path.dirname(current_dir)

def make_env(rank, env_conf, seed=0):
    """
    Utility function for multiprocessed env.
    :param env_id: (str) the environment ID
    :param num_env: (int) the number of environments you wish to have in subprocesses
    :param seed: (int) the initial seed for RNG
    :param rank: (int) index of the subprocess
    """
    def _init():
        env = RedGymEnv(env_conf)
        #env.seed(seed + rank)
        return env
    set_random_seed(seed)
    return _init

if __name__ == '__main__':

    sess_path = Path(f'session_{str(uuid.uuid4())[:8]}')
    ep_length = 2**23

    env_config = {
                'headless': False, 'save_final_state': True, 'early_stop': False,
                'action_freq': 24, 'init_state': parent_dir + '/has_pokedex_nballs.state', 'max_steps': ep_length, 
                'print_rewards': True, 'save_video': False, 'fast_video': True, 'session_path': sess_path,
                'gb_path': parent_dir + '/PokemonRed.gb', 'debug': False, 'sim_frame_dist': 2_000_000.0, 'extra_buttons': True
            }
    
    num_cpu = 1 #64 #46  # Also sets the number of episodes per training iteration
    env = make_env(0, env_config)() #SubprocVecEnv([make_env(i, env_config) for i in range(num_cpu)])

    task_prompt = "You are playing Pokemon Red on GameBoy, and your target is to clear the game. Next, I would give you a sequntial of its game screenshot, and you should return me the next button you should press. Three have six buttons you can press, which are UP, DOWN, LEFT, RIGHT, A and B." + \
    "You will respond with one JSON Key \"UP\", \"DOWN\", \"LEFT\", \"RIGHT\", \"A\", \"B\", with the value as its probability on a scale of 0-1? " + \
    "For example: if you have 0.8 probabiligy of pressing \"LEFT\", you would return {\"LEFT\": 0.8}."
    #"After you press a button, we would return you three reward values respectively indicate pokemons' levels, pokemons' health, and the explore progress of the game. Your actions are supposed to maximize these reward values."

    # input_msg = "Return me one of the six buttons each time."

    print(Fore.YELLOW + f"Original task prompt:\n{task_prompt}\n")
    poke_session = PokeEnv(env, task_prompt, assistant_role_name = 'assistant', user_role_name = 'user')
    print(Fore.CYAN + f"Specified task prompt:\n{poke_session.task_prompt}\n")

    obs, info = poke_session.reset()
    step_n = 0
    while True:
        obs, rewards, terminated, truncated, info = poke_session.step(n = step_n)
        poke_session.render()
        step_n +=1 
        if truncated:
            break
    poke_session.close()
    # res = poke_session.step()
    # print_text_animated(Fore.GREEN + "AI Response:\n\n"f"{res}\n")


        
    # #keyboard.on_press_key("M", toggle_agent)
    # obs, info = env.reset()
    # while True:
    #     action = 7 # pass action
    #     try:
    #         with open("agent_enabled.txt", "r") as f:
    #             agent_enabled = f.readlines()[0].startswith("yes")
    #     except:
    #         agent_enabled = False
    #     if agent_enabled:
    #         action, _states = model.predict(obs, deterministic=False)
    #     obs, rewards, terminated, truncated, info = env.step(action)
    #     env.render()
    #     if truncated:
    #         break
