#!/bin/python
from flask import Flask
from views.home_view import HomeView


# Logic to set up the application
app = Flask(__name__)


# Rules to connect the views
app.add_url_rule('/', view_func=HomeView.as_view('home'))

# Static files

# Application entry point
if __name__ == "__main__":
    app.run(debug=True)
