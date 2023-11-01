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
print('Starting...')
from prompts_store import CHAT_MODE_PROMPT, TEXT_MODE_PROMPT, CHAT_MODE_CONTEXT, TEXT_MODE_CONTEXT, TEST_PROMPT
from agent import ChatAgent, TextAgent
from absl import logging
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
import sys
import json

VERSION = "1.0.0"
BANNER = f"The Agents v{VERSION}"
TEMPERATURE = 0.8

# Set logging level to WARNING or above to disable progress bar
logging.set_verbosity(logging.WARNING)

ai_console = Console(record=True)#(width=60)
ai_console.rule(BANNER)

CHAT_MODE = False
SUPPER_TESTING_MODE = False
if len(sys.argv) > 1:
    if sys.argv[1] == '--chat':
        CHAT_MODE = True
        print('CHAT-MODE')
    if sys.argv[1] == '--text':
        CHAT_MODE = False
    if sys.argv[1] == '--supper':
        SUPPER_TESTING_MODE = True
        CHAT_MODE = False
        print('SUPPER-MODE')
    if sys.argv[1] == '--help':
        print('Usage:')
        print('\t<script> command')
        print('')
        print('Commands:')
        print('')
        print(' '*4+' --help                    Show help')
        print(' '*4+' --chat                    Start in Chat Mode')
        print(' '*4+' --text                    Start in Text Mode')
        print(' '*4+' --supper                  Start in Super Testing Text Mode')
        sys.exit()


context = CHAT_MODE_CONTEXT if CHAT_MODE else TEXT_MODE_CONTEXT
agent = ChatAgent(context_text=context) if CHAT_MODE else TextAgent(
    context_text=context)
agent._agent_.mediator.temp = TEMPERATURE

def print_question(q: str):
    ai_console.print(Panel.fit("Question: " + q))


def print_response(r: str):
    ai_console.print("PaLM 2 [Answer]:")
    ai_console.print(Panel.fit(Markdown(r)))


def fetch_text_response(question: str):
    question = TEXT_MODE_PROMPT.format(query=question)
    response = agent.ask(question)
    print_response(response)

def fetch_text_response_v2(question: str):
    question = TEST_PROMPT.replace('{user_prompt}',question)
    response = agent.ask(question)
    while not response.startswith("{"):
        response = response[1:]
    while not response.endswith("}"):
        response = response[:-1]
    response = response.replace("{","{ ").replace("}","} ").replace("'","\"")
    try:
        json_data = json.loads(response)
        json_response = ''
        for k,v in json_data.items():
            if isinstance(v, list):
                json_response += f"**{k}** : \n"
                for item in v: json_response += f"\n\t - {item}\n"
                json_response += "\n"

            elif isinstance(v, dict):
                json_response += f"**{k}** : \n"
                for vkey, vvalue in v.items(): json_response += f"\n\t - **{vkey}** : {vvalue}\n"
                json_response += "\n"

            else: json_response += f"**{k}** : {v} \n\n"

        print_response(json_response)
    except Exception as e:
        print(e)
        print_response(response)


def fetch_chat_response(question: str):
    question = CHAT_MODE_PROMPT.format(query=question)
    response = agent.ask(question)
    print_response(response)


def print_intro():
    # ai_console.print("\nHow can I help?")
    return input(" > ")


def print_state(state: str):
    ai_console.print(f"STATE : {state}")


def cli():

    fn_fetch_text = fetch_text_response_v2 if SUPPER_TESTING_MODE else fetch_text_response
    # Initialize Agent
    print_state("Initializing Agent...")

    ai_console.print("\nHello! I'm PaLM 2.\n")

    question = "Hi!"

    # User input loop
    while True:

        print_question(question)

        if CHAT_MODE:
            if question == '[SYS_HISTORY]':
                print('\n\n'.join([f"{message['role']}: {message['content']}" for message in agent._agent_.mediator.history]))
            else:
                fetch_chat_response(question)
        else:
            fn_fetch_text(question)

        question = print_intro()

        if question.lower().strip() in ["exit", "quit"]:
            ai_console.print("Goodbye!")
            ai_console.save_text('last_run_text.txt')
            sys.exit()


if __name__ == "__main__":
    cli()
