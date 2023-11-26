"""
State-Machine implementing the various states in the game play
"""
import random
import logging
from discord import Guild, TextChannel

from logic.command import GameCommand
from logic.command import StatusCommand, JoinCommand, QuitCommand, StartCommand, VoteCommand
from model.player import Player, HumanPlayer, AIAgentPlayer
from model.card import create_cards, WerewolfCard, SeerCard


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)


class GameContext:
    """The game that holds the state"""
    def __init__(self, guild: Guild, channel :TextChannel) ->None:
        self.guild = guild
        self.channel = channel
        self.werewolves_channel : TextChannel = None
        self.name = channel.name
        self.__state__ = ReadyState()
        self.players: dict[str, Player] = {}

    async def handle(self, command :GameCommand) ->None:
        """Handle the provided command, returns a text message to be displaye in the channel"""
        await self.__state__.handle(self, command)

    async def change_state(self, next_state) ->None:
        """Change the state, will automatically call on_leave/on_enter"""
        prev_state = self.__state__
        if not prev_state is None:
            await prev_state.on_leave( self, next_state )
        self.__state__ = next_state
        await self.__state__.on_enter( self, prev_state )


    async def send_msg(self, msg :str) ->None:
        """Sends a message in the channel of the game"""
        await self.channel.send( msg )

    async def send_werewolves(self, msg :str) ->None:
        """Sends a message int the secret channel of the werewolves"""
        if not self.werewolves_channel is None:
            await self.werewolves_channel.send(msg)
        else:
            logger.error("No werewolves channel exist! Send '%s' failed!", msg)


    def find_player_by_name(self, player_name: str) ->Player:
        """Finds the player by player_name"""
        for player in self.players.values():
            if player.name == player_name:
                return player
        return None

    def get_alive_players_count(self) ->int:
        """Counts the number of alive players"""
        nr_alive = 0
        for player in self.players.values():
            if not player.is_dead:
                nr_alive += 1
        return nr_alive


    def check_gameover(self) ->(int, int):
        """Counts the alive werewolves and villagers to check if the game is over."""
        nr_werewolves = 0
        nr_villagers = 0
        for player in self.players.values():
            if not player.is_dead:
                if isinstance(player.card, WerewolfCard):
                    nr_werewolves += 1
                else:
                    nr_villagers += 1
        return nr_werewolves, nr_villagers


class GameState:
    """Base state class"""

    async def handle(self, game :GameContext, command :GameCommand) ->None:
        """Forwards the command to the corresponding command-handler"""
        if isinstance(command, StatusCommand):
            await self.handle_status(game, command)
        elif isinstance(command, JoinCommand):
            await self.handle_join(game, command)
        elif isinstance(command, QuitCommand):
            await self.handle_quit(game, command)
        elif isinstance(command, StartCommand):
            await self.handle_start(game, command)
        elif isinstance(command, VoteCommand):
            await self.handle_vote(game, command)
        else:
            raise NotImplementedError


    async def handle_status(self, game :GameContext, command :StatusCommand) ->None:
        """Implementation of the Status command"""
        await self.send_cmd_not_supported(game, command)

    async def handle_join(self, game: GameContext, command :JoinCommand) ->None:
        """Implementation of the Join command"""
        await self.send_cmd_not_supported(game, command)

    async def handle_quit(self, game: GameContext, command :QuitCommand) ->None:
        """Implementation of the Quit command"""
        await self.send_cmd_not_supported(game, command)

    async def handle_start(self, game: GameContext, command: StartCommand) ->None:
        """Implementation of the Start command"""
        await self.send_cmd_not_supported(game, command)

    async def handle_vote(self, game: GameContext, command: StartCommand) ->None:
        """Implementation of the Vote command"""
        await self.send_cmd_not_supported(game, command)


    async def send_cmd_not_supported(self, game :GameContext, cmd) ->None:
        """Sends a command not supported message"""
        await game.send_msg( f"Command {cmd.name} not supported here (in {game.name})!")


    async def on_enter(self, game: GameContext, prev_state) ->None:
        """Called before the state is activated"""

    async def on_leave(self, game: GameContext, next_state) ->None:
        """Called after the state is deactivated"""


    async def handle_game_over(self, game :GameContext) ->bool:
        """Check if the game is over, if yes --> handle it"""
        nr_werewolves, nr_villagers = game.check_gameover()
        if nr_werewolves == 0:
            await game.send_msg("GAME OVER - the villagers won!")
        if nr_villagers == 0:
            await game.send_msg("GAME OVER - the werewolves won!")

        if nr_werewolves == 0 or nr_villagers == 0:
            await game.change_state( ReadyState() )
            return True
        return False    # game continues



class ReadyState(GameState):
    """In the ReadyState the members may join themselves to the players list"""

    async def handle_status(self, game: GameContext, command :StatusCommand) ->None:
        result = "No game is running yet, you are in the join-to-play phase.\n"
        result += "Currently the following members have registered to play:\n"
        for player in game.players.values():
            result += f"- **{player.name}**\n"
        result += "\nNext steps:\n"
        result += "- **!join** to join the game.\n"
        result += "- **!quit** to leave the game.\n"
        result += "- **!start** to start the game (needs at least 6 players!)"
        await game.send_msg( result )

    async def handle_join(self, game: GameContext, command :JoinCommand) ->None:
        # Add an human player
        logger.info("%s joins the game %s", command.author, game.name)
        game.players[command.get_player_name()] = HumanPlayer(command.author)
        await game.send_msg( f"{command.get_player_name()} joined the game." )

    async def handle_quit(self, game: GameContext, command :QuitCommand) ->None:
        logger.info("%s quits the game %s", command.author, game.name)
        if command.author.display_name in game.players:
            del game.players[command.author.display_name]
        await game.send_msg( f"{command.author.display_name} quits the game." )

    async def handle_start(self, game: GameContext, command: StartCommand) ->None:
        if len(game.players)<3:  # TODO - set this check to 6 when released
            await game.send_msg( "Cannot start game. "
                                "At least six player must join the game via !join command." )
            return

        # Shuffle and assign cards
        cards = create_cards(len(game.players))
        result = "Game started\nThe following cards are in the game:\n"
        for card in cards:
            result += f"- **{card.name}**: {card.desc}\n"
        result += "See your direct-messages from me, to get to know your own card "
        result += "and further instructions."
        logger.info(result)
        await game.send_msg( result )

        random.shuffle(cards)
        for player in game.players.values():
            card = cards.pop()
            logger.info( "%s gets card %s", player.name, card )
            player.card = card
            await player.send_dm(
                f"You got the card **{card.name}** in game **{game.name}**.\n"
                f"{card.desc}")

        # Tell all the Werewolves who they are
        werewolves = []
        for player in game.players.values():
            if isinstance(player.card, WerewolfCard):
                werewolves.append(player)
        if game.werewolves_channel is None:
            game.werewolves_channel = await game.guild.create_text_channel(
                "WerewolvesOnly_" + game.channel.name
            )
        werewolves_str = "The werewolves team is:\n"
        for werewolf in werewolves:
            werewolves_str += f"- **{werewolf.name}**\n"
        logger.info(werewolves_str)
        for player in werewolves:
            await player.send_dm( werewolves_str +
                (f"The werewolves team is {werewolves_str},\n"
                f" secretly talk to them in {game.werewolves_channel.name}!\n"
                "You need to vote for a villager to be eaten.\n"
                "Tell me your decision using the **!vote** command.")
            )
        await game.send_werewolves(
            f"This is the channel for Werewolves in {game.name} only - **PLEASE DON't CHEAT!**\n")
        await game.send_werewolves(
            werewolves_str +
            "You need to vote for a villager to be your next victim."
        )

        await game.change_state( NightState() )


    async def on_enter(self, game: GameContext, prev_state) ->None:
        await game.send_msg("This GAME is over!\n\n")
        while len(game.players)>0:
            _, player = game.players.popitem()
            if isinstance(player, AIAgentPlayer ):
                player.stop()
            del player
        if not game.werewolves_channel is None:
            await game.werewolves_channel.delete()
            game.werewolves_channel = None
        await self.handle_status(game, StatusCommand(None, None))



class NightState(GameState):
    """The night-phase of a game-round"""
    async def handle_status(self, game :GameContext, command :StatusCommand) ->None:
        if command.channel==game.werewolves_channel:
            await self.check_current_votes(game, None)
        else:
            result = "It is night. The Werewolves seek for their next victim.\n"
            result += "Currently the following players are still alive:\n"
            for player in game.players.values():
                if not player.is_dead:
                    result += f"- **{player.name}**\n"
            result += "\nNext steps:\n"
            result += "- **!vote** (for Werewolves only) use this command to select their victim.\n"
            result += "- **!quit** to leave the game through suicide.\n"
            await game.send_msg( result )

    async def handle_quit(self, game: GameContext, command :QuitCommand) ->None:
        logger.info("%s quits the game %s through suicide.", command.author, game.name)
        if command.author.display_name in game.players:
            del game.players[command.author.display_name]
        await game.send_msg( f"{command.author.display_name} quits the game through suicide." )
        await self.handle_game_over(game)

    async def handle_vote(self, game :GameContext, command :VoteCommand) ->None:
        # Check if the player is allowed to vote
        player = game.players[command.voter_name]
        if player.is_dead:
            await game.send_msg( "Only alive players are allowed to vote!" )
            return
        # Check if the victim is existing
        victim = game.find_player_by_name(command.player_name)
        if victim is None or victim.is_dead:
            await game.send_msg(
                f"{command.player_name} was not found in the list of alive players!" )
            return

        if isinstance(player.card, WerewolfCard):
            await self.handle_werewolf_vote(game, player, victim)
        elif isinstance(player.card, SeerCard):
            await self.handle_seer_vote(player, victim)
        else:
            await game.send_msg( "Only alive Werewolves are allowed to vote a victim!" )


    async def handle_werewolf_vote(self, game :GameContext, player :Player, victim :Player) ->None:
        """Handles the Werewolves vote process"""
        player.night_vote = victim

        # Check if the vote is already ended
        if not await self.check_current_votes(game, victim):
            return

        # We found a victim
        result = f"{victim.name} is killed by the Werewolves!\n"
        result += f"{victim.name} was a {victim.card.name}."
        victim.is_dead = True
        await game.send_msg(result)

        if not await self.handle_game_over(game):
            await game.change_state( DayState() )

    async def check_current_votes(self, game :GameContext, victim :Player) ->bool:
        """Show and check if the vote is already ended"""
        votes = "The current votes are:\n"
        non_votes = "These players still need to vote:\n"
        vote_valid = True
        for plr in game.players.values():
            if not plr.is_dead and isinstance(plr.card, WerewolfCard):
                if not plr.night_vote is None:
                    votes += f"- {plr.name} votes for {plr.night_vote.name}\n"
                    if plr.night_vote != victim:
                        vote_valid = False
                else:
                    non_votes += f"- {plr.name}\n"
        if not vote_valid:
            await game.send_werewolves(
                "All Werewolves must agree on one victim.\n"
                + votes +
                "Vote is not finished yet.\n"
                + non_votes +
                "Use **!vote** command to update your decision."
            )
        return vote_valid


    async def handle_seer_vote(self, player :Player, victim :Player) ->None:
        """Handles the seer asking if a player is a werewolf."""
        if player.seer_asked_werewolf:
            await player.send_dm( "You are not allowed to ask twice within one night!" )
        player.seer_asked_werewolf = True
        if isinstance(victim.card, WerewolfCard):
            await player.send_dm( f"{victim.name} is a Werewolf!" )
        else:
            await player.send_dm( f"{victim.name} is not a Werewolf!" )


    async def on_enter(self, game: GameContext, prev_state) ->None:
        for player in game.players.values():
            player.night_vote = None
            player.seer_asked_werewolf = False
        await game.send_msg(
            "It's been a long day and now night is falling. "
            "The villagers are asleep and the werewolves are becoming active."
        )


class DayState(GameState):
    """The day-phase of a game-round"""
    async def handle_status(self, game :GameContext, command :StatusCommand) ->None:
        if command.channel==game.werewolves_channel:
            await self.check_current_votes(game)
        else:
            result = "It is day. All players seek for their next victim.\n"
            result += "Currently the following players are still alive:\n"
            for player in game.players.values():
                if not player.is_dead:
                    result += f"- **{player.name}**\n"
            result += "\nNext steps:\n"
            result += "- **!vote** command to select the next victim.\n"
            result += "- **!quit** to leave the game through suicide.\n"
            await game.send_msg( result )


    async def handle_quit(self, game: GameContext, command :QuitCommand) ->None:
        logger.info("%s quits the game %s through suicied", command.author, game.name)
        if command.author.display_name in game.players:
            del game.players[command.author.display_name]
        await game.send_msg( f"{command.author.display_name} quits the game through suicide." )
        await self.handle_game_over(game)


    async def handle_vote(self, game :GameContext, command :VoteCommand) ->None:
        # Check if player is alive
        player = game.players[command.voter_name]
        if player.is_dead:
            return "Only alive players are allowed to vote a victim!"
        # Check if the victim is existing
        victim = game.find_player_by_name(command.player_name)
        if victim is None or victim.is_dead:
            return f"{command.player_name} was not found in the list of alive players!"
        player.day_vote = victim

        victim = await self.check_current_votes(game)
        if victim is None:
            return

        # We found a victim
        result = f"{victim.name} is killed by the villagers!\n"
        result += f"{victim.name} was a {victim.card.name}."
        victim.is_dead = True
        await game.send_msg(result)

        if not await self.handle_game_over(game):
            await game.change_state( NightState() )

    async def check_current_votes(self, game :GameContext) ->Player:
        """Check if the vote is already ended"""
        votes = "The current votes are:\n"
        non_votes = "These players still need to vote:\n"
        nr_players = game.get_alive_players_count()
        players_voted : dict[Player, int] = {}
        for player in game.players.values():
            players_voted[player] = 0
        for player in game.players.values():
            if not player.is_dead:
                if not player.day_vote is None:
                    players_voted[player.day_vote] = players_voted[player.day_vote]+1
                    votes += f"- {player.name} votes for {player.day_vote.name}\n"
                else:
                    non_votes += f"- {player.name}\n"
        victim = None
        for player, v in players_voted.items():
            if v*2 > nr_players:
                victim = player

        if victim is None:
            await game.send_msg(
                votes +
                "Vote is not finished, because the victim must count at least half of the votes.\n"
                + non_votes +
                "Use **!vote** command to update your decision."
            )
        return victim


    async def on_enter(self, game: GameContext, prev_state) ->None:
        for player in game.players.values():
            player.day_vote = None
        await game.send_msg(
            "It was a long night and the werewolves roamed the streets of the city. "
            "Wake up, everyone, and wait for the things to come."
        )
