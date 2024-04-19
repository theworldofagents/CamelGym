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
from pyboy.utils import WindowEvent

client = OpenAI()

class PokeEnv(RolePlaying):
    def __init__(self, env, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Pass all parent-required parameters concisely
        self.pokenv = env
        self.recent_frames = np.zeros(
            (env.frame_stacks, 144, 
             160, 3),
            dtype=np.uint8)
        
        self.action_to_index = {
            "DOWN": self.pokenv.valid_actions.index(WindowEvent.PRESS_ARROW_DOWN),
            "LEFT": self.pokenv.valid_actions.index(WindowEvent.PRESS_ARROW_LEFT),
            "RIGHT": self.pokenv.valid_actions.index(WindowEvent.PRESS_ARROW_RIGHT),
            "UP": self.pokenv.valid_actions.index(WindowEvent.PRESS_ARROW_UP),
            "A": self.pokenv.valid_actions.index(WindowEvent.PRESS_BUTTON_A),
            "B": self.pokenv.valid_actions.index(WindowEvent.PRESS_BUTTON_B),
        }

    # Function to encode the image
    def encode_image(self, image):
        return base64.b64encode(image).decode('utf-8')
    
    def reset(self):
        return self.pokenv.reset()

    def render(self):
        return self.pokenv.render()
    
    def close(self):
        return self.pokenv.close()
    
    def step(self):
        frame_list = []
        self.recent_frames = np.roll(self.recent_frames, 1, axis=0)
        self.recent_frames[0] = self.pokenv.render(reduce_res=False)
        for i in range(self.pokenv.frame_stacks):
            img = self.recent_frames[i,...]
            img = Image.fromarray(img)
            # plt.imsave(
            #     self.pokenv.s_path / Path(f'recent_meme_{str(i)}.jpeg'), 
            #     img)
            # Convert the NumPy array to a PIL Imag

            # Save the image to a bytes buffer instead of a file
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            image_data = buffer.getvalue()
            frame_list.append(self.encode_image(image_data))

        lv_rwd = self.pokenv.recent_memory[0, 0]
        hp_rwd = self.pokenv.recent_memory[0, 1]
        exp_rwd = self.pokenv.recent_memory[0, 2]

        # assistant_msg = BaseMessage.make_assistant_message(
        act = None
        while act not in ("A", "B", "UP", "DOWN", "LEFT", "RIGHT"):   
          if act is not None:
              print("LLM return unexpected act:", act)
              print("Run another round") 
          response = client.chat.completions.create(
              model="gpt-4-turbo",
              messages=[
                {
                  "role": "user",
                  "content": [
          {
            "type": "text",
            "text": "In this stage, your level award is: " + str(lv_rwd) + ". Your health reward is: " + str(hp_rwd) + ". Your explore reward is: " + str(exp_rwd) + ". If you find the rewards or game frames not change a lot, you should try pressing different buttons to proceed the progess of the game. The following are the three sequential frames of the pokemon game. Which button should press next? Return me one of the six buttons. You will respond with JSON keys \"UP\", \"DOWN\", \"LEFT\", \"RIGHT\", and \"A\" and \"B\". ",
          },
          {
            "type": "image_url",
            "image_url":  {
                      "url": f"data:image/jpeg;base64,{frame_list[0]}"
                  },
          },
          {
            "type": "image_url",
            "image_url":  {
                      "url": f"data:image/jpeg;base64,{frame_list[1]}"
                  },
          },
          {
            "type": "image_url",
            "image_url":  {
                      "url": f"data:image/jpeg;base64,{frame_list[2]}"
            },
          },
        ],
      }
    ],
      max_tokens=300,
  )
          print('DEBUG: LLM return response', response)
          res = response.choices[0].message.content.split('```json\n')[1].split('\n```')[0]  
          res = json.loads(res)
          act = next((button for button in ["A", "B", "UP", "DOWN", "LEFT", "RIGHT"] if button in res), None)
        print('DEBUG: LLM return action', act)
        act_ind = self.action_to_index[act]
        
        return self.pokenv.step(act_ind)


        # user_response = self.user_agent.step(assistant_msg)
        # # if user_response.terminated or user_response.msgs is None:

        # return ChatAgentResponse([], user_response.terminated,
        #                                 user_response.info)
        # user_msg = self.reduce_message_options(user_response.msgs)
        # self.user_agent.record_message(user_msg)
