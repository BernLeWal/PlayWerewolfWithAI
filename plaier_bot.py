#!/bin/python
""" plaier_bot.py
Discord Bot who will be used for the AI-agents (plAIer) in all Werewolves games 
on the configured Discord Guild.
"""
import os
import logging
from dotenv import load_dotenv

import discord
from discord import Intents, TextChannel

from logic.gaimstate import GAImContext
from model.plaier import PlAIer


# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)




class PlaierBot(discord.Client):
    """Discord Bot who will be used for the AI-agents (plAIer)"""

    def __init__(self, my_intents :Intents, discord_guild_str :str) ->None:
        super().__init__(intents=my_intents)
        self.discord_guild_str = discord_guild_str
        self.guild = None    # is set in on_ready()
        self.gaims: dict[TextChannel, GAImContext] = {}

    ##### Helpers
    def __gaim_from_channel__(self, channel :TextChannel) ->GAImContext:
        """Fetches the game of the channel, creates a new one if not found."""
        if not channel in self.gaims:
            gaim = GAImContext(self.guild, channel)
            self.gaims[channel] = gaim
            return gaim
        return self.gaims[channel]


    def __is_general_channel__(self, channel :TextChannel) ->bool:
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
        logger.debug("%s: %s=%s", message.channel, message.author, message.content)
        print(f"{message.channel}: {message.author}={message.content}")

        if not self.__is_general_channel__(message.channel):
            gaim = self.__gaim_from_channel__( message.channel )
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
                        await message.channel.send("Only one AI-agent per game supported.")
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

            elif not gaim.plaier is None:
                await gaim.plaier.add_message(message.channel,
                                              message.author.display_name,
                                              message.content)



# Application entry point
if __name__ == "__main__":
    # Load configuration
    load_dotenv()

    # Setup discord connection and the bot
    intents = discord.Intents.default()
    intents.message_content = True
    intents.messages = True
    intents.guilds = True
    intents.members = True  # This is necessary to access the member list

    client = PlaierBot(intents, os.getenv('DISCORD_GUILD'))
    client.run(os.getenv('PLAIER_TOKEN'))
