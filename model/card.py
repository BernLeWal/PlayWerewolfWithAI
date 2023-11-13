"""
Representing the cards in the game
"""
import random

class Card:
    """Base class for all cards"""
    def __init__(self, name :str, character :int, night_order :int, desc :str):
        self.name = name
        self.character = character
        self.desc = desc
        self.night_order = night_order

    def __str__(self):
        return f"{self.name}({self.character})"


class WerewolfCard(Card):
    """Card representing the Werewolf role"""
    def __init__(self) -> None:
        super().__init__("Werewolf", -6, 10,
            "Choose a victim to devour each night together with the other werewolves.")


class VillagerCard(Card):
    """Card representing the Villager role"""
    def __init__(self) -> None:
        super().__init__("Villager", +1, 0,
            "Find the werewolves and lynch them.")


class SeerCard(Card):
    """Card representing the Seer role"""
    def __init__(self) -> None:
        super().__init__("Seer", +7, 1,
            "Choose a player every night and find out whether they are the werewolf or not.")


def create_cards( count :int):
    """Returns a set of cards"""
    result = []
    sum_character = 0
    if count > 4:
        result.append( SeerCard() )
        sum_character += 7
    while len(result) < count:
        card = None
        if sum_character <= 0:
            card = VillagerCard()
        else:
            card = WerewolfCard()
        result.append(card)
        sum_character += card.character
    return result


# Usage
if __name__ == "__main__":
    for nr in range(1,20):
        cards = create_cards(nr)
        CARDS_STR = ", ".join(str(card) for card in cards)
        print(f"{nr} cards:   {CARDS_STR}")
        random.shuffle(cards)
        CARDS_STR = ", ".join(str(card) for card in cards)
        print(f"{nr} shuffled:{CARDS_STR}")
