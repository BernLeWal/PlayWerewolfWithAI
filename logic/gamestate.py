class GameState:
    """Base state class"""
    def handle(self, context, command, author):
        raise NotImplementedError


class ReadyState(GameState):
    def handle(self, context, command, author):
        if command=='status':
            players = '\n - '.join([str(player) for player in context.players.keys()])
            msg = "Run !start commant to start the game."
            if len(context.players.keys()) < 6:
                msg = f"You need {6-len(context.players.keys())} more players to join the game."
            return f"The following players joined the game:\n - {players}\n{msg}"
        elif command=='join':
            context.players[author] = author
            return f"{author} joined the game."
        elif command=='start':
            if len(context.players.keys())<6:
                return "Cannot start game. At least six player must join the game via !join command."
            context.state = StartingState()
            return "Game started"
        else:
            return "Command not supported in ready state!"


class StartingState(GameState):
    def handle(self, context, command, author):
        if command=='status':
            return "Game is starting. Get ready!"
        else:
            return "Command not supported in starting state!"



class DayState(GameState):
    def handle(self, context, command, author):
        return  "It's daytime. Players, start your activities!"


class NightState(GameState):
    def handle(self, context, command, author):
        return "Night has fallen. Dangerous creatures emerge."


class EndState(GameState):
    def handle(self, context, command, author):
        return "The game has ended. Calculating scores and showing results."



class GameContext:    
    """The context that holds the state"""
    def __init__(self, channel):
        self.state = ReadyState()
        self.channel = channel
        self.players = {}

    def request(self, command, author):
        return self.state.handle(self, command, author)



# Usage
if __name__ == "__main__":
    # Initial state is Ready
    game = GameContext(None)

    # The game goes through its states
    print(game.request('status', None))  # Ready
    print(game.request('start', None))    # Ready --> Starting

    print(game.request(None, None))  # Starting

    print(game.request(None, None))  # Day

    print(game.request(None, None))  # Night

    print(game.request(None, None))  # End

    print(game.request(None, None))  # Ready again (looped back)
