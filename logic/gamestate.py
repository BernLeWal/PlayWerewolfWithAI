"""
State-Machine implementing the various states in the game play
"""
from discord import TextChannel
from discord import Member

from logic.command import GameCommand, StatusCommand, JoinCommand, QuitCommand, StartCommand
from model.player import Player
from model.card import shuffle


class GameContext:
    """The game that holds the state"""
    def __init__(self, channel :TextChannel) ->None:
        self.channel = channel
        self.name = channel.name
        self.state = ReadyState()
        self.players: dict[Member, Member] = {}

    async def handle(self, command :GameCommand) ->str:
        """Handle the provided command, returns a text message to be displaye in the channel"""
        return await self.state.handle(self, command)




class GameState:
    """Base state class"""

    async def handle(self, game :GameContext, command :GameCommand) ->str:
        """Forwards the command to the corresponding command-handler"""
        if isinstance(command, StatusCommand):
            return await self.on_status(game, command)
        elif isinstance(command, JoinCommand):
            return await self.on_join(game, command)
        elif isinstance(command, QuitCommand):
            return await self.on_quit(game, command)
        elif isinstance(command, StartCommand):
            return await self.on_start(game, command)
        raise NotImplementedError

    async def on_status(self, game :GameContext, command :StatusCommand) ->str:
        """Implementation of the Status command"""
        return "Command not supported here!"

    async def on_join(self, game: GameContext, command :JoinCommand) ->str:
        """Implementation of the Join command"""
        return "Command not supported here!"

    async def on_quit(self, game: GameContext, command :QuitCommand) ->str:
        """Implementation of the Quit command"""
        return "Command not supported here!"

    async def on_start(self, game: GameContext, command: StartCommand) ->str:
        """Implementation of the Start command"""
        return "Command not supported here!"


class ReadyState(GameState):
    """In the ReadyState the members may join themselves to the players list"""

    async def on_status(self, game: GameContext, command :StatusCommand) ->str:
        result = "The game is in READY state:\n"
        result += "Currently the following members have registered to play:\n"
        for item in game.players.values():
            result += f"- **{item.name}**\n"
        result += "\nNext steps:\n"
        result += "- **!join** to join the game.\n"
        result += "- **!quit** to leave the game.\n"
        result += "- **!start** to start the game (needs at least 6 players!)"
        return result

    async def on_join(self, game: GameContext, command :JoinCommand) ->str:
        print(f"{command.author} joins the game {game.name}")
        game.players[command.author] = Player(command.author.name)
        return f"{command.author} joined the game."

    async def on_quit(self, game: GameContext, command :QuitCommand) ->str:
        print(f"{command.author} quits the game {game.name}")
        if command.author in game.players:
            del game.players[command.author]
        return f"{command.author} quits the game."

    async def on_start(self, game: GameContext, command: StartCommand) ->str:
        if len(game.players)<2:  # TODO
            return "Cannot start game. At least six player must join the game via !join command."
        cards = shuffle(len(game.players))
        for member in game.players.keys():
            card = cards.pop()
            print( f"{member} gets card {card}" )
            game.players[member].card = card
            await member.create_dm()
            await member.dm_channel.send(f"You got the card {card.name} in game {game.name}.\n{card.desc}")

        game.state = NightState()
        return "Game started, cards shuffled and distributed."


class NightState(GameState):
    """The night-phase of a game-round"""
    async def on_status(self, game: GameContext, command :StatusCommand) ->str:
        return "It is night"
