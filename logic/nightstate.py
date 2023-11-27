"""
The NightState implementation for the State-Machine in the game play
"""
import logging

from logic.context import Context
from logic.gamestate import GameState
from model.command import StatusCommand, VoteCommand
from model.player import Player
from model.card import WerewolfCard, SeerCard


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)


class NightState(GameState):
    """The night-phase of a game-round"""
    async def handle_status(self, game :Context, command :StatusCommand) ->None:
        if command.channel==game.werewolves_channel:
            await self.check_current_votes(game, None)
        else:
            result = "It is night. The Werewolves seek for their next victim.\n"
            result += game.get_alive_players_msg()
            await game.send_msg( result )

    async def handle_vote(self, game :Context, command :VoteCommand) ->None:
        (player, victim) = await self.check_vote_valid(game, command)
        if player is None or victim is None:
            return

        if isinstance(player.card, WerewolfCard):
            await self.handle_werewolf_vote(game, player, victim)
        elif isinstance(player.card, SeerCard):
            await self.handle_seer_vote(player, victim)
        else:
            await game.send_msg( "Only alive Werewolves are allowed to vote a victim!" )


    async def handle_werewolf_vote(self, game :Context, player :Player, victim :Player) ->None:
        """Handles the Werewolves vote process"""
        player.night_vote = victim

        # Check if the vote is already ended
        if not await self.check_current_votes(game, victim):
            return

        # We found a victim
        result = f"{victim.name} is killed by the Werewolves!\n"
        result += f"{victim.name} was a {victim.card.name}."
        victim.is_dead = True
        await game.send_msg(result)

        if not await game.handle_game_over():
            await game.switch_to_daystate()

    async def check_current_votes(self, game :Context, victim :Player) ->bool:
        """Show and check if the vote is already ended"""
        votes = "The current votes are:\n"
        non_votes = "These players still need to vote:\n"
        vote_valid = True
        for plr in game.players.values():
            if not plr.is_dead and isinstance(plr.card, WerewolfCard):
                if not plr.night_vote is None:
                    votes += f"- {plr.name} votes for {plr.night_vote.name}\n"
                    if plr.night_vote != victim:
                        vote_valid = False
                else:
                    non_votes += f"- {plr.name}\n"
        if not vote_valid:
            await game.send_werewolves(
                "All Werewolves must agree on one victim.\n"
                + votes +
                "Vote is not finished yet.\n"
                + non_votes +
                "Use **!vote** command to update your decision."
            )
        return vote_valid


    async def handle_seer_vote(self, player :Player, victim :Player) ->None:
        """Handles the seer asking if a player is a werewolf."""
        if player.seer_asked_werewolf:
            await player.send_dm( "You are not allowed to ask twice within one night!" )
        player.seer_asked_werewolf = True
        if isinstance(victim.card, WerewolfCard):
            await player.send_dm( f"{victim.name} is a Werewolf!" )
        else:
            await player.send_dm( f"{victim.name} is not a Werewolf!" )


    async def on_enter(self, game: Context, prev_state) ->None:
        for player in game.players.values():
            player.clear_votes()
        await game.send_msg(
            "It's been a long day and now night is falling. "
            "The villagers are asleep and the werewolves are becoming active."
        )
