"""
Representing a player in a Werewolve game
"""
import asyncio
import logging

from discord import Member
from agents.openai_agent import OpenAIAgent

from model.card import Card


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
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
    def __init__(self, name :str, bot) ->None:
        super().__init__(name)
        self.message_queue = asyncio.Queue()
        self.agent = OpenAIAgent()
        self.bot = bot
        logger.info("Created AIAgentPlayer with name %s", self.name)

        self.current_channel_id = -1
        self.current_messages : str = ""

        self.timer_task_name = "$$TimerTask$$"
        self.timer_task = None
        self.worker_task = None

    def __del__(self) ->None:
        self.stop()
        logger.info("Deleted AIAgentPlayer named %s", self.name)


    async def send_dm(self, msg :str) ->None:
        """Sends a direct message to the player"""
        logger.info("Sent DM '%s' to AIPlayer %s", msg, self.name)
        self.agent.advice( msg, None )

    async def __worker_task__(self):
        while True:
            # Get message from the queue and process it
            (channel_id, author_name, message) = await self.message_queue.get()
            logger.debug("Worker processing: channel_id=%d %s:%s", channel_id, author_name, message)

            if author_name == "ModeratorBot":
                if message == "!quit":
                    break
                await self.bot.get_channel(channel_id).send(f"{self.agent.ask(message)}")
            elif author_name == self.timer_task_name:
                if not self.current_channel_id == -1:
                    await self.__send_current_messages__()
            else:
                if self.current_channel_id == -1:
                    # It's a new message
                    self.current_channel_id = channel_id
                    self.current_messages = f"{author_name}: {message}\n"
                elif self.current_channel_id == channel_id:
                    # It adds to the current collaboration
                    self.current_messages += f"{author_name}: {message}\n"
                else:
                    # The collaboration moves to a different channel
                    # --> send current collab to agent now
                    await self.__send_current_messages__()
                    self.current_channel_id = channel_id
                    self.current_messages = f"{author_name}: {message}\n"


    async def __send_current_messages__(self) ->None:
        if self.current_channel_id > -1 and len(self.current_messages)>0:
            logger.info("Send to LLM: %s", self.current_messages)
            self.agent.advice(
                "What did the other players say lately?",
                self.current_messages
            )
            self.current_messages = ""
            prompt = "Take part of the recent conversation or give answer."
            await self.bot.get_channel(self.current_channel_id).send(f"{self.agent.ask(prompt)}")
            self.current_channel_id = -1


    async def __timer_task__(self):
        while True:
            await asyncio.sleep(60)   # produce a reminder every minute
            await self.message_queue.put( (-1, self.timer_task_name, "SendCurrentMessages") )


    async def start(self) ->None:
        """Start the worker thread"""
        self.worker_task = asyncio.create_task(self.__worker_task__())
        self.timer_task = asyncio.create_task(self.__timer_task__())
        await asyncio.gather(self.timer_task, self.worker_task)

    def stop(self) ->None:
        """Stop the worker threads"""
        if not self.worker_task is None:
            self.worker_task.cancel()
            self.worker_task = None
        if not self.timer_task is None:
            self.timer_task.cancel()
            self.timer_task = None


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


    async def add_message(self, channel_id :int, author_name :str, message :str) ->None:
        """Put a message in the queue"""
        logger.info("Inform AI-Player %s about message '%s:%s'", self.name, author_name, message)
        await self.message_queue.put( (channel_id, author_name, message) )
