from camel.societies import RolePlaying 
from camel.messages import BaseMessage
from camel.responses import ChatAgentResponse
import base64
import requests
from openai import OpenAI
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
import json
from camelgym.utils.common import FixedFIFO
from .utils import encode_img, content_wrap, handle_input, json_parser

def reward_complete_compare(model, state, goal, input, history = []):
        '''
        state: string, init or resume
        goal: the goal agent is supposed to achieve
        input: image with type np.array, the game screenshot
        '''
        rate_to_index = {
            "much worse": -2,
            "worse": -1,
            "nearly the same": 0,
            "better": 1,
            "much better": 2,
            "completed": 10,
        }

        if "gpt" in model:
             client = OpenAI()
        else:
             client = OpenAI()

        img = encode_img(input)

        if state == 'init':
             prompt = f"I am using reinforcement learning to play Pokemon red, the task is to {goal}. Then I will give you the initial state of the game, in the form of a game screenshot. You should remember it and then I will give you the following states for you to compare it is better or worse in term of the completeness of the task."
        else:
             prompt = """Compare this frame to the last one, tell me it is better or worse in term of the completeness of the task “get out of the room”. You should return me one of the 5 options: much worse, worse, nearly the same, better, much better, completed. Here is the rules for you to return the specific rates:
             
                        much worse: Comparing to the last frame, the player turned into a state harder or impossible or irrelated to complete the task. For example, in the last frame, there has clear relations between the task and the current state. The players could achieve the task by doing a sequential of actions. But in this frame, there is no clear clue indicating the current state of the player is related to the task, or the player has no clear actions to complete the task.

                        worse: Comparing to the last frame, the player turned into a state which needs more actions to complete the task.

                        nearly the same: Comparing to the last frame, the player needs the same complexity of the actions to complete the task, or in both frames, it is unknown how to complete the task.

                        better: Comparing to the last frame, the player turned into a state which needs fewer actions to complete the task.

                        much better: Comparing to the last frame, the player turned into a state much more favorable to complete the task. For example, in the last frame, there has no clear relations between the task and the current state, and it is unknown what actions to take for completing the task. But in this frame, there has strong relations between the task and the current state. The players could achieve the task through some feasible actions. Or in the last frame, the player needs very complex actions to complete the task, but in this frame, the player only needs very clear and specific actions to complete the task. 

                        completed: Considering the current state, there may no relations between the task and the current state. The player has completed the task. The current state is likely what happened after completing this task. Never return this if the player has not completely done the task, even it is very very close to achieve the task.
                        
                        Return a JSON array as the result. One of the five options should be the key, and the value should be the probability (0-1) of this result. For example: \{ "nearly the same": 0.8 \}
                        """

        img = {
                    "url": f"data:image/jpeg;base64,{img}"
        }

        # Get the user's input
        user_input = content_wrap(prompt) + content_wrap(img, type = "image_url")
        
        # Handle the input
        res_msg = handle_input(user_input, client, model, history, "user", "assistant")
        print('DEBUG in reward_complete_compare: LLM return response:', res_msg)

        if state == 'init':
              return 0

        res_json = json_parser(res_msg)
        print('DEBUG in reward_complete_compare: json parser:', res_json)

        rate = next((button for button in ["much worse", "worse", "nearly the same", "better", "much better", "completed"] if button in res_json), None)
        print('DEBUG in reward_complete_compare: LLM return rate', rate)

        value = rate_to_index[rate]
        
        return value