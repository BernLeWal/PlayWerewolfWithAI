#!/bin/python
""" plaier_bot.py
Discord Bot who will be used for the AI-agents (plAIer) in all Werewolves games 
on the configured Discord Guild.
"""
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

import discord
from discord import TextChannel, Member



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
            "Hello! I am an AI-Player, now online and will be happy to be invited to your Werewolves games!\n"
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


client.run(PLAIER_TOKEN)
