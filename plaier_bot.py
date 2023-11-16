#!/bin/python
""" plaier_bot.py
Discord Bot who will be used for the AI-agents (plAIer) in all Werewolves games 
on the configured Discord Guild.
"""
import os
import logging
from dotenv import load_dotenv

import discord
from discord import TextChannel, Member

from logic.gaimstate import GAImContext
from model.plaier import PlAIer


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)


# Load configuration
load_dotenv()
DISCORD_GUILD = os.getenv('DISCORD_GUILD')
DEV_USER_ID = os.getenv('DEV_USER_ID')
PLAIER_TOKEN = os.getenv('PLAIER_TOKEN')


# Setup discord connection and the bot
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True  # This is necessary to access the member list

client = discord.Client(intents=intents)

# Global variables (singletons ;-) )
GUILD = None    # is set in on_ready()
GAIMS: dict[TextChannel, GAImContext] = {}

##### Helpers
def gaim_from_channel(channel :TextChannel, member :Member) ->GAImContext:
    """Fetches the game of the channel, creates a new one if not found."""
    if not channel in GAIMS:
        gaim = GAImContext(GUILD, channel, member)
        GAIMS[channel] = gaim
        return gaim
    return GAIMS[channel]


def is_general_channel(channel :TextChannel) ->bool:
    """Checks if the channel is the general-channel (which is not used for games)"""
    return channel == GUILD.text_channels[0]


###### Discord Event Handlers:
@client.event
async def on_ready():
    """Bot connected to Discord"""
    global GUILD
    GUILD = discord.utils.get(client.guilds, name=DISCORD_GUILD)

    logger.info("%s is connected to the following guild:\n%s(id: %s)\n",
        client.user, GUILD.name, GUILD.id )

    members = '\n - '.join([str(member) for member in GUILD.members])
    logger.info("Guild Members:\n - %s\n", members)

    channels = '\n - '.join([str(channel) for channel in GUILD.text_channels])
    logger.info("Guild Channels:\n - %s\n", channels)

    general = GUILD.text_channels[0]
    if general and general.permissions_for(GUILD.me).send_messages:
        await general.send(
            "Hello! I am an AI-Player, now online "
            "and will be happy to be invited to your Werewolves games!\n"
        )
    else:
        logger.warning("No 'general' channel found in %s or missing permission to send messages.",
            GUILD.name)


@client.event
async def on_message(message):
    """A member sent a message"""
    if message.author == client.user:
        return
    logger.debug("%s: %s=%s", message.channel, message.author, message.content)

    if not is_general_channel(message.channel):
        gaim = gaim_from_channel( message.channel, message.author )
        msg : str = message.content

        if msg.startswith("!"):
            cmd_parts = msg.split(' ')

            if cmd_parts[0] == "!invite":
                if len(cmd_parts)<2:
                    await message.channel.send(
                        "Please give the AI-agent a name.\n"
                        "The syntax is: !invite <AsName>"
                    )
                elif not gaim.plaier is None:
                    await message.channel.send("Currently only one AI-agent per game is supported.")
                else:
                    gaim.plaier = PlAIer(cmd_parts[1])
                    await message.channel.send("!join")
                    await gaim.plaier.init()
                    await gaim.plaier.add_message(
                        message.channel,
                        "ModeratorBot", 
                        "Introduce yourself to the other players."
                    )
                    await gaim.plaier.start()




client.run(PLAIER_TOKEN)
