""" aiagent.py
The base class for integrating LLMs for AI-Agents.
"""
import logging
import asyncio
import threading
from dotenv import load_dotenv


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)


# Load configuration
load_dotenv()


class AIAgent:
    """Accesses the OpenAI API, will keep track of the context"""
    def __init__(self) ->None:
        self.messages = []
        self.result :str = None


    def system(self, content :str):
        """Starts with a new context (a reset), and provides the chat-systems general behavior"""

    def advice(self, question :str, answer :str) ->None:
        """Provides ChatGPT with a predefined question-answer pair """

    def ask(self, prompt :str) ->str:
        """Sends a prompt to ChatGPT, will track the result in the context"""
        return prompt

    async def ask_async(self, prompt :str ) ->str:
        """Sends a prompt to ChatGPT via async, tracks the result in the context"""
        thread = threading.Thread(target=self.ask, args=(prompt,))
        thread.start()
        while thread.is_alive and self.result is None:
            await asyncio.sleep(1)
        return self.result
