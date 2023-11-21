"""
Representing a player in a Werewolve game
"""
import asyncio
import logging

from discord import TextChannel, Member
from agents.openai_agent import OpenAIAgent

from model.card import Card


# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)



class Player:
    """Representing a player"""
    def __init__(self, name :str) ->None:
        self.name = name
        self.card : Card = None
        self.night_vote : Player = None
        self.day_vote : Player = None
        self.seer_asked_werewolf = False
        self.is_dead = False


    def reset(self) ->None:
        """Resets the players values"""
        self.card : Card = None
        self.night_vote : Player = None
        self.day_vote : Player = None
        self.seer_asked_werewolf = False
        self.is_dead = False


    async def send_dm(self, msg :str) ->None:
        """Sends a direct message to the player"""


class HumanPlayer(Player):
    """Representing a human player"""
    def __init__(self, member :Member) ->None:
        super().__init__(member.display_name)
        self.member = member

    async def send_dm(self, msg :str) ->None:
        """Sends a direct message to the player"""
        logger.debug( "Send DM to %s", self.member)
        await self.member.create_dm()
        await self.member.dm_channel.send( msg )
        logger.debug( "Sending DM to %s done", self.member)



class AIAgentPlayer(Player):
    """Representing a AI-agent player"""
    def __init__(self, name :str) ->None:
        super().__init__(str)
        self.message_queue = asyncio.Queue()
        self.agent = OpenAIAgent()
        logger.info("Created AIAgentPlayer with name %s", name)

        self.current_channel = None
        self.current_messages : str = ""
        self.timer_task_name = "$$TimerTask$$"

    async def send_dm(self, msg :str) ->None:
        """Sends a direct message to the player"""
        self.agent.advice( msg, None )

    async def __worker_task__(self):
        while True:
            # Get message from the queue and process it
            (channel, author_name, message) = await self.message_queue.get()
            logger.debug("Worker processing: %s %s:%s", channel, author_name, message)

            if author_name == "ModeratorBot":
                if message == "!quit":
                    break
                await channel.send(f"{self.agent.ask(message)}")
            elif author_name == self.timer_task_name:
                if not self.current_channel is None:
                    await self.__send_current_messages__()
            else:
                if self.current_channel is None:
                    # It's a new message
                    self.current_channel = channel
                    self.current_messages = f"{author_name}: {message}\n"
                elif self.current_channel == channel:
                    # It adds to the current collaboration
                    self.current_messages += f"{author_name}: {message}\n"
                else:
                    # The collaboration moves to a different channel
                    # --> send current collab to agent now
                    await self.__send_current_messages__()
                    self.current_channel = channel
                    self.current_messages = f"{author_name}: {message}\n"


    async def __send_current_messages__(self) ->None:
        if not self.current_channel is None and len(self.current_messages)>0:
            logger.info("Send to LLM: %s", self.current_messages)
            self.agent.advice(
                "What did the other players say lately?",
                self.current_messages
            )
            self.current_messages = ""
            prompt = "Take part of the recent conversation or give answer."
            await self.current_channel.send(f"{self.agent.ask(prompt)}")
            self.current_channel = None


    async def __timer_task__(self):
        while True:
            await asyncio.sleep(60)   # produce a reminder every minute
            await self.message_queue.put( (None, self.timer_task_name, "SendCurrentMessages") )


    async def start(self) ->None:
        """Start the worker thread"""
        await asyncio.gather(self.__timer_task__(), self.__worker_task__())


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
