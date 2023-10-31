import os
import sys

from absl import logging

import json
import google.generativeai as palm

MODEL_ERROR_MESSAGE = """Something went wrong."""
GOOGLE_PALM_API_KEY = "AIzaSyBrwy6q71vjEuADhoiZqriXDmnyMuSR6oU"
palm.configure(api_key=GOOGLE_PALM_API_KEY)
"""
MODELS AS OF 31st October 2023 :
*********************************************
-| Model(name='models/chat-bison-001',
    version='001', 
    display_name='Chat Bison', 
    description='Chat-optimized generative language model.', 
    input_token_limit=4096, 
    output_token_limit=1024, 
    supported_generation_methods=['generateMessage', 'countMessageTokens'], 
    temperature=0.25, top_p=0.95, top_k=40)

-| Model(name='models/text-bison-001',
    version='001', 
    display_name='Text Bison', 
    description='Model targeted for text generation.', 
    input_token_limit=8196, 
    output_token_limit=1024, 
    supported_generation_methods=['generateText', 'countTextTokens', 'createTunedTextModel'], 
    temperature=0.7, top_p=0.95, top_k=40)

-| Model(name='models/embedding-gecko-001', 
    version='001', 
    display_name='Embedding Gecko', 
    description='Obtain a distributed representation of a text.', 
    input_token_limit=1024, 
    output_token_limit=1, 
    supported_generation_methods=['embedText'], 
    temperature=None, top_p=None, top_k=None)

*********************************************
"""

MODEL_NAME_CHAT = "models/chat-bison-001"
MODEL_NAME_TEXT = "models/text-bison-001"

def SystemMessage(content:str):
    return dict(role="system",content=content)

def AssistantMessage(content:str):
    return dict(role="assistant",content=content)

def UserMessage(content:str):
    return dict(role="user",content=content)

class Mediator:
    def __init__(self, model_name, is_chat=False, temperature=0.0, context_text=None):
        models = self.__list_models__()
        model_names = [m.name for m in models]
        if model_name not in model_names:
            print(f"Invalid model '{model_name}'\nAvailable are: ", model_names)
            exit(-1)
        self.model = [m for m in models if m.name == model_name][0]
        self.context_text = context_text
        self.history = []
        if temperature == None:
            temperature = 0.7
        self.temp = temperature

    def __list_models__(self):
        models = [m for m in palm.list_models()]
        print(f"Fetched {len(models)} Models")
        return models

    def validate(self, content:str):
        assert isinstance(content, str) and content.strip() != '' 

    def ask_text(self, prompt):
        self.validate(prompt)
        self.history.append(UserMessage(content))
        completion = palm.generate_text(
            model=self.model,
            prompt=prompt,
            temperature=self.temp,
            # The maximum length of the response
            max_output_tokens=800,
        )
        self.history.append(AssistantMessage(completion.result))
        return completion.result

    def chat(self, content):
        self.validate(content)
        self.history.append(UserMessage(content))
        response = None
        try:
            response = palm.chat(model=self.model ,messages=[item['content'] for item in self.history], temperature=self.temp, candidate_count=1, context=self.context_text, examples=None)
            if response is None: raise Exception('Response is None')
            self.history.append(AssistantMessage(response.last))
            return response.last
        except Exception as e:
            print("Error : ",str(e))
            self.history.append(AssistantMessage("No response"))
            return None


class Agent:

    def __init__(self, model_name=MODEL_NAME_CHAT, context_text=None):
        self.model_error_message = MODEL_ERROR_MESSAGE
        self.palm_none_response = MODEL_ERROR_MESSAGE + "\n[No Response]"
        self.mediator = Mediator(model_name, context_text=context_text)

    def format_question_with_context(self, question, context):
        new_prompt = f"{context}\nQuestion: {question}"
        return new_prompt

    def ask_text(self, question):
        response = self.mediator.ask_text(question)
        return response

    def ask_chat(self, question):
        response = self.mediator.chat(question)
        if response is None:
            return self.palm_none_response
        return response
