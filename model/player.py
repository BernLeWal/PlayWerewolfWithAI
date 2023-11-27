"""
Representing a player in a Werewolve game
"""
import logging

from model.card import Card


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)



class Player:
    """Representing a player"""
    def __init__(self, name :str) ->None:
        self.name = name
        self.card : Card = None
        self.night_vote : Player = None
        self.day_vote : Player = None
        self.seer_asked_werewolf = False
        self.is_dead = False


    def reset(self) ->None:
        """Resets the players values"""
        self.card : Card = None
        self.is_dead = False
        self.clear_votes()


    def clear_votes(self) ->None:
        """Clear the votes (prior to the next round)"""
        self.night_vote : Player = None
        self.day_vote : Player = None
        self.seer_asked_werewolf = False


    async def send_dm(self, msg :str) ->None:
        """Sends a direct message to the player"""
