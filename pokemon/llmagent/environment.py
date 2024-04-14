from camel.societies import RolePlaying 
from camel.messages import BaseMessage
from camel.responses import ChatAgentResponse
import base64
import requests

class PokeEnv(RolePlaying):
    def __init__(self, env, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Pass all parent-required parameters concisely
        self.env = env

    # Function to encode the image
    def encode_image(image):
        return base64.b64encode(image).decode('utf-8')
    
    def step(self):
        frame_list = []
        for i in range(self.frame_stacks):
            frame_list.append(self.encode_image(self.recent_frames[i,...]))
        
        assistant_msg = BaseMessage.make_assistant_message(
            role_name=self.assistant_sys_msg.role_name,
            content=([
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
      ]))

        user_response = self.user_agent.step(assistant_msg)
        # if user_response.terminated or user_response.msgs is None:

        return ChatAgentResponse([], user_response.terminated,
                                        user_response.info)
        # user_msg = self.reduce_message_options(user_response.msgs)
        # self.user_agent.record_message(user_msg)
