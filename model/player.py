"""
Representing a player in a Werewolve game
"""
from model.card import Card


class Player:
    """Representing a player"""
    def __init__(self, name :str):
        self.name = name
        self.card : Card = None
