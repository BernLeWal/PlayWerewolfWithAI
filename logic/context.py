"""
Abstract State-Machine implementing the various states in the game play
"""
import logging

from model.command import GameCommand
from model.player import Player
from model.card import WerewolfCard


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)


class Context:
    """The game that holds the state"""
    def __init__(self, name :str) ->None:
        self.players: dict[str, Player] = {}
        self.name = name


    ##### Abstract State-Handling
    async def handle(self, command :GameCommand) ->None:
        """Handle the provided command"""


    async def switch_to_readystate(self):
        """Next state is ReadyState"""


    async def switch_to_nightstate(self):
        """Next state is NightState"""


    async def switch_to_daystate(self):
        """Next state is DayState"""


    ##### Game Logic Helpers
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



    ##### Abstract UI functions
    async def send_msg(self, msg :str) ->None:
        """Sends a message in the channel of the game"""        


    async def handle_game_over(self) ->bool:
        """Check if the game is over, if yes --> handle it"""


    def is_werewolf_vote_needed(self, player: Player):
        """Checks if the werewolf-player needs to vote"""


    def is_villager_vote_needed(self, player: Player):
        """Checks if the player needs to vote"""


    def is_seer_vote_needed(self, player: Player):
        """Checks is the seer needs to ask if a player is a werewolf"""
