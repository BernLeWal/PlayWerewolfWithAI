"""
State-Machine implementing the various states in the game play
"""
from discord import TextChannel
from discord import Member

from logic.command import GameCommand, StatusCommand, JoinCommand, QuitCommand, StartCommand
from model.player import Player
from model.card import shuffle, WerewolfCard, SeerCard


class GameContext:
    """The game that holds the state"""
    def __init__(self, channel :TextChannel) ->None:
        self.channel = channel
        self.name = channel.name
        self.__state__ = ReadyState()
        self.players: dict[Member, Player] = {}

    async def handle(self, command :GameCommand) ->str:
        """Handle the provided command, returns a text message to be displaye in the channel"""
        return await self.__state__.handle(self, command)

    def change_state(self, next_state) ->None:
        """Change the state, will automatically call on_leave/on_enter"""
        prev_state = self.__state__
        if not prev_state is None:
            prev_state.on_leave( next_state )
        self.__state__ = next_state
        self.__state__.on_enter( prev_state )

    def handle_dm_from_seer(self, author: Member) ->bool:
        """Handles direct messages from the seer."""
        for member, player in self.players.items():
            if member==author and isinstance(player.card, SeerCard):
                if not player.seer_asked_werewolf:
                    # TODO
                    player.seer_asked_werewolf = True




class GameState:
    """Base state class"""

    async def handle(self, game :GameContext, command :GameCommand) ->str:
        """Forwards the command to the corresponding command-handler"""
        if isinstance(command, StatusCommand):
            return await self.handle_status(game, command)
        elif isinstance(command, JoinCommand):
            return await self.handle_join(game, command)
        elif isinstance(command, QuitCommand):
            return await self.handle_quit(game, command)
        elif isinstance(command, StartCommand):
            return await self.handle_start(game, command)
        raise NotImplementedError

    async def handle_status(self, game :GameContext, command :StatusCommand) ->str:
        """Implementation of the Status command"""
        return "Command not supported here!"

    async def handle_join(self, game: GameContext, command :JoinCommand) ->str:
        """Implementation of the Join command"""
        return "Command not supported here!"

    async def handle_quit(self, game: GameContext, command :QuitCommand) ->str:
        """Implementation of the Quit command"""
        return "Command not supported here!"

    async def handle_start(self, game: GameContext, command: StartCommand) ->str:
        """Implementation of the Start command"""
        return "Command not supported here!"

    def on_enter(self, prev_state) ->None:
        """Called before the state is activated"""

    def on_leave(self, next_state) ->None:
        """Called after the state is deactivated"""


class ReadyState(GameState):
    """In the ReadyState the members may join themselves to the players list"""

    async def handle_status(self, game: GameContext, command :StatusCommand) ->str:
        result = "The game is in READY state:\n"
        result += "Currently the following members have registered to play:\n"
        for item in game.players.values():
            result += f"- **{item.name}**\n"
        result += "\nNext steps:\n"
        result += "- **!join** to join the game.\n"
        result += "- **!quit** to leave the game.\n"
        result += "- **!start** to start the game (needs at least 6 players!)"
        return result

    async def handle_join(self, game: GameContext, command :JoinCommand) ->str:
        print(f"{command.author} joins the game {game.name}")
        game.players[command.author] = Player(command.author.display_name)
        return f"{command.author.display_name} joined the game."

    async def handle_quit(self, game: GameContext, command :QuitCommand) ->str:
        print(f"{command.author} quits the game {game.name}")
        if command.author in game.players:
            del game.players[command.author]
        return f"{command.author.display_name} quits the game."

    async def handle_start(self, game: GameContext, command: StartCommand) ->str:
        if len(game.players)<2:  # TODO
            return "Cannot start game. At least six player must join the game via !join command."

        # Shuffle and assign cards
        cards = shuffle(len(game.players))
        for member in game.players.keys():
            card = cards.pop()
            print( f"{member} gets card {card}" )
            game.players[member].card = card
            await member.create_dm()
            await member.dm_channel.send(
                f"You got the card {card.name} in game {game.name}.\n"
                f"{card.desc}"
            )

        # Tell all the Werewolves who they are
        werewolves = []
        for member in game.players.keys():
            if isinstance(game.players[member].card, WerewolfCard):
                werewolves.append(member)
        werewolves_str = " ".join( member.display_name for member in werewolves )
        print(f"The werewolves are:{werewolves_str}")
        for member in werewolves:
            await member.dm_channel.send(
                f"The werewolves team is {werewolves_str},\n"
                " secretly talk to them with direct messages!\n"
                "You need to vote for a villager to be eaten.\n"
                "Tell me your decision using the !vote command in this direct-channel."
            )

        game.change_state( NightState() )
        return "Game started, cards shuffled and distributed."


class NightState(GameState):
    """The night-phase of a game-round"""
    async def handle_status(self, game: GameContext, command :StatusCommand) ->str:
        return "It is night"
