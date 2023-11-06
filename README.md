# Play Werewolf with AI
An online game based on the famous werewolf cardgame, but also with AI-agents as players. 

It is a case study how well AI-agents (using LLMs) act in human collaboration.
* Are AI agents on a par with humans when it comes to communication and collaboration? 
* Is it fun to play a board game with AI players?
* If not, what improvements could be made to bring AI agents closer to humans, and what could a technical implementation look like?

These questions will be examined and answered in the context of an online board game - the card game "Werewolves". As gaming platform [Discord](https://discord.com) is used.

## The Werewolves Game

It's a social role-playing game that divides a group of people into two camps: the villagers and the werewolves. The objective of the game differs for the two groups. The werewolves aim to eliminate all the villagers, while the villagers aim to identify and eradicate all the werewolves.

The basic gameplay rules:

**Setup:**
Each player draws a card that determines their role in the game (e.g., Werewolf, Villager, Seer, Witch, Hunter, etc.).
Cards are drawn secretly, and each player looks at their card to know their role.
A game leader is chosen. This person will moderate the game, provide instructions, and help enforce the rules.
Gameplay:
The game alternates between night and day phases.

***Night:***
1. All players close their eyes.
2. The game leader asks the werewolves to open their eyes and silently select a villager they wish to "kill."
3. Other special roles, such as the Seer or Witch, may also act, depending on the rules established for those roles.
4. After all special roles have performed their actions, the day begins.

***Day:***
1. All players open their eyes.
2. The game leader announces who has been "killed" during the night.
3. The villagers discuss who they believe might be a werewolf.
4. One player is selected by vote to be "killed"; their role is revealed.
5. A new day-night cycle begins.

**Objective:**
The villagers win if all werewolves are eliminated.
The werewolves win if their number is equal to or greater than the remaining villagers.
There are many variants and additional roles that can be added to the game to make it more interesting or complex.


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
