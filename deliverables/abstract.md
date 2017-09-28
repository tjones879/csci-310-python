Backend
-------
Python -> FLASK, FLASK-SOCKETIO

MONGODB -> Store players, scores, gamestate

Frontend
-------
Typescript or Javascript

HTML5 Canvas

Game Components
-------
Online 2D game

 -> Survival pong arena

 -> Massively multiplayer


## Abstract
Tyler Jones, Ernie Ripley, Andrew Whitehurst, Joel Cressy

Our final project is a massively multiplayer web version of Pong. Each game will
start with several players. When a player fails to return a ball, they are
successively eliminated, the pong arena shrinks, and eventually the last player
standing is crowned victor.

The server backend will utilize Flask as the web framework in addition to
flask-socketio to maintain web-socket connections with clients. The Python backend
will automatically create and destroy lobbies as players enter and leave games.
MongoDB will be our database engine used to store the state of each lobby, provide
the information necessary to maintain synchronization and correctness between
clients, and store persistent player data.

The game's frontend will utilize Javascript and HTML5 canvas to render 2D graphics
and provide user feedback during gameplay.
