""" gAIm
The context of the game where the ai-agents play
"""
import logging
from discord import Guild, TextChannel
from model.plaier import PlAIer


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)


class GAImContext:
    """The game that holds the AI-agents and the stat"""
    def __init__(self, guild: Guild, channel :TextChannel) ->None:
        self.guild = guild
        self.channel = channel
        self.werewolves_channel : TextChannel = None
        self.name = channel.name
        self.plaier : PlAIer = None
        logger.info("Created GAImContext on guild %s in channel %s", guild.name, channel.name)
