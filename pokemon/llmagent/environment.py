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
from pyboy.utils import WindowEvent

client = OpenAI()
MODEL_ENGINE = "gpt-4-turbo"
USERNAME = "user"
AI_NAME = "assistant"

class PokeEnv(RolePlaying):
    def __init__(self, env, prompt, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Pass all parent-required parameters concisely
        self.pokenv = env
        self.recent_frames = np.zeros(
            (env.frame_stacks, 144, 
             160, 3),
            dtype=np.uint8)
        self.memory = FixedFIFO(15)
        self.last_act = FixedFIFO(3)
        self.press_time = 2
        self.init_prompt = prompt
        
        self.action_to_index = {
            "DOWN": self.pokenv.valid_actions.index(WindowEvent.PRESS_ARROW_DOWN),
            "LEFT": self.pokenv.valid_actions.index(WindowEvent.PRESS_ARROW_LEFT),
            "RIGHT": self.pokenv.valid_actions.index(WindowEvent.PRESS_ARROW_RIGHT),
            "UP": self.pokenv.valid_actions.index(WindowEvent.PRESS_ARROW_UP),
            "A": self.pokenv.valid_actions.index(WindowEvent.PRESS_BUTTON_A),
            "B": self.pokenv.valid_actions.index(WindowEvent.PRESS_BUTTON_B),
        }
        self.history = []
        init_res = self.handle_input(prompt, self.history, 'system', AI_NAME)
        print('DEBUG: LLM init response:', init_res)

    # Function to encode the image
    def encode_image(self, image):
        return base64.b64encode(image).decode('utf-8')
    
    def add_memory(self, msg):
        self.memory.push(msg)
    
    def reflection(self):
        # summerize the current state based on previous summerized memory and the last msg
        response = client.chat.completions.create(
                      model="gpt-4-turbo",
                      messages=[
                        {
                          "role": "user",
                          "content": [
                                        {
            "type": "text",
            "text": "You are playing Pokemon Red on GameBoy, and your goal is to explore more of the game. You had returned me the button you pressed based on the given screenshots." +
            "Given the previous game memory, briefly summerize what you are previously doing, and reflect what shoud do next to proceed the game. " + 
            "Your previous memories are:" + str(self.memory.get_all())
            #Here is your last game state:" + str(self.memory.get_item(0)) + ". And here is the last message you produced:" + str(msg),
          },
                ],
              }
            ],
              max_tokens=300,
          )
        res = response.choices[0].message.content
        print('DEBUG: LLM return reflection:', res)
        return res
    
    def reset(self):
        return self.pokenv.reset()

    def render(self):
        return self.pokenv.render()
    
    def close(self):
        return self.pokenv.close()

    def get_response(self, prompt):
        """Returns the response for the given prompt using the OpenAI API."""
        completions = client.chat.completions.create(
                model = MODEL_ENGINE,
                messages = prompt,
            max_tokens = 300,
        )
        return completions.choices[0].message.content

    def content_wrap(self, content, type = 'text'):
        return [
            {
              "type": type,
              "text": content,
            }
        ]

    def handle_input(self,
                  input_msg : str,
        conversation_history : list,
                    USERNAME : str,
                    AI_NAME : str,
                    ):
        """Updates the conversation history and generates a response using GPT."""
        # Update the conversation history

        conversation_history.append({
            "role": USERNAME,
            "content": self.content_wrap(input_msg)
        })
      
        # Generate a response using GPT-3
        message = self.get_response(conversation_history)

        conversation_history.append({
            "role": AI_NAME,
            "content": self.content_wrap(message)
        })

        # Print the response
        # print(f'{AI_NAME}: {message}')
        
        return message

    
    def step(self, n = 0):
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
        while act not in ("A", "B", "UP", "DOWN", "LEFT", "RIGHT"):   

          if act is not None:
              print("LLM return unexpected act:", act)
              print("Run another round") 
          # print("DEBUG: the prompt is: Your current state of the game is: " + str(self.memory.get_item(0)) + "." + "Your last action is: " + str(self.last_act.get_item(0)) + '.')
          # print("DEBUG: memory in prompt is: " + str(self.memory.get_all()))

          # Get the user's input
          user_input = [{
            "type": "text",
            # "text": "In this stage, your level award is: " + str(lv_rwd) + ". Your health reward is: " + str(hp_rwd) + ". Your explore reward is: " + str(exp_rwd) + ". If you find the rewards or game frames not change a lot, you should try pressing different buttons to proceed the progess of the game. 
            "text": 
            # "You are playing Pokemon Red on GameBoy, and your goal is to explore more of the game. Next, I would give you a sequntial of its game screenshot, and you should return me the next button you should press. Three have six buttons you can press, which are UP, DOWN, LEFT, RIGHT, A and B. Consider you would press that button a very shot time, like 0.5 second. " +
            # "After you press a button, we would return you three reward values respectively indicate pokemons' levels, pokemons' health, and the explore progress of the game. Your actions are supposed to maximize these reward values." +
            # "The following are the three sequential frames of the pokemon game. The last one is the current frame, and that is what you should exceptionally focus on. Which button should press next? Return me one of the six buttons. You will respond with JSON keys \"UP\", \"DOWN\", \"LEFT\", \"RIGHT\", and \"A\" and \"B\". " +
            "The following is the current frame. Which button should press next? and with how much probability? Return a JSON array as the result." 
            # "Your decision should consider your previous game experiences." +
            #"If your actions did not change the game states a lot, you should try different actions from your previous ones." + 
            # "Your previous reflection of the game is: " + str(self.reflection()) 
            # "Your last three actions are: 1." + str(self.last_act.get_item(0)) + "." + "2." + str(self.last_act.get_item(1)) + "." + "3." + str(self.last_act.get_item(2)) + "."
          },
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
          {
            "type": "image_url",
            "image_url":  {
                      "url": f"data:image/jpeg;base64,{frame_list[0]}"
            },
          }]

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

        for _ in range(self.press_time):
            self.pokenv.step(act_ind)
        
        return self.pokenv.step(act_ind)


        # user_response = self.user_agent.step(assistant_msg)
        # # if user_response.terminated or user_response.msgs is None:

        # return ChatAgentResponse([], user_response.terminated,
        #                                 user_response.info)
        # user_msg = self.reduce_message_options(user_response.msgs)
        # self.user_agent.record_message(user_msg)
