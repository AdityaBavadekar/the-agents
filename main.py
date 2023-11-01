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
from prompts_store import CHAT_MODE_PROMPT, TEXT_MODE_PROMPT, CHAT_MODE_CONTEXT, TEXT_MODE_CONTEXT
from agent import ChatAgent, TextAgent
from absl import logging
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
import sys

VERSION = "1.0.0"
BANNER = f"The Agents v{VERSION}"
TEMPERATURE = 0.8

# Set logging level to WARNING or above to disable progress bar
logging.set_verbosity(logging.WARNING)

ai_console = Console(record=True)#(width=60)
ai_console.rule(BANNER)

CHAT_MODE = False
if len(sys.argv) > 1:
    if sys.argv[1] == '--chat':
        CHAT_MODE = True
    if sys.argv[1] == '--text':
        CHAT_MODE = False
    if sys.argv[1] == '--help':
        print('Usage:')
        print('\t<script> command')
        print('')
        print('Commands:')
        print('')
        print(' '*4+' --help                    Show help')
        print(' '*4+' --chat                    Start in Chat Mode')
        print(' '*4+' --text                    Start in Text Mode')
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
            fetch_text_response(question)

        question = print_intro()

        if question.lower().strip() in ["exit", "quit"]:
            ai_console.print("Goodbye!")
            ai_console.save_text('last_run_text.txt')
            sys.exit()


if __name__ == "__main__":
    cli()
