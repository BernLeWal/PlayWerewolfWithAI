#!/bin/python
""" moderator_bot.py
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
from discord import TextChannel, Member

from logic.context import Context
from logic.discordcontext import DiscordContext
from model.command import StatusCommand, JoinCommand, QuitCommand, StartCommand, VoteCommand


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)




class ModeratorBot(commands.Bot):
    """Discord Bot who will be the moderator and story-teller of the Werewolves games"""

    def __init__(self, discord_guild_str :str) ->None:
        # Setup discord connection and the bot
        my_intents = discord.Intents.default()
        my_intents.message_content = True
        my_intents.messages = True
        my_intents.guilds = True
        my_intents.members = True  # This is necessary to access the member list
        super().__init__(command_prefix='!', intents=my_intents)
        self.discord_guild_str = discord_guild_str
        self.guild = None    # is set in on_ready()
        self.games :dict[TextChannel, Context] = {}


    #### Helpers
    def game_from_breakout_channel(self, channel :TextChannel) ->Context:
        """Fetches the game of the breakout-channel where the Werewolves secretly communicate."""
        for game in self.games.values():
            if game.werewolves_channel == channel:
                return game
        return None


    def game_from_channel(self, channel :TextChannel, create = True) ->Context:
        """Fetches the game of the channel, creates a new one if not found."""
        if not channel in self.games:
            if not create:
                return None
            game = DiscordContext(self.guild, channel)
            self.games[channel] = game
            return game
        return self.games[channel]


    def game_from_member(self, player_name) ->Context:
        """Fetches the game where the author is playing."""
        for game in self.games.values():
            for name in game.players.keys():
                if player_name==name:
                    return game
        return None

    def general_channel(self) ->TextChannel:
        """Returns the general channel"""
        return self.guild.text_channels[0]

    def is_general_channel(self, channel :TextChannel) ->bool:
        """Checks if the channel is the general-channel (which is not used for games)"""
        return channel == self.guild.text_channels[0]


    async def send_to_general(self, msg :str) ->None:
        """Sends a message into the general channel"""
        general = self.guild.text_channels[0]
        if general and general.permissions_for(self.guild.me).send_messages:
            await general.send(msg)
        else:
            logger.warning("No 'general' channel found in %s or missing permission to send.\n%s",
                self.guild.name, msg)

    async def send_dm_to(self, member :Member, msg :str) ->None:
        """Sends a direct message to a member"""
        await member.create_dm()
        await member.dm_channel.send(msg)



    ###### Discord Event Handlers:
    async def on_ready(self):
        """Bot connected to Discord"""
        self.guild = discord.utils.get(bot.guilds, name=self.discord_guild_str)

        logger.info("%s is connected to the following guild:%s(id: %s)\n",
            self.user, self.guild.name, self.guild.id )

        members = '\n - '.join([str(member) for member in self.guild.members])
        logger.info("Guild Members:\n - %s\n", members)

        channels = '\n - '.join([str(channel) for channel in self.guild.text_channels])
        logger.info("Guild Channels:\n - %s\n", channels)

        await self.send_to_general("Hello! "
                                   "I am now online and will moderate the Werewolves games!\n"
                "Enter !help to get a list of all commands.")


    async def on_member_join(self, member):
        """A member joined the Discord guild"""
        await self.send_dm_to( member,
            f'Hi {member.display_name}, welcome to the server of wAIrewolves games!'
        )




# Load configuration
load_dotenv()
bot = ModeratorBot(os.getenv('DISCORD_GUILD'))


##### Discord Event Handlers: #####
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

    # Without this, commands won't get processed
    await bot.process_commands(message)


##### Game Commands: #####
@bot.command(name='rules', help='Display the game rules')
async def show_rules(ctx):
    """The game rules are displayed"""
    with open('doc/GAMEPLAY.md','r', encoding="utf-8") as f:
        await ctx.send(f.read())


@bot.command(name='terms', help='Display the terms of use')
async def show_terms(ctx):
    """The terms of use are displayed"""
    chunk_size = 2000
    with open('doc/TERMS-OF-USE.md','r', encoding="utf-8") as f:
        while True:
            chunk = f.read(chunk_size)   # Read a chunk of the specified size
            if not chunk:
                break   # If chunk is empty, end of file is reached
            await ctx.send(chunk)    # Output the chunk
            # Break if the chunk is smaller than the chunk size (end of file)
            if len(chunk) < chunk_size:
                break


@bot.command(name='status',
    help="Shows the status of the current game. \n"
    "Every channel except general represents one game")
async def status(ctx):
    """Status command"""
    if bot.is_general_channel(ctx.channel):
        await bot.send_to_general(
            "ModeratorBot is up and running!\n"
            "Join one of the channels to join a Werewolves game!"
        )
    elif isinstance(ctx.channel, discord.DMChannel):
        pass
    else:
        game = bot.game_from_breakout_channel(ctx.channel)
        if not game is None:
            await game.handle( StatusCommand(ctx.author, ctx.channel) )
        game = bot.game_from_channel(ctx.channel, True)
        if not game is None:
            await game.handle( StatusCommand(ctx.author, ctx.channel) )


@bot.command(name='join', help='Join the game in the current channel')
async def join(ctx):
    """Join command"""
    if bot.is_general_channel(ctx.channel):
        await ctx.send( "Games can only be played in the other channels!\n" )
    elif isinstance(ctx.channel, discord.DMChannel):
        pass
    else:
        game = bot.game_from_channel(ctx.channel)
        await game.handle( JoinCommand(ctx.author))


@bot.command(name='invite', help='Invite an AI-agent to play with you')
async def invite(ctx, player_name : str):
    """Invite command"""
    if bot.is_general_channel(ctx.channel):
        await ctx.send( "Games can only be played in the other channels!\n")
    else:
        logger.info("AI-agent with name %s was invited!", player_name)
        bot.game_from_channel(ctx.channel)
        # processing is done in plaier_bot.py


@bot.command(name='quit', help='Leaves the game')
async def quit_bot(ctx):
    """To leave a game (or stop the bot)"""
    if bot.is_general_channel(ctx.channel):
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
        game = bot.game_from_channel(ctx.channel, False)
        await game.handle( QuitCommand(ctx.author))


@bot.command(name='start', help='Starts the game with all joint members in the current channel.')
async def start(ctx):
    """Start command"""
    if bot.is_general_channel(ctx.channel):
        await ctx.send( "Games can only be played in the other channels!" )
    elif isinstance(ctx.channel, discord.DMChannel):
        pass
    else:
        game = bot.game_from_channel(ctx.channel, False)
        await game.handle( StartCommand(ctx.author))


@bot.command(name='vote', help='Votes a player to be selected for the next victim.')
async def vote(ctx, player_name :str):
    """Vote command"""
    voter_name = ctx.author.display_name
    if bot.is_general_channel(ctx.channel):
        await ctx.send( "Games can only be player in the other channels!")
    elif isinstance(ctx.channel, discord.DMChannel):
        game = bot.game_from_member(voter_name)
        if not game is None:
            await game.handle( VoteCommand(ctx.author, voter_name, player_name))
    else:
        game = bot.game_from_breakout_channel(ctx.channel)
        if not game is None:
            await game.handle( VoteCommand(ctx.author, voter_name, player_name))
        else:
            game = bot.game_from_channel(ctx.channel, False)
            if game is None:
                logger.warning("Game for channel %s not found!", ctx.channel)
            else:
                await game.handle( VoteCommand(ctx.author, voter_name, player_name))


#@bot.event
#async def on_command_error(ctx, error):
#    """Error Handling"""
#    if isinstance(error, commands.errors.CommandNotFound):
#        await ctx.send('Command does not exist: \n'
#                       'Type !help to get a list of all commands')
#    elif isinstance(error, commands.errors.MissingRequiredArgument):
#        await ctx.send(f"An argument {error.param} is missing. Try !<command> help")
#    else:
#        raise error # Re-raise the error to see the full traceback in the console



# Application entry point
if __name__ == "__main__":
    if not os.path.exists('data'):
        os.makedirs('data')

    bot.run(os.getenv('MODERATOR_TOKEN'))
