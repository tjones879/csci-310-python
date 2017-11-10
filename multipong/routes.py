from flask import render_template, jsonify
from multipong import app, users
from multipong.models import User
from multipong.mongo import get_user


@app.route('/')
def index():
    test = User("111", "111")
    test.update_db(users)
    return str(get_user(users, dict(test.key())))
    return render_template("index.html")
