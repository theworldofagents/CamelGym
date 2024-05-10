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


def encode_img(image):
    img = Image.fromarray(image)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    image_data = buffer.getvalue()
    
    return base64.b64encode(image_data).decode('utf-8')

def reward_complete_compare(state, input):
        img, text = input
        frame_list = []
        self.recent_frames = np.roll(self.recent_frames, 1, axis=0)
        self.recent_frames[0] = self.pokenv.render(reduce_res=False)

        print('saving frames at:', str(self.pokenv.s_path ))
        for i in range(self.pokenv.frame_stacks):
            img = self.recent_frames[i,...]
            img = Image.fromarray(img)
            img.save(self.pokenv.s_path / Path(f'recent_meme_step_{str(n)}_frame_{str(i)}.jpeg'))

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            image_data = buffer.getvalue()
            frame_list.append(self.encode_image(image_data))

        lv_rwd = self.pokenv.recent_memory[0, 0]
        hp_rwd = self.pokenv.recent_memory[0, 1]
        exp_rwd = self.pokenv.recent_memory[0, 2]

        # assistant_msg = BaseMessage.make_assistant_message(
        act = None
        main_prompt =  "Your current goal is to get out of the room. The following is the current frame. Which button should press next? and with how much probability? Return a JSON array as the result."        
           # "text": "In this stage, your level award is: " + str(lv_rwd) + ". Your health reward is: " + str(hp_rwd) + ". Your explore reward is: " + str(exp_rwd) + ". If you find the rewards or game frames not change a lot, you should try pressing different buttons to proceed the progess of the game. 
            # "You are playing Pokemon Red on GameBoy, and your goal is to explore more of the game. Next, I would give you a sequntial of its game screenshot, and you should return me the next button you should press. Three have six buttons you can press, which are UP, DOWN, LEFT, RIGHT, A and B. Consider you would press that button a very shot time, like 0.5 second. " +
            # "After you press a button, we would return you three reward values respectively indicate pokemons' levels, pokemons' health, and the explore progress of the game. Your actions are supposed to maximize these reward values." +
            # "The following are the three sequential frames of the pokemon game. The last one is the current frame, and that is what you should exceptionally focus on. Which button should press next? Return me one of the six buttons. You will respond with JSON keys \"UP\", \"DOWN\", \"LEFT\", \"RIGHT\", and \"A\" and \"B\". " +
            #"The following is the current frame. Which button should press next? and with how much probability? Return a JSON array as the result." 
            # "Your decision should consider your previous game experiences." +
            #"If your actions did not change the game states a lot, you should try different actions from your previous ones." + 
            # "Your previous reflection of the game is: " + str(self.reflection()) 
            # "Your last three actions are: 1." + str(self.last_act.get_item(0)) + "." + "2." + str(self.last_act.get_item(1)) + "." + "3." + str(self.last_act.get_item(2)) + "."

        while act not in ("A", "B", "UP", "DOWN", "LEFT", "RIGHT"):   

          if act is not None:
              print("LLM return unexpected act:", act)
              print("Run another round") 
          # print("DEBUG: the prompt is: Your current state of the game is: " + str(self.memory.get_item(0)) + "." + "Your last action is: " + str(self.last_act.get_item(0)) + '.')
          # print("DEBUG: memory in prompt is: " + str(self.memory.get_all()))
          img = {
                      "url": f"data:image/jpeg;base64,{frame_list[0]}"
            }

          # Get the user's input
          user_input = self.content_wrap(main_prompt) + self.content_wrap(img, type = "image_url")
          
          # {
          #   "type": "image_url",
          #   "image_url":  {
          #             "url": f"data:image/jpeg;base64,{frame_list[2]}"
          #         },
          # },
          # {
          #   "type": "image_url",
          #   "image_url":  {
          #             "url": f"data:image/jpeg;base64,{frame_list[1]}"
          #         },
          # },

          # Handle the input
          res_msg = self.handle_input(user_input, self.history, USERNAME, AI_NAME)
          print('DEBUG: LLM return response:', res_msg)
          # self.reflection(response.choices[0].message.content)
          # self.add_memory(f'On step {str(n)}, you return the reasoning and action as follow: {str(res_msg)}' )
          res = res_msg.split('```json\n')[1].split('\n```')[0]  
          res = json.loads(res)
          act = next((button for button in ["A", "B", "UP", "DOWN", "LEFT", "RIGHT"] if button in res), None)
          print('DEBUG: LLM return action', act)
        self.last_act.push(act)
        act_ind = self.action_to_index[act]

        # for _ in range(self.press_time):
        #     self.pokenv.step(act_ind)
        
        return self.pokenv.step(act_ind)