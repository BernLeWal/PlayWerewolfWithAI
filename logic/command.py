""" command.py
Module providing classes to handle commands.
The command is created in the caller, but executed in the states.
"""
from discord import Member

class GameCommand:
    """Base command class"""
    def __init__(self, name: str, author :Member) ->None:
        self.name = name
        self.author = author


class StatusCommand(GameCommand):
    """Handles !status command"""
    def __init__(self, author :Member) -> None:
        super().__init__("status", author)


class JoinCommand(GameCommand):
    """Handles !join command"""
    def __init__(self, author :Member) -> None:
        super().__init__("join", author)


class QuitCommand(GameCommand):
    """Handles !quit command (in the game)"""
    def __init__(self, author :Member) ->None:
        super().__init__("quit", author)


class StartCommand(GameCommand):
    """Handles !start command"""
    def __init__(self, author :Member) ->None:
        super().__init__("start", author)


class VoteCommand(GameCommand):
    """Handles !vote command"""
    def __init__(self, author :Member, player_name :str) ->None:
        super().__init__("vote", author)
        self.player_name = player_name
        