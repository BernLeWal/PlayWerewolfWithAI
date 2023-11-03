from flask.views import MethodView
from flask import render_template, request, redirect, url_for, session

class NewGameView(MethodView):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app

    def get(self):
        return render_template('newgame.html')

    def post(self):
        player_name = request.form['player_name']
        game_name = request.form['game_name']

        if player_name!="" and game_name!="":
            print(f"Player {player_name} creates game {game_name}.")

            session['PLAYER_NAME'] = player_name
            session['NEW_GAME_NAME'] = game_name

            return redirect(url_for('games'))

        return "Not implemented yet", 500
