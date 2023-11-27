""" command.py
Module providing classes to handle commands.
The command is created in the caller, but executed in the states.
"""
import dataclasses
from discord import Member, TextChannel

@dataclasses.dataclass
class GameCommand:
    """Base command class"""
    def __init__(self, name: str, author :Member) ->None:
        self.name = name
        self.author = author


@dataclasses.dataclass
class StatusCommand(GameCommand):
    """Handles !status command"""
    def __init__(self, author :Member, channel :TextChannel) -> None:
        super().__init__("status", author)
        self.channel = channel


@dataclasses.dataclass
class JoinCommand(GameCommand):
    """Handles !join command"""
    def __init__(self, author :Member, ai_player_name :str = "") -> None:
        super().__init__("join", author)
        self.ai_player_name = ai_player_name

    def get_player_name(self):
        """Returns the name of the human-player or the ai-agent player"""
        if not self.author is None:
            return self.author.display_name
        return self.ai_player_name


@dataclasses.dataclass
class QuitCommand(GameCommand):
    """Handles !quit command (in the game)"""
    def __init__(self, author :Member) ->None:
        super().__init__("quit", author)


@dataclasses.dataclass
class StartCommand(GameCommand):
    """Handles !start command"""
    def __init__(self, author :Member) ->None:
        super().__init__("start", author)


@dataclasses.dataclass
class VoteCommand(GameCommand):
    """Handles !vote command"""
    def __init__(self, author :Member, voter_name :str, player_name :str) ->None:
        super().__init__("vote", author)
        self.voter_name = voter_name
        self.player_name = player_name
        