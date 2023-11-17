"""
Representing a player in a Werewolve game
"""
from model.card import Card


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
        self.night_vote : Player = None
        self.day_vote : Player = None
        self.seer_asked_werewolf = False
        self.is_dead = False
