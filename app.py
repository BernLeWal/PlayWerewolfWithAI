#!/bin/python
import os
from datetime import datetime
from dotenv import load_dotenv

import discord

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # This is necessary to access the member list
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')


@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to the server of wAIrewolves games!'
    )


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    print(f'{message.channel}: {message.author}={message.content}')

    # write channel messages to later use to analyze and improve the AI-player bot
    with open(f'data/{message.channel}.txt','a') as f:
        timestamp_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f'{timestamp_string} {message.author}: {message.content}\n')

client.run(TOKEN)