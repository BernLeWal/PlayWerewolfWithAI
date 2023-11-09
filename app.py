#!/bin/python
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

import discord
from discord.ext import commands


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__) # This logger will inherit the settings from the root logger, configured above


# Load configuration
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
DEV_USER_ID = os.getenv('DEV_USER_ID')


# Setup discord connection and the bot
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True  # This is necessary to access the member list

bot = commands.Bot(command_prefix='!', intents=intents)


# Discord Event Handlers:
@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    logger.info(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

    members = '\n - '.join([str(member) for member in guild.members])
    logger.info(f'Guild Members:\n - {members}\n')

    channels = '\n - '.join([str(channel) for channel in guild.text_channels])
    logger.info(f'Guild Channels:\n - {channels}\n')

    general = guild.text_channels[0]   #discord.utils.get(guild.text_channels, name="Allgemein")  # in english
    if general and general.permissions_for(guild.me).send_messages:
        await general.send(
            f'Hello! I am now online and will moderate the Werewolves games!\n'
            f'Enter !help to get a list of all commands.'
            )
    else:
        logger.warn(f"No 'general' channel found in {guild.name} or missing permission to send messages.")



@bot.command(name='quit', help='Shuts down the bot (accessible only by the master-user ;-) )')
async def quit(ctx):
    if str(ctx.author.id) == DEV_USER_ID:
        logger.info(f'{ctx.author.id} shuts down the bot!')
        await ctx.send("I'll take a nap, bye...")
        await bot.close()
        sys.exit(0)
    else:
        logger.warn(f'{ctx.author.id} wanted to shut down the bot!')
        await ctx.send('You do not have permission to shut down the bot.')


@bot.command(name='rules', help='Display the game rules')
async def show_rules(ctx):
    with open('doc/GAMEPLAY.md','r') as f:
        await ctx.send(f.read())


@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to the server of wAIrewolves games!'
    )


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    logger.debug(f'{message.channel}: {message.author}={message.content}')

    # write channel messages to later use to analyze and improve the AI-player bot
    with open(f'data/{message.channel}.csv','a') as f:
        timestamp_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f'{timestamp_string};{message.author};{message.content}\n')

    # Without this, commands won't get processed
    await bot.process_commands(message)



bot.run(TOKEN)