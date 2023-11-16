""" gAIm
The context of the game where the ai-agents play
"""
from discord import Guild, TextChannel, Member
from model.plaier import PlAIer


class GAImContext:
    """The game that holds the AI-agents and the stat"""
    def __init__(self, guild: Guild, channel :TextChannel, member :Member) ->None:
        self.guild = guild
        self.channel = channel
        self.member = member
        self.werewolves_channel : TextChannel = None
        self.name = channel.name
        self.plaier : PlAIer = None
