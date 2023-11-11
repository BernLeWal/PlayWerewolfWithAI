""" command.py
Module providing classes to handle commands.
The command is created in the caller, but executed in the states.
"""
from discord import Member

class GameCommand:
    """Base command class"""
    def __init__(self, author :Member) ->None:
        self.author = author



class StatusCommand(GameCommand):
    """Handles !status command"""
    def __init__(self, author :Member) -> None:
        super().__init__(author)


class JoinCommand(GameCommand):
    """Handles !join command"""
    def __init__(self, author :Member) -> None:
        super().__init__(author)


class QuitCommand(GameCommand):
    """Handles !quit command (in the game)"""
    def __init__(self, author :Member) ->None:
        super().__init__(author)


class StartCommand(GameCommand):
    """Handles !start command"""
    def __init__(self, author :Member) ->None:
        super().__init__(author)
