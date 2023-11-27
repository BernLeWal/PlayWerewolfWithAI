"""
The ReadyState implementation for the State-Machine in the game play
"""
import logging
import random

from logic.context import Context
from logic.gamestate import GameState
from model.command import StatusCommand, QuitCommand, JoinCommand, StartCommand
from model.humanplayer import HumanPlayer
from model.aiagentplayer import AIAgentPlayer
from model.card import create_cards, WerewolfCard


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)


class ReadyState(GameState):
    """In the ReadyState the members may join themselves to the players list"""

    async def handle_status(self, game: Context, command :StatusCommand) ->None:
        result = "No game is running yet, you are in the join-to-play phase.\n"
        result += "Currently the following members have registered to play:\n"
        for player in game.players.values():
            result += f"- **{player.name}**\n"
        result += "\nNext steps:\n"
        result += "- **!join** to join the game.\n"
        result += "- **!quit** to leave the game.\n"
        result += "- **!start** to start the game (needs at least 6 players!)"
        await game.send_msg( result )

    async def handle_join(self, game: Context, command :JoinCommand) ->None:
        # Add an human player
        logger.info("%s joins the game %s", command.author, game.name)
        game.players[command.get_player_name()] = HumanPlayer(command.author)
        await game.send_msg( f"{command.get_player_name()} joined the game." )

    async def handle_quit(self, game: Context, command :QuitCommand) ->None:
        logger.info("%s quits the game %s", command.author, game.name)
        if command.author.display_name in game.players:
            del game.players[command.author.display_name]
        await game.send_msg( f"{command.author.display_name} quits the game." )

    async def handle_start(self, game: Context, command: StartCommand) ->None:
        if len(game.players)<4:  # TODO - set this check to 6 when released
            await game.send_msg( "Cannot start game. "
                                "At least six player must join the game via !join command." )
            return

        # Shuffle and assign cards
        cards = create_cards(len(game.players))
        result = "Game started\nThe following cards are in the game:\n"
        for card in cards:
            result += f"- **{card.name}**: {card.desc}\n"
        result += "See your direct-messages from me, to get to know your own card "
        result += "and further instructions."
        logger.info(result)
        await game.send_msg( result )

        random.shuffle(cards)
        for player in game.players.values():
            card = cards.pop()
            logger.info( "%s gets card %s", player.name, card )
            player.card = card
            await player.send_dm(
                f"You got the card **{card.name}** in game **{game.name}**.\n"
                f"{card.desc}")

        # Tell all the Werewolves who they are
        werewolves = []
        for player in game.players.values():
            if isinstance(player.card, WerewolfCard):
                werewolves.append(player)
        if game.werewolves_channel is None:
            game.werewolves_channel = await game.guild.create_text_channel(
                "WerewolvesOnly_" + game.channel.name
            )
        werewolves_str = "The werewolves team is:\n"
        for werewolf in werewolves:
            werewolves_str += f"- **{werewolf.name}**\n"
        logger.info(werewolves_str)
        for player in werewolves:
            await player.send_dm( werewolves_str +
                (f"The werewolves team is {werewolves_str},\n"
                f" secretly talk to them in {game.werewolves_channel.name}!\n"
                "You need to vote for a villager to be eaten.\n"
                "Tell me your decision using the **!vote** command.")
            )
        await game.send_werewolves(
            f"This is the channel for Werewolves in {game.name} only - **PLEASE DON't CHEAT!**\n")
        await game.send_werewolves(
            werewolves_str +
            "You need to vote for a villager to be your next victim."
        )

        await game.switch_to_nightstate()


    async def on_enter(self, game: Context, prev_state) ->None:
        await game.send_msg("This GAME is over!\n\n")
        while len(game.players)>0:
            _, player = game.players.popitem()
            if isinstance(player, AIAgentPlayer ):
                player.stop()
            del player
        if not game.werewolves_channel is None:
            await game.werewolves_channel.delete()
            game.werewolves_channel = None
        await self.handle_status(game, StatusCommand(None, None))
