#!/bin/python
""" openai_agent.py
The OpenAI API Agent to access the API for ChatGPT.
"""
import os
import logging
import asyncio
import threading
from dotenv import load_dotenv

from openai import OpenAI


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)


# Load configuration
load_dotenv()


class OpenAIAgent:
    """Accesses the OpenAI API, will keep track of the context"""
    def __init__(self) ->None:
        #apikey = os.getenv('OPENAI_API_KEY')
        organization = os.getenv('OPENAI_ORGANIZATION')

        self.client = OpenAI(
            # defaults to os.environ.get("OPENAI_API_KEY")
            organization= organization
        )
        self.messages = []
        self.model_name = "gpt-3.5-turbo"

        self.result :str = None


    def system(self, content :str):
        """Starts with a new context (a reset), and provides the chat-systems general behavior"""
        logger.info("Set OpenAIAgent system context:%s", content)
        self.messages = []
        self.messages.append( {"role": "system", "content": content} )

    def advice(self, question :str, answer :str) ->None:
        """Provides ChatGPT with a predefined question-answer pair """
        logger.info("Advice OpenAIAgent Question:'%s', Answer:'%s'", question, answer)
        if not question is None:
            self.messages.append( {"role": "user", "content": question})
        if not answer is None:
            self.messages.append( {"role": "assistant", "content": answer} )

    def ask(self, prompt :str) ->str:
        """Sends a prompt to ChatGPT, will track the result in the context"""
        self.result = None
        logger.info("Ask OpenAIAgent '%s'", prompt)
        self.messages.append({"role": "user", "content": prompt})
        chat_completion = self.client.chat.completions.create(
            messages=self.messages,
            model=self.model_name,
        )
        result = ""
        for choice in chat_completion.choices:
            result += choice.message.content + "\n"
        self.result = result
        self.messages.append({"role": "assistant", "content": result} )
        return result

    async def ask_async(self, prompt :str ) ->str:
        """Sends a prompt to ChatGPT via async, tracks the result in the context"""
        thread = threading.Thread(target=self.ask, args=(prompt,))
        thread.start()
        while thread.is_alive and self.result is None:
            await asyncio.sleep(1)
        return self.result




# Usage
async def main():
    """Async main function"""

    agent = OpenAIAgent()
    agent.system("You are a helpful assistant.")
    agent.advice(
        "Who won the world series in 2020?",
        "The Los Angeles Dodgers won the World Series in 2020."
    )
    #print( await aiagent.ask("Where was it played?") )

    # A demo for asynchronous programming
    task = asyncio.create_task(agent.ask_async("Where was it played?"))
    print("Waiting for the answer...")  # do other stuff...
    print( await task )


if __name__ == "__main__":
    ### Synchronous Call ###
    #agent = OpenAIAgent()
    #agent.system("You are a player of the famous card game 'Werwölfe vom Düsterwald'")
    #print( agent.ask("Tell me the rules of the game.") )

    ### Asynchronous Call ###
    asyncio.run(main())
