#
# Copyright 2023 Aditya Bavadekar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

VERSION = "1.0.0"

"""
88888888888 888                          d8888                            888             
    888     888                         d88888                            888             
    888     888                        d88P888                            888             
    888     88888b.   .d88b.          d88P 888  .d88b.   .d88b.  88888b.  888888 .d8888b  
    888     888 "88b d8P  Y8b        d88P  888 d88P"88b d8P  Y8b 888 "88b 888    88K      
    888     888  888 88888888       d88P   888 888  888 88888888 888  888 888    "Y8888b. 
    888     888  888 Y8b.          d8888888888 Y88b 888 Y8b.     888  888 Y88b.       X88 
    888     888  888  "Y8888      d88P     888  "Y88888  "Y8888  888  888  "Y888  88888P' 
                                                    888                                   
                                               Y8b d88P                                   
                                                "Y88P"                                    
"""

BANNER = f"The Agents [v {VERSION}] "
print(BANNER)

from agent import Agent, MODEL_NAME_CHAT, MODEL_NAME_TEXT



from absl import logging
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
import sys

CONTEXT_TEXT_CHAT = """Your name is Aragot and your are created by Aditya Bavadekar.\
You are my personal assistant.\
Stay in character for every response you give me.\ 
Keep your responses short. Feel free to ask me questions, too."""

CONTEXT_TEXT_NORMAL = """You are an expert at solving problems. Your name is Matheo."""

# Set logging level to WARNING or above to disable progress bar
logging.set_verbosity(logging.WARNING)

# Initialize Rich console
ai_console = Console(width=60)
ai_console.rule("Assistant")

# Initialize Agent
ai_console.print("STATE: Initializing Agent.")
CHAT_MODE = False
CHAT_MODE = str(input("Chat or normal ? [C for Chat , otherwise Normal] ")).strip().lower() in ['c', 'chat']
SELECTED_MODEL = MODEL_NAME_CHAT if CHAT_MODE else MODEL_NAME_TEXT
context = CONTEXT_TEXT_CHAT if CHAT_MODE else CONTEXT_TEXT_NORMAL
agent = Agent(model_name=SELECTED_MODEL, context_text=context)
ai_console.print("\nHello! I'm PaLM 2.\n")

prompt = """Please solve the following problem.

{prompt}

----------------

Important: Use the calculator for each step.
Don't do the arithmetic in your head. 

To use the calculator wrap an equation in <calc> tags like this: 

<calc> 3 cats * 2 hats/cat </calc> = 6

----------------"""

def format(question:str):
    return prompt.format(prompt=question)

def print_question(q:str):
    ai_console.print(Panel.fit("Question: " + q))

def print_response(r:str):
    ai_console.print("\nPaLM 2 [Answer]:")
    ai_console.print(Panel.fit(Markdown(r)))

def fetch_text_response(q:str):
    q = format(q)
    response = agent.ask_text(q)
    print_response(response)

def fetch_chat_response(q:str):
    response = agent.ask_chat(q)
    print_response(response)

def print_intro():
    ai_console.print("")
    ai_console.print("\n######## Ask PaLM 2 ########")
    return input("How can I help?\n> ")
    

def cli():
    question = "Hi!"
        
    # User input loop
    while True:

        print_question(question)
        
        if CHAT_MODE:
            fetch_chat_response(question)
        else: fetch_text_response(question)

        question = print_intro()

        if question.lower().strip() in ["exit","quit"]:
            ai_console.print("Goodbye!")
            sys.exit()

if __name__ == "__main__":
    cli()
