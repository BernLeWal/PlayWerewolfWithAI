"""
The Baseclass implementation for the State-Machine in the game play
"""
import logging

from model.command import QuitCommand, VoteCommand
from model.player import Player
from logic.context import Context
from logic.state import State


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)



class GameState(State):
    """Base state class"""


    async def send_cmd_not_supported(self, game, cmd) ->None:
        """Sends a command not supported message"""
        await game.send_msg( f"Command {cmd.name} not supported here (in {game.name})!")


    async def handle_quit(self, game :Context, command :QuitCommand) ->None:
        """Handles the quit command during a running game"""
        logger.info("%s quits the game %s through suicide.", command.author, game.name)
        if command.author.display_name in game.players:
            del game.players[command.author.display_name]
        await game.send_msg( f"{command.author.display_name} quits the game through suicide." )
        await game.handle_game_over()


    async def check_vote_valid(self, game :Context, command :VoteCommand) ->(Player, Player):
        """Checks if the vote-command is valid/allowed in the current game state"""
        # Check if the player is allowed to vote
        player = game.players[command.voter_name]
        if player.is_dead:
            await game.send_msg( "Only alive players are allowed to vote!" )
            return (None, None)
        # Check if the victim is existing
        victim = game.find_player_by_name(command.player_name)
        if victim is None or victim.is_dead:
            await game.send_msg(
                f"{command.player_name} was not found in the list of alive players!" )
            return (None, None)
        return (player, victim)
