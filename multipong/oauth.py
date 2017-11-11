from flask import jsonify, session, url_for, redirect
from multipong import app, google, twitter, users
from multipong.models import User


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('google_token', None)
    session.pop('twitter_oauth', None)
    return redirect(url_for('index'))


@app.route('/auth/google')
def google_auth():
    return google.authorize(callback=url_for('google_callback',
                                             _external=True))


@app.route('/auth/twitter')
def twitter_auth():
    return twitter.authorize(callback=url_for('twitter_callback',
                                              _external=True))


@app.route("/callback/google")
def google_callback():
    resp = google.authorized_response()
    session['google_token'] = (resp['access_token'], '')
    id = google.get('userinfo').data['id']
    store_oauth_user(id, 'google')
    return jsonify(dict(session.get('user')))


@app.route('/callback/twitter')
def twitter_callback():
    resp = twitter.authorized_response()
    store_oauth_user(resp['user_id'], 'twitter')
    return jsonify(dict(session.get('user')))


@app.route('/getone')
def get_one():
    '''Endpoint to ensure that the current user is stored in db'''
    current = users.find_one(dict(session['user'].key()))
    return str(current)


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']


def store_oauth_user(oauth: str, provider: str) -> User:
    user = User(oauth, provider)
    user.update_db(users)
    session['user'] = user
    return user
