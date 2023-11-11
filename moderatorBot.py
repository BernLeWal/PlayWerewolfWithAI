#!/bin/python
""" moderatorBot.py
Discord Bot who will automatically be the moderator of all Werewolves games 
on the configured Discord Guild.
"""
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

import discord
from discord.ext import commands
from discord import TextChannel

from logic.gamestate import GameContext
from logic.command import StatusCommand, JoinCommand, QuitCommand, StartCommand


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)


# Load configuration
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_GUILD = os.getenv('DISCORD_GUILD')
DEV_USER_ID = os.getenv('DEV_USER_ID')


# Setup discord connection and the bot
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True  # This is necessary to access the member list

bot = commands.Bot(command_prefix='!', intents=intents)

# Global variables (singletons ;-) )
GUILD = None    # is set in on_ready()
GAMES: dict[TextChannel, GameContext] = {}


# Discord Event Handlers:
@bot.event
async def on_ready():
    """Bot connected to Discord"""
    global GUILD
    GUILD = discord.utils.get(bot.guilds, name=DISCORD_GUILD)

    logger.info("%s is connected to the following guild:\n%s(id: %s)\n",
        bot.user, GUILD.name, GUILD.id )

    members = '\n - '.join([str(member) for member in GUILD.members])
    logger.info("Guild Members:\n - %s\n", members)

    channels = '\n - '.join([str(channel) for channel in GUILD.text_channels])
    logger.info("Guild Channels:\n - %s\n", channels)

    general = GUILD.text_channels[0]
    if general and general.permissions_for(GUILD.me).send_messages:
        await general.send(
            "Hello! I am now online and will moderate the Werewolves games!\n"
            "Enter !help to get a list of all commands."
            )
    else:
        logger.warning("No 'general' channel found in %s or missing permission to send messages.",
            GUILD.name)


@bot.event
async def on_member_join(member):
    """A member joined the Discord guild"""
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to the server of wAIrewolves games!'
    )


@bot.event
async def on_message(message):
    """A member sent a message"""
    if message.author == bot.user:
        return

    logger.debug("%s: %s=%s", message.channel, message.author, message.content)

    # write channel messages to later use to analyze and improve the AI-player bot
    with open(f'data/{message.channel}.csv', 'a', encoding="utf-8") as f:
        timestamp_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f'{timestamp_string};{message.author};{message.content}\n')

    if message.guild is None:
        # a direct message from a player to the bot
        for game in GAMES.values():
            game.handle_dm_from_seer(message.author)

    # Without this, commands won't get processed
    await bot.process_commands(message)


# Game Commands:
@bot.command(name='rules', help='Display the game rules')
async def show_rules(ctx):
    """The game rules are displayed"""
    with open('doc/GAMEPLAY.md','r', encoding="utf-8") as f:
        await ctx.send(f.read())


@bot.command(name='status', help='Shows the status of the current game. \nEvery channel except general represents one game')
async def status(ctx):
    """Status command"""
    if ctx.channel == GUILD.text_channels[0]:
        await ctx.send(
            "ModeratorBot is up and running!\n"
            "Join one of the channels to join a Werewolves game!"
        )
    elif isinstance(ctx.channel, discord.DMChannel):
        pass
    else:
        game = None
        if not ctx.channel in GAMES:
            game = GameContext(ctx.channel)
        else:
            game = GAMES[ctx.channel]
        await ctx.send(f"{await game.handle( StatusCommand(ctx.author) )}")


@bot.command(name='join', help='Join the game in the current channel')
async def join(ctx):
    """Join command"""
    if ctx.channel == GUILD.text_channels[0]:
        await ctx.send( "Games can only be played in the other channels (one channel represents one game)!\n" )
    elif isinstance(ctx.channel, discord.DMChannel):
        pass
    else:
        game = None
        if not ctx.channel in GAMES:
            game = GameContext(ctx.channel)
            GAMES[ctx.channel] = game
        else:
            game = GAMES[ctx.channel]
        await ctx.send(f"{await game.handle( JoinCommand(ctx.author))}")


@bot.command(name='quit', help='Leaves the game')
async def quit_bot(ctx):
    """To leave a game (or stop the bot)"""
    if ctx.channel == GUILD.text_channels[0]:
        #The master user (it's me, the developer), stops the bot.
        if str(ctx.author.id) == DEV_USER_ID:
            logger.info("%s shuts down the bot!", ctx.author.id)
            await ctx.send("I'll take a nap, bye...")
            await bot.close()
            sys.exit(0)
        else:
            logger.warning("%s wanted to shut down the bot!", ctx.author.id)
            await ctx.send('You do not have permission to shut down the bot.')
    elif isinstance(ctx.channel, discord.DMChannel):
        pass
    else:
        game = None
        if not ctx.channel in GAMES:
            game = GameContext(ctx.channel)
            GAMES[ctx.channel] = game
        else:
            game = GAMES[ctx.channel]
        await ctx.send(f"{await game.handle( QuitCommand(ctx.author))}")


@bot.command(name='start', help='Starts the Werewolves game with all members in the current channel.')
async def start(ctx):
    """Start command"""
    if ctx.channel == GUILD.text_channels[0]:
        await ctx.send( "Games can only be played in the other channels (one channel represents one game)!\n" )
    elif isinstance(ctx.channel, discord.DMChannel):
        pass
    else:
        game = None
        if not ctx.channel in GAMES:
            game = GameContext(ctx.channel)
        else:
            game = GAMES[ctx.channel]
        await ctx.send(f"{await game.handle( StartCommand(ctx.author))}")


bot.run(DISCORD_TOKEN)
