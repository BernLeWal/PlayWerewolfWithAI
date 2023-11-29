"""
The DayState implementation for the State-Machine in the game play
"""
import logging

from logic.context import Context
from logic.gamestate import GameState
from model.command import StatusCommand, VoteCommand
from model.player import Player


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)


class DayState(GameState):
    """The day-phase of a game-round"""
    async def handle_status(self, game :Context, command :StatusCommand) ->None:
        if command.channel==game.werewolves_channel:
            await self.check_current_votes(game)
        else:
            result = "It is day. All players seek for their next victim.\n"
            result += game.get_alive_players_msg()
            await game.send_msg( result )


    async def handle_vote(self, game :Context, command :VoteCommand) ->None:
        (player, victim) = await self.check_vote_valid(game, command)
        if player is None or victim is None:
            return
        player.day_vote = victim

        victim = await self.check_current_votes(game)
        if victim is None:
            return

        # We found a victim
        result = f"{victim.name} is killed by the villagers!\n"
        result += f"{victim.name} was a {victim.card.name}."
        victim.is_dead = True
        await game.send_msg(result)

        if not await game.handle_game_over():
            await game.switch_to_nightstate()

    async def check_current_votes(self, game :Context) ->Player:
        """Check if the vote is already ended"""
        votes = "The current votes are:\n"
        non_votes = "These players still need to vote:\n"
        nr_players = game.get_alive_players_count()
        players_voted : dict[Player, int] = {}
        for player in game.players.values():
            players_voted[player] = 0
        for player in game.players.values():
            if not player.is_dead:
                if not player.day_vote is None:
                    players_voted[player.day_vote] = players_voted[player.day_vote]+1
                    votes += f"- {player.name} votes for {player.day_vote.name}\n"
                else:
                    non_votes += f"- {player.name}\n"
        victim = None
        for player, v in players_voted.items():
            if v*2 > nr_players:
                victim = player

        if victim is None:
            await game.send_msg(
                votes +
                "Vote is not finished, because the victim must count at least half of the votes.\n"
                + non_votes +
                "Use **!vote** command to update your decision."
            )
        return victim


    async def on_enter(self, game: Context, prev_state) ->None:
        for player in game.players.values():
            player.clear_votes()
        await game.send_msg(
            "It was a long night and the werewolves roamed the streets of the city. "
            "Wake up, everyone, and wait for the things to come."
        )
