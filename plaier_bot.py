#!/bin/python
""" plaier_bot.py
Discord Bot who will be used for the AI-agents (plAIer) in all Werewolves games 
on the configured Discord Guild.
"""
import os
import logging
from dotenv import load_dotenv

import discord
from discord import TextChannel

from logic.gamestate import GameContext
from model.player import AIAgentPlayer


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)




class PlaierBot(discord.Client):
    """Discord Bot who will be used for the AI-agents (plAIer)"""

    def __init__(self, discord_guild_str :str, games :dict[TextChannel, GameContext]) ->None:
        # Setup discord connection and the bot
        my_intents = discord.Intents.default()
        my_intents.message_content = True
        my_intents.messages = True
        my_intents.guilds = True
        my_intents.members = True  # This is necessary to access the member list
        super().__init__(intents=my_intents)
        self.discord_guild_str = discord_guild_str
        self.guild = None    # is set in on_ready()
        self.games = games


    def game_from_channel(self, channel :TextChannel) ->GameContext:
        """Fetches the game of the channel"""
        if not channel in self.games:
            return None
        return self.games[channel]


    def is_general_channel(self, channel :TextChannel) ->bool:
        """Checks if the channel is the general-channel (which is not used for games)"""
        return channel == self.guild.text_channels[0]


    ###### Discord Event Handlers:
    async def on_ready(self):
        """Bot connected to Discord"""
        self.guild = discord.utils.get(self.guilds, name=self.discord_guild_str)

        logger.info("%s is connected to the following guild:%s(id: %s)\n",
            self.user, self.guild.name, self.guild.id )

        general = self.guild.text_channels[0]
        if general and general.permissions_for(self.guild.me).send_messages:
            await general.send(
                "Hello! I am an AI-Player, now online "
                "and will be happy to be invited to your Werewolves games!\n"
            )
        else:
            logger.warning("No 'general' channel found in %s or missing permission to send.",
                self.guild.name)

    async def on_message(self, message):
        """A member sent a message"""
        if message.author == self.user:
            return
        logger.info("%s: %s=%s", message.channel, message.author, message.content)

        # Send messages also to AI-agent players
        game = self.game_from_channel( message.channel )
        if not game is None:
            if message.content.startswith("!invite ") and len(message.content)>9:
                # Add an AI-Agent player
                ai_player_name = message.content[8:]
                logger.info("AI-Agent %s joins the game %s", ai_player_name, game.name)
                player = AIAgentPlayer(ai_player_name, self)
                game.players[ai_player_name] = player
                await player.init()
                await player.add_message(
                    game.channel.id,
                    "ModeratorBot", 
                    "Introduce yourself to the other players."
                )
                await player.start()
            elif message.content.startswith("!"):
                pass
            else:
                # pass the messages to all players
                for player in game.players.values():
                    if isinstance(player, AIAgentPlayer):
                        await player.add_message(message.channel.id,
                                                message.author.display_name,
                                                message.content)


# Application entry point
if __name__ == "__main__":
    # Load configuration
    load_dotenv()

    client = PlaierBot(os.getenv('DISCORD_GUILD'), {})
    client.run(os.getenv('PLAIER_TOKEN'))
