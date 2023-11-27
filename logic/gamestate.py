"""
The Baseclass implementation for the State-Machine in the game play
"""
import logging

from model.command import GameCommand
from model.command import StatusCommand, JoinCommand, QuitCommand, StartCommand, VoteCommand


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)



class GameState:
    """Base state class"""

    async def handle(self, game, command :GameCommand) ->None:
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


    async def handle_status(self, game, command :StatusCommand) ->None:
        """Implementation of the Status command"""
        await self.send_cmd_not_supported(game, command)

    async def handle_join(self, game, command :JoinCommand) ->None:
        """Implementation of the Join command"""
        await self.send_cmd_not_supported(game, command)

    async def handle_quit(self, game, command :QuitCommand) ->None:
        """Implementation of the Quit command"""
        await self.send_cmd_not_supported(game, command)

    async def handle_start(self, game, command: StartCommand) ->None:
        """Implementation of the Start command"""
        await self.send_cmd_not_supported(game, command)

    async def handle_vote(self, game, command: StartCommand) ->None:
        """Implementation of the Vote command"""
        await self.send_cmd_not_supported(game, command)


    async def send_cmd_not_supported(self, game, cmd) ->None:
        """Sends a command not supported message"""
        await game.send_msg( f"Command {cmd.name} not supported here (in {game.name})!")


    async def on_enter(self, game, prev_state) ->None:
        """Called before the state is activated"""

    async def on_leave(self, game, next_state) ->None:
        """Called after the state is deactivated"""
