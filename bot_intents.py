"""
Intents for the discord bots
"""
import discord

bot_intents = discord.Intents.default()
bot_intents.message_content = True
bot_intents.messages = True
bot_intents.guilds = True
bot_intents.members = True  # This is necessary to access the member list
