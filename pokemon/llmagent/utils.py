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

def get_response(client, model, prompt):
    """Returns the response for the given prompt using the OpenAI API."""
    completions = client.chat.completions.create(
            model = model,
            messages = prompt,
        max_tokens = 300,
    )
    return completions.choices[0].message.content

def content_wrap(content, type = 'text'):
    return [
        {
            "type": type,
            type: content,
        }
    ]

def handle_input(
                input_msg,
                client,
                model,
    conversation_history : list,
                USERNAME : str,
                AI_NAME : str,
                ):
    """input_msg is a wrapped content"""
    """Updates the conversation history and generates a response using GPT."""
    # Update the conversation history

    conversation_history.append({
        "role": USERNAME,
        "content": input_msg
    })
    
    # Generate a response using GPT-3
    message = get_response(client, model, conversation_history)

    conversation_history.append({
        "role": AI_NAME,
        "content": content_wrap(message)
    })

    # Print the response
    # print(f'{AI_NAME}: {message}')
    
    return message


def encode_img(image):
    img = Image.fromarray(image)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    image_data = buffer.getvalue()
    
    return base64.b64encode(image_data).decode('utf-8')

def json_parser(input):
    res = input.split('```json\n')[1].split('\n```')[0]  
    res = json.loads(res)
    return res
