"""
Representing an AI-agent which will take part as player in Werewolve games
"""
import asyncio

from discord import TextChannel
from agents.openai_agent import OpenAIAgent


class PlAIer:
    """Representing a AI-agent"""
    def __init__(self, name :str) ->None:
        self.name = name
        self.message_queue = asyncio.Queue()
        self.agent = OpenAIAgent()


    async def __worker_task__(self):
        while True:
            # Get message from the queu and process it
            (channel, author_name, message) = await self.message_queue.get()
            print(f"Worker processing: {author_name}:{message}")
            is_from_moderator = author_name == "ModeratorBot"

            if is_from_moderator:
                if message == "!quit":
                    break
                await channel.send(f"{self.agent.ask(message)}")



    async def start(self) ->None:
        """Start the worker thread"""
        await asyncio.gather(self.__worker_task__())


    async def init(self) ->None:
        """Initialize the context for the LLM"""
        self.agent.system(
            "You are a player of the famous card game 'Werwölfe vom Düsterwald'."
            "You will play together with the werewolves team or with the villagers team, "
            "depending on the card you get."
            "Be curios, be funny, make jokes."
            f"Your name is {self.name}."
            "Do not use more than five sentences in your responses!"
        )


    async def add_message(self, channel :TextChannel, author_name :str, message :str) ->None:
        """Put a message in the queue"""
        await self.message_queue.put( (channel, author_name, message) )
