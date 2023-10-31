# Auto generated on 31-10-2023-13-03

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

from agent import Agent

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

from absl import logging
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
import sys

context = "Pretend you are a friendly snowman. "

CONTEXT_TEXT = """Your name is Aragot and your are created by Aditya Bavadekar.\
You are my personal assistant.\
Stay in character for every response you give me.\ 
Keep your responses short. Feel free to ask me questions, too."""

# Set logging level to WARNING or above to disable progress bar
logging.set_verbosity(logging.WARNING)

# Initialize Rich console
ai_console = Console(width=60)
ai_console.rule("Assistant")

# Initialize Agent
ai_console.print("STATE: Initializing Agent.")
agent = Agent(context_text=CONTEXT_TEXT)
ai_console.print("\nHello! I'm PaLM 2.\n")


def print_question(q:str):
    ai_console.print(Panel.fit("Question: " + q))

def print_response(r:str):    
    ai_console.print("\nPaLM 2 [Answer]:")
    ai_console.print(Panel.fit(Markdown(r)))

def fetch_response(q:str):
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
        fetch_response(question)

        question = print_intro()    

        if question.startswith("exit"):
            ai_console.print("Goodbye!")
            sys.exit()

if __name__ == "__main__":
    cli()
