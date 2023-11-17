#!/bin/python
""" moderator_bot.py
Discord Bot who will automatically be the moderator of all Werewolves games 
on the configured Discord Guild.
"""
import os
import sys
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv

import discord
from discord.ext import commands
from discord import TextChannel, Member

from plaier_bot import PlaierBot
from logic.gamestate import GameContext, ReadyState
from logic.command import StatusCommand, JoinCommand, QuitCommand, StartCommand, VoteCommand


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)


# Load configuration
load_dotenv()
DISCORD_GUILD = os.getenv('DISCORD_GUILD')


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


#### Helpers
def game_from_breakout_channel(channel :TextChannel) ->GameContext:
    """Fetches the game of the breakout-channel where the Werewolves secretly communicate."""
    for game in GAMES.values():
        if game.werewolves_channel == channel:
            return game
    return None


def game_from_channel(channel :TextChannel) ->GameContext:
    """Fetches the game of the channel, creates a new one if not found."""
    if not channel in GAMES:
        game = GameContext(GUILD, channel)
        GAMES[channel] = game
        return game
    return GAMES[channel]


def game_from_member(author :Member) ->GameContext:
    """Fetches the game where the author is playing."""
    for game in GAMES.values():
        for member in game.players.keys():
            if member==author:
                return game
    return None

def is_general_channel(channel :TextChannel) ->bool:
    """Checks if the channel is the general-channel (which is not used for games)"""
    return channel == GUILD.text_channels[0]


###### Discord Event Handlers:
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
        f'Hi {member.display_name}, welcome to the server of wAIrewolves games!'
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

    # Handle join-command here, because it would ignore these from the plAIer-bot
    if message.content == "!join" and message.author.display_name == "plAIer":
        if is_general_channel(message.channel):
            await message.channel.send( "Games can only be played in the other channels!\n" )
        elif not isinstance(message.channel, discord.DMChannel):
            game = game_from_channel(message.channel)
            await message.channel.send(f"{await game.handle( JoinCommand(message.author))}")

    # Without this, commands won't get processed
    await bot.process_commands(message)


##### Game Commands: #####
@bot.command(name='rules', help='Display the game rules')
async def show_rules(ctx):
    """The game rules are displayed"""
    with open('doc/GAMEPLAY.md','r', encoding="utf-8") as f:
        await ctx.send(f.read())


@bot.command(name='status',
    help="Shows the status of the current game. \n"
    "Every channel except general represents one game")
async def status(ctx):
    """Status command"""
    if is_general_channel(ctx.channel):
        await ctx.send(
            "ModeratorBot is up and running!\n"
            "Join one of the channels to join a Werewolves game!"
        )
    elif isinstance(ctx.channel, discord.DMChannel):
        pass
    else:
        game = game_from_channel(ctx.channel)
        await ctx.send(f"{await game.handle( StatusCommand(ctx.author) )}")


@bot.command(name='join', help='Join the game in the current channel')
async def join(ctx):
    """Join command"""
    if is_general_channel(ctx.channel):
        await ctx.send( "Games can only be played in the other channels!\n" )
    elif isinstance(ctx.channel, discord.DMChannel):
        pass
    else:
        game = game_from_channel(ctx.channel)
        await ctx.send(f"{await game.handle( JoinCommand(ctx.author))}")


@bot.command(name='invite', help='Invite an AI-agent to play with you')
async def invite(ctx, player_name : str = ""):
    """Invite command"""
    if is_general_channel(ctx.channel):
        await ctx.send( "Games can only be played in the other channels!\n")
    else:
        logger.info("AI-agent with name %s was invited!", player_name)


@bot.command(name='quit', help='Leaves the game')
async def quit_bot(ctx):
    """To leave a game (or stop the bot)"""
    if is_general_channel(ctx.channel):
        #The master user (it's me, the developer), stops the bot.
        if str(ctx.author.id) == os.getenv('DEV_USER_ID'):
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
        game = game_from_channel(ctx.channel)
        await ctx.send(f"{await game.handle( QuitCommand(ctx.author))}")


@bot.command(name='start', help='Starts the game with all joint members in the current channel.')
async def start(ctx):
    """Start command"""
    if is_general_channel(ctx.channel):
        await ctx.send( "Games can only be played in the other channels!" )
    elif isinstance(ctx.channel, discord.DMChannel):
        pass
    else:
        game = game_from_channel(ctx.channel)
        await ctx.send(f"{await game.handle( StartCommand(ctx.author))}")


@bot.command(name='vote', help='Votes a player to be selected for the next victim.')
async def vote(ctx, player_name :str):
    """Vote command"""
    if is_general_channel(ctx.channel):
        await ctx.send( "Games can only be player in the other channels!")
    elif isinstance(ctx.channel, discord.DMChannel):
        game = game_from_member(ctx.author)
        if not game is None:
            result = await game.handle( VoteCommand(ctx.author, player_name))
            await ctx.send(result)
            if isinstance(game.state, ReadyState):
                # GAME OVER occured - also tell the others about it
                await game.channel.send(result)
    else:
        game = game_from_breakout_channel(ctx.channel)
        if not game is None:
            result = await game.handle( VoteCommand(ctx.author, player_name))
            await ctx.send(result)
            if isinstance(game.state, ReadyState):
                # GAME OVER occured - also tell the others about it
                await game.channel.send(result)
        else:
            game = game_from_channel(ctx.channel)
            if game is None:
                logger.warning("Game for channel %s not found!", ctx.channel)
            else:
                await ctx.send(f"{await game.handle( VoteCommand(ctx.author, player_name))}")


@bot.event
async def on_command_error(ctx, error):
    """Error Handling"""
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send('Command does not exist: \n'
                       'Type !help to get a list of all commands')

    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(f"An argument {error.param} is missing. Try !<command> help")



# Application entry point
if __name__ == "__main__":
    if not os.path.exists('data'):
        os.makedirs('data')

    plaier = PlaierBot(intents, DISCORD_GUILD)

    loop = asyncio.get_event_loop()
    loop.create_task( bot.start(os.getenv('MODERATOR_TOKEN')) )   #bot.run(MODERATOR_TOKEN)
    loop.create_task( plaier.start(os.getenv('PLAIER_TOKEN')) )
    loop.run_forever()
