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

client = OpenAI()

class PokeEnv(RolePlaying):
    def __init__(self, env, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Pass all parent-required parameters concisely
        self.pokenv = env
        self.recent_frames = np.zeros(
            (env.frame_stacks, 144, 
             160, 3),
            dtype=np.uint8)

    # Function to encode the image
    def encode_image(self, image):
        return base64.b64encode(image).decode('utf-8')
    
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

        # assistant_msg = BaseMessage.make_assistant_message(
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
              {
                "role": "user",
                "content": [
        {
          "type": "text",
          "text": "The following are the three sequential frames of the pokemon game, which button I should press next?",
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
        return response.choices[0]

        # user_response = self.user_agent.step(assistant_msg)
        # # if user_response.terminated or user_response.msgs is None:

        # return ChatAgentResponse([], user_response.terminated,
        #                                 user_response.info)
        # user_msg = self.reduce_message_options(user_response.msgs)
        # self.user_agent.record_message(user_msg)
