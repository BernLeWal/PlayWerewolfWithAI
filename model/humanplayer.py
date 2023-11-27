"""
Representing a human-player in a Werewolve game
"""
import logging

from discord import Member

from model.player import Player



# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)


class HumanPlayer(Player):
    """Representing a human player"""
    def __init__(self, member :Member) ->None:
        super().__init__(member.display_name)
        self.member = member

    async def send_dm(self, msg :str) ->None:
        """Sends a direct message to the player"""
        logger.debug( "Send DM to %s", self.member)
        await self.member.create_dm()
        await self.member.dm_channel.send( msg )
        logger.debug( "Sending DM to %s done", self.member)
