#!/bin/python
import os
import secrets
from flask import Flask
from views.home_view import HomeView
from views.newgame_view import NewGameView


# Logic to set up the application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16)) 



# Rules to connect the views
app.add_url_rule('/', view_func=HomeView.as_view('home'))
app.add_url_rule('/newgame', view_func=NewGameView.as_view('newgame', app))

# Static files

# Application entry point
if __name__ == "__main__":
    app.run(debug=True)
