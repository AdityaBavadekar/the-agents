import os
import sys

from absl import logging

import json
import google.generativeai as palm

MODEL_ERROR_MESSAGE = """Something went wrong."""
# Replace with your own. [This one is deleted from console]
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


def SystemMessage(content: str):
    return dict(role="system", content=content)


def AssistantMessage(content: str):
    return dict(role="assistant", content=content)


def UserMessage(content: str):
    return dict(role="user", content=content)


class Mediator:
    def __init__(self, model_name, temperature=0.0, context_text=None):

        self.model = self.find_model_with_name(model_name)
        self.is_chat_mode = 'generateMessage' in self.model.supported_generation_methods

        self.context_text = context_text
        self.history = []

        self.temp = temperature

    def find_model_with_name(self, name):
        try:
            available_models = self.__list_models__()
        except Exception as e:
            print('Error : Unable to list available models')
            print('Error :', str(e))
            exit(-1)

        model_names = []
        for model in available_models:
            if model.name == name:
                return model
            model_names.append(model.name)

        print(f"Invalid model '{name}'\nAvailable are: ", model_names)
        raise AttributeError(f"Model with name '{name}' was not found")

    def __list_models__(self):
        models = [m for m in palm.list_models()]
        print(f"Fetched {len(models)} Models")
        return models

    def validate(self, content: str):
        assert isinstance(content, str) and content.strip() != ''

    def ask_text_with_tools(self, prompt, custom_stop_sequences=[], custom_processing_fn=None):
        """
        custom_processing_fn(prompt, seq, response, equation)

        """
        results = []

        for _ in range(2):
            completion = palm.generate_text(
                model=self.model,
                prompt=prompt,
                stop_sequences=custom_stop_sequences,
                temperature=self.temp,
                candidate_count=1,
                max_output_tokens=800,
            )
            for i, candidate in enumerate(completion.candidates):
                if completion.result:
                    for seq in custom_stop_sequences:
                        if seq in completion.result:
                            response, equation = completion.result.split(seq, maxsplit=1)
                            if custom_processing_fn:
                                response = custom_processing_fn(prompt, seq, response, equation)
                            else: raise Exception('Processing fuction is required')
                            results.append(response)
                            prompt = prompt + response
                    if '<ANSWER_COMPLETED>' in completion.result:
                        break

        return ' '.join(results)

    def ask_text(self, prompt):
        assert not self.is_chat_mode
        self.validate(prompt)

        self.history.append(UserMessage(prompt))

        try:
            completion = palm.generate_text(
                model=self.model,
                prompt=prompt,
                temperature=self.temp,
                candidate_count=1,
                # The maximum length of the response
                max_output_tokens=800,
            )
            if completion.result is None:
                raise Exception('Response is None')
            self.history.append(AssistantMessage(completion.result))
            return completion.result
        except Exception as e:
            print("Error : ", str(e))
            self.history.append(AssistantMessage("No response"))
            return None

    def chat(self, content):
        assert self.is_chat_mode
        self.validate(content)
        self.history.append(UserMessage(content))
        try:
            response = palm.chat(model=self.model, messages=[
                item['content'] for item in self.history],
                temperature=self.temp,
                candidate_count=1,
                context=self.context_text,
                examples=None)
            if response.last is None:
                raise Exception('Response is None, filters:' + str(response.filters))

            self.history.append(AssistantMessage(response.last))
            return response.last
        except Exception as e:
            print("Error : ", str(e))
            self.history.append(AssistantMessage("[NOR]")) #NOR : No Response
            return None


class Agent:

    def __init__(self, model_name=MODEL_NAME_CHAT, context_text=None):
        self.model_error_message = MODEL_ERROR_MESSAGE
        self.palm_none_response = MODEL_ERROR_MESSAGE + "\n[No Response]"

        self.mediator = Mediator(model_name, context_text=context_text)

    def format_question_with_context(self, question, context):
        return f"{context}\nQuestion: {question}"

    def ask_text(self, question):
        response = self.mediator.ask_text(question)
        if response is None:
            return self.palm_none_response
        return response

    def ask_chat(self, question):
        response = self.mediator.chat(question)
        if response is None:
            return self.palm_none_response
        return response


class ChatAgent:
    """Chat Agent for Chat or Conversation Tasks"""

    def __init__(self, context_text=None):
        self._agent_ = Agent(model_name=MODEL_NAME_CHAT,
                             context_text=context_text)

    def ask(self, message):
        return self._agent_.ask_chat(message)


class TextAgent:
    """Simple Text Agent for Question Answering tasks"""

    def __init__(self, context_text=None):
        self._agent_ = Agent(model_name=MODEL_NAME_TEXT,
                             context_text=context_text)

    def ask(self, question):
        return self._agent_.ask_text(question)
