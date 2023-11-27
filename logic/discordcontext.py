"""
State-Machine implementing for Discord
"""
import logging
from discord import Guild, TextChannel

from logic.gamecontext import GameContext


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)


class DiscordContext(GameContext):
    """The game that holds the state"""
    def __init__(self, guild: Guild, channel :TextChannel) ->None:
        super().__init__(channel.name)
        self.guild = guild
        self.channel = channel
        self.werewolves_channel : TextChannel = None


    async def send_msg(self, msg :str) ->None:
        """Sends a message in the channel of the game"""
        await self.channel.send( msg )

    async def send_werewolves(self, msg :str) ->None:
        """Sends a message int the secret channel of the werewolves"""
        if not self.werewolves_channel is None:
            await self.werewolves_channel.send(msg)
        else:
            logger.error("No werewolves channel exist! Send '%s' failed!", msg)
