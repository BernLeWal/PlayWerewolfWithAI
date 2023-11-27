"""
State-Machine implementing the various states in the game play
"""
import logging

from logic.context import Context
from logic.state import State
from logic.readystate import ReadyState
from logic.nightstate import NightState
from logic.daystate import DayState
from model.command import GameCommand
from model.player import Player
from model.card import WerewolfCard, SeerCard


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)


class GameContext(Context):
    """The game that holds the state"""
    def __init__(self, name :str) ->None:
        super().__init__(name)
        self.players: dict[str, Player] = {}
        self.__state__ :State = ReadyState()


    ##### State-Handling
    async def handle(self, command :GameCommand) ->None:
        """Handle the provided command, returns a text message to be displaye in the channel"""
        await self.__state__.handle(self, command)


    async def __change_state__(self, next_state) ->None:
        """Change the state, will automatically call on_leave/on_enter"""
        prev_state = self.__state__
        if not prev_state is None:
            await prev_state.on_leave( self, next_state )
        self.__state__ = next_state
        await self.__state__.on_enter( self, prev_state )


    async def switch_to_readystate(self):
        """Next state is ReadyState"""
        await self.__change_state__( ReadyState() )


    async def switch_to_nightstate(self):
        """Next state is NightState"""
        await self.__change_state__( NightState() )


    async def switch_to_daystate(self):
        """Next state is DayState"""
        await self.__change_state__( DayState() )


    ##### Override UI functions
    async def send_msg(self, msg :str) ->None:
        """Sends a message in the channel of the game"""        


    async def handle_game_over(self) ->bool:
        """Check if the game is over, if yes --> handle it"""
        nr_werewolves, nr_villagers = self.check_gameover()
        if nr_werewolves == 0:
            await self.send_msg("GAME OVER - the villagers won!")
        if nr_villagers == 0:
            await self.send_msg("GAME OVER - the werewolves won!")

        if nr_werewolves == 0 or nr_villagers == 0:
            await self.switch_to_readystate()
            return True
        return False    # game continues


    def is_werewolf_vote_needed(self, player: Player):
        """Checks if the werewolf-player needs to vote"""
        if not isinstance(player.card, WerewolfCard):
            return False
        if isinstance(self.__state__, NightState) and player.night_vote is None:
            return True
        return False


    def is_villager_vote_needed(self, player: Player):
        """Checks if the player needs to vote"""
        if isinstance(self.__state__, DayState) and player.day_vote is None:
            return True
        return False


    def is_seer_vote_needed(self, player: Player):
        """Checks is the seer needs to ask if a player is a werewolf"""
        if not isinstance(player.card, SeerCard):
            return False
        if isinstance(self.__state__, NightState) and not player.seer_asked_werewolf:
            return True
        return False
