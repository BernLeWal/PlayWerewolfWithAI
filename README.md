# Play Werewolf with AI
An online game based on the famous werewolf cardgame, but also with AI-agents as players. 

It is a case study how well AI-agents (using LLMs) act in human collaboration.
* Are AI agents on a par with humans when it comes to communication and collaboration? 
* Is it fun to play a board game with AI players?
* If not, what improvements could be made to bring AI agents closer to humans, and what could a technical implementation look like?

These questions will be examined and answered in the context of an online board game - the card game "Werewolves". As gaming platform [Discord](https://discord.com) is used.

## The Werewolves Game

It's a social role-playing game that divides a group of people into two camps: the villagers and the werewolves. The objective of the game differs for the two groups. The werewolves aim to eliminate all the villagers, while the villagers aim to identify and eradicate all the werewolves.

The villagers win if all werewolves are eliminated.
The werewolves win if their number is equal to or greater than the remaining villagers.

Details see [Werewolve Game Rules](doc/GAMEPLAY.md)

## Pre-Requisites

Install the required packages
```
pip install -r requirements.txt
```
See the contents of [requirements.txt](requirements.txt) to check out which libraries are needed


Create an application and guild on Discord:
1. Create a Discord Account or login: [Discord](https://discord.com)
2. Login at the Discord [Developer Portal](http://discordapp.com/developers/applications)
3. Create a new application, fill out the "General Information" form
4. Create a new bot, fill out the "Build-A-Bot" form
5. Head to the Discord [Home](https://discord.com) Page and create a new guild (which is a server)
6. In the [Developer Portal](http://discordapp.com/developers/applications) add the Bot to the guild using OAuth2 URL Generator, set Scopes=Bot and Permissions=Administrator.   
   ATTENTION: Also enable the privileged intents!
7. The generated URL open in the browser and authorize the bot.

For a detailed tutorial see [Real Python: How to Make a Discord Bot in Python](https://realpython.com/how-to-make-a-discord-bot-python/)

## Run the application
```
python app.py
```

Open the Discord Home in the browser, and open the "General" channel in your guild.
