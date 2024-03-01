from typing import Union
import os

import base64
import requests
import json5
from retrying import retry
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

from llm_utils import ChatSequence, Message



load_dotenv(find_dotenv())


def call_gpt_v(image_path: str, prompt: str) -> dict:
    """
    Calls the OpenAI GPT-4 Vision API to generate a response to the prompt and image.
    """
    # OpenAI API Key
    api_key = os.environ.get("OPENAI_API_KEY")

    # Function to encode the image
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    # Getting the base64 string
    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
        {
            "role": "user",
            "content": [
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
            ]
        }
        ],
        "max_tokens": 500
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return response.json()


def extract_json(answer_str: str) -> dict:
    """
    Extracts the JSON from the OpenAI response string.
    """
    # extract the string between "```json" and "```"
    start_idx = answer_str.find("```json")
    end_idx = answer_str.find("```", start_idx+1)
    json_str = answer_str[start_idx+7:end_idx]

    # convert the string to dict
    try:
        answer_dict = json5.loads(json_str)
        return answer_dict
    except ValueError:
        print(f"Error: \n{json_str}")
        return {}

@retry(wait_fixed=1000, stop_max_attempt_number=3)
def ask_gpt_v(image_path: str, prompt: str) -> dict:
    """
    Asks the OpenAI GPT-4 Vision API to generate a JSON response to the prompt and image.
    """
    response = call_gpt_v(image_path, prompt)
    
    # if the response is successful
    if response.get("id"):
        text_str =  response["choices"][0]['message']['content']
    else:
        # raise an error if the response is not successful
        raise ValueError(response)
    
    json_dict = extract_json(text_str)

    # if JSON is empty, raise an error
    if not json_dict:
        raise ValueError("The JSON is empty")
    
    return json_dict


@retry(wait_fixed=1000, stop_max_attempt_number=3)
def ask_gpt_v_text(image_path: str, prompt: str) -> str:

    # check if the image exists
    if not os.path.exists(image_path):
        return {}

    response = call_gpt_v(image_path, prompt)
    
    # if the response is successful
    if response.get("id"):
        text_str =  response["choices"][0]['message']['content']
    else:
        # raise an error if the response is not successful
        raise ValueError(response)
    
    return text_str


def chat_with_gpt(messages: Union[ChatSequence, list[dict]]) -> str:
    # if messages is a ChatSequence, convert it to a list of dicts
    if isinstance(messages, ChatSequence):
        messages = messages.raw()

    try:
        client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages
            )
    except Exception as err:
        print(f'OPENAI ERROR: {err}')
        raise err

    return response.choices[0].message.content


@retry(wait_fixed=1000, stop_max_attempt_number=3)
def ask_gpt_text(sys_prompt: str, input: str) -> dict:
    """
    Ask the OpenAI GPT-4 API to generate a JSON response to the prompt and input.
    """
    chat_seq = ChatSequence()
    chat_seq.append(Message("system", sys_prompt))
    chat_seq.append(Message("user", input))
    result = chat_with_gpt(chat_seq.raw())

    json_dict = extract_json(result)

    if not json_dict:
        raise ValueError("The JSON is empty")
    
    return json_dict
    

def get_text_embeddings(text: str) -> list[float]:
    """
    Get the text embeddings from the OpenAI API.
    """

    client = OpenAI()

    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )

    return response.data[0].embedding