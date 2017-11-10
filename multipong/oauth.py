from flask import jsonify, request, session, url_for, redirect
from multipong import app, google, twitter


@app.route('/logout')
def logout():
    session.pop('google_token', None)
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
    if resp is None:
        return 'Access denied: reson=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    # Figure out how to resolve different services
    return jsonify({"data": me.data})


@app.route('/callback/twitter')
def twitter_callback():
    resp = twitter.authorized_response()
    session['twitter_oauth'] = resp
    # Figure out how to resolve different services
    return jsonify({'user': resp['user_id']})


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']
