"""
State-Machine implementing the various states in the game play
"""
import random
from discord import Guild, TextChannel, Member

from logic.command import GameCommand
from logic.command import StatusCommand, JoinCommand, QuitCommand, StartCommand, VoteCommand
from model.player import Player
from model.card import create_cards, WerewolfCard, SeerCard


class GameContext:
    """The game that holds the state"""
    def __init__(self, guild: Guild, channel :TextChannel) ->None:
        self.guild = guild
        self.channel = channel
        self.werewolves_channel : TextChannel = None
        self.name = channel.name
        self.__state__ = ReadyState()
        self.players: dict[Member, Player] = {}

    async def handle(self, command :GameCommand) ->str:
        """Handle the provided command, returns a text message to be displaye in the channel"""
        return await self.__state__.handle(self, command)

    async def change_state(self, next_state) ->None:
        """Change the state, will automatically call on_leave/on_enter"""
        prev_state = self.__state__
        if not prev_state is None:
            await prev_state.on_leave( self, next_state )
        self.__state__ = next_state
        await self.__state__.on_enter( self, prev_state )

    def find_player_by_name(self, player_name: str) ->Player:
        """Finds the player by player_name"""
        for _, player in self.players.items():
            if player.name == player_name:
                return player
        return None

    def get_alive_players_count(self) ->int:
        """Counts the number of alive players"""
        nr_alive = 0
        for _, player in self.players.items():
            if not player.is_dead:
                nr_alive += 1
        return nr_alive


    def check_gameover(self) ->(int, int):
        """Counts the alive werewolves and villagers to check if the game is over."""
        nr_werewolves = 0
        nr_villagers = 0
        for _, player in self.players.items():
            if not player.is_dead:
                if isinstance(player.card, WerewolfCard):
                    nr_werewolves += 1
                else:
                    nr_villagers += 1
        return nr_werewolves, nr_villagers


class GameState:
    """Base state class"""

    async def handle(self, game :GameContext, command :GameCommand) ->str:
        """Forwards the command to the corresponding command-handler"""
        if isinstance(command, StatusCommand):
            return await self.handle_status(game, command)
        if isinstance(command, JoinCommand):
            return await self.handle_join(game, command)
        if isinstance(command, QuitCommand):
            return await self.handle_quit(game, command)
        if isinstance(command, StartCommand):
            return await self.handle_start(game, command)
        if isinstance(command, VoteCommand):
            return await self.handle_vote(game, command)
        raise NotImplementedError


    async def handle_status(self, game :GameContext, command :StatusCommand) ->str:
        """Implementation of the Status command"""
        return f"Command {command.name} not supported here (in {game.name})!"

    async def handle_join(self, game: GameContext, command :JoinCommand) ->str:
        """Implementation of the Join command"""
        return f"Command {command.name} not supported here (in {game.name})!"

    async def handle_quit(self, game: GameContext, command :QuitCommand) ->str:
        """Implementation of the Quit command"""
        return f"Command {command.name} not supported here (in {game.name})!"

    async def handle_start(self, game: GameContext, command: StartCommand) ->str:
        """Implementation of the Start command"""
        return f"Command {command.name} not supported here (in {game.name})!"

    async def handle_vote(self, game: GameContext, command: StartCommand) ->str:
        """Implementation of the Vote command"""
        return f"Command {command.name} not supported here (in {game.name})!"


    async def on_enter(self, game: GameContext, prev_state) ->None:
        """Called before the state is activated"""

    async def on_leave(self, game: GameContext, next_state) ->None:
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
        if len(game.players)<3:  # TODO - set this check to 6 when released
            return "Cannot start game. At least six player must join the game via !join command."

        # Shuffle and assign cards
        cards = create_cards(len(game.players))
        result = "Game started\nThe following cards are in the game:\n"
        for card in cards:
            result += f"- **{card.name}**: {card.desc}\n"
        result += "See your direct-messages from me, to get to know your own card\n"
        result += "and further instructions."
        print(result)

        random.shuffle(cards)
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
        if game.werewolves_channel is None:
            game.werewolves_channel = await game.guild.create_text_channel(
                "WerewolvesOnly_" + game.channel.name
            )
        werewolves_str = " ".join( member.display_name for member in werewolves )
        print(f"The werewolves are:{werewolves_str}")
        for member in werewolves:
            await member.dm_channel.send(
                f"The werewolves team is {werewolves_str},\n"
                f" secretly talk to them in {game.werewolves_channel.name}!\n"
                "You need to vote for a villager to be eaten.\n"
                "Tell me your decision using the !vote command in this direct-channel."
            )
        await game.werewolves_channel.send(
            f"This is the channel for Werewolves in {game.name} only - **PLEASE DON't CHEAT!**\n")
        await game.werewolves_channel.send(
            f"The werewolves team is {werewolves_str},\n"
            "You need to vote for a villager to be your next victim."
        )

        await game.change_state( NightState() )
        return result

    async def on_enter(self, game: GameContext, prev_state) ->None:
        for _, player in game.players.items():
            player.reset()

        await game.channel.send(
            "This GAME is over!\n"
            "Use the !start command to start with a new one."
        )

        if not game.werewolves_channel is None:
            await game.werewolves_channel.delete()
            game.werewolves_channel = None



class NightState(GameState):
    """The night-phase of a game-round"""
    async def handle_status(self, game :GameContext, command :StatusCommand) ->str:
        result = "It is night. The Werewolves seek for their next victim.\n"
        result += "Currently the following are still alive:\n"
        for player in game.players.values():
            if not player.is_dead:
                result += f"- **{player.name}**\n"
        result += "Werewolves use the !vote command."
        return result


    async def handle_vote(self, game :GameContext, command :VoteCommand) ->str:
        # Check if the player is allowed to vote
        player = game.players[command.author]
        if player.is_dead:
            return "Only alive players are allowed to vote!"
        # Check if the victim is existing
        victim = game.find_player_by_name(command.player_name)
        if victim is None or victim.is_dead:
            return f"{command.player_name} was not found in the list of alive players!"

        if isinstance(player.card, WerewolfCard):
            return await self.handle_werewolf_vote(game, player, victim)
        if isinstance(player.card, SeerCard):
            return self.handle_seer_vote(player, victim)
        return "Only alive Werewolves are allowed to vote a victim!"


    async def handle_werewolf_vote(self, game :GameContext, player :Player, victim :Player) ->str:
        """Handles the Werewolves vote process"""
        player.night_vote = victim

        # Check if the vote is already ended
        votes = ""
        vote_valid = True
        for _, player in game.players.items():
            if isinstance(player.card, WerewolfCard):
                if not player.night_vote is None:
                    votes += player.night_vote.name + " "
                    if player.night_vote != victim:
                        vote_valid = False
        if not vote_valid:
            return (
                "All Werewolves must agree on one victim.\n"
                f"Current votes are {votes}\n"
                "Vote is not finished yet.\n"
                "Use !vote command to update your decision."
            )

        # We found a victim
        result = f"{victim.name} is killed by the Werewolves!\n"
        result += f"{victim.name} was a {victim.card.name}."
        victim.is_dead = True

        # Check if the game is over
        nr_werewolves, nr_villagers = game.check_gameover()
        if nr_werewolves == 0:
            result += "\nGAME OVER - the villagers won!"
        if nr_villagers == 0:
            result += "\nGAME OVER - the werewolves won!"
        await game.channel.send(result)

        if nr_werewolves == 0 or nr_villagers == 0:
            await game.change_state( ReadyState() )
        else:
            await game.change_state( DayState() )

        return result


    def handle_seer_vote(self, player :Player, victim :Player) ->str:
        """Handles the seer asking if a player is a werewolf."""
        if player.seer_asked_werewolf:
            return "You are not allowed to ask twice within one night!"
        player.seer_asked_werewolf = True
        if isinstance(victim.card, WerewolfCard):
            return f"{victim.name} is a Werewolf!"
        else:
            return f"{victim.name} is not a Werewolf!"


    async def on_enter(self, game: GameContext, prev_state) ->None:
        for _, player in game.players.items():
            player.night_vote = None
            player.seer_asked_werewolf = False
        await game.channel.send(
            "It's been a long day and now night is falling. "
            "The villagers are asleep and the werewolves are becoming active."
        )


class DayState(GameState):
    """The day-phase of a game-round"""
    async def handle_status(self, game :GameContext, command :StatusCommand) ->str:
        result = "It is day. All players seek for their next victim.\n"
        result += "Currently the following are still alive:\n"
        for player in game.players.values():
            if not player.is_dead:
                result += f"- **{player.name}**\n"
        result += "Use the !vote command."
        return result

    async def handle_vote(self, game :GameContext, command :VoteCommand) ->str:
        # Check if player is alive
        player = game.players[command.author]
        if player.is_dead:
            return "Only alive players are allowed to vote a victim!"
        # Check if the victim is existing
        victim = game.find_player_by_name(command.player_name)
        if victim is None or victim.is_dead:
            return f"{command.player_name} was not found in the list of alive players!"
        player.day_vote = victim

        # Check if the vote is already ended
        votes = ""
        nr_players = game.get_alive_players_count()
        players_voted : dict[Player, int] = {}
        for _, player in game.players.items():
            players_voted[player] = 0
        for _, player in game.players.items():
            if not player.day_vote is None:
                players_voted[player.day_vote] = players_voted[player.day_vote]+1
                votes += player.day_vote.name + " "
        victim = None
        for player, v in players_voted.items():
            if v*2 > nr_players:
                victim = player

        if victim is None:
            return (
                f"Current votes are {votes}\n"
                "Vote is not finished, because the victim must count at least half of the votes.\n"
                "Use !vote command to update your decision."
            )

        # We found a victim
        result = f"{victim.name} is killed by the villagers!\n"
        result += f"{victim.name} was a {victim.card.name}."
        victim.is_dead = True

        # Check if the game is over
        nr_werewolves, nr_villagers = game.check_gameover()
        if nr_werewolves == 0:
            result += "\nGAME OVER - the villagers won!"
        if nr_villagers == 0:
            result += "\nGAME OVER - the werewolves won!"
        await game.channel.send(result)

        if nr_werewolves == 0 or nr_villagers == 0:
            await game.change_state( ReadyState() )
        else:
            await game.change_state( NightState() )

        return ""


    async def on_enter(self, game: GameContext, prev_state) ->None:
        for _, player in game.players.items():
            player.day_vote = None
        await game.channel.send(
            "It was a long night and the werewolves roamed the streets of the city. "
            "Wake up, everyone, and wait for the things to come."
        )
