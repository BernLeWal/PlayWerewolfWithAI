#!/bin/python
""" app.py
Discord app which will generate the bots for the Werewolves games 
on the configured Discord Guild.
"""
import os
import asyncio
from dotenv import load_dotenv

import discord

from plaier_bot import PlaierBot
from moderator_bot import bot


# Load configuration
load_dotenv()
DISCORD_GUILD = os.getenv('DISCORD_GUILD')
DEV_USER_ID = os.getenv('DEV_USER_ID')
MODERATOR_TOKEN = os.getenv('MODERATOR_TOKEN')
PLAIER_TOKEN = os.getenv('PLAIER_TOKEN')


# Setup discord connection and the bot
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True  # This is necessary to access the member list




# Application entry point
if __name__ == "__main__":
    if not os.path.exists('data'):
        os.makedirs('data')

    plaier = PlaierBot(intents, DISCORD_GUILD)

    loop = asyncio.get_event_loop()
    loop.create_task( bot.start(MODERATOR_TOKEN))   #bot.run(MODERATOR_TOKEN)
    loop.create_task( plaier.start(PLAIER_TOKEN))
    loop.run_forever()
