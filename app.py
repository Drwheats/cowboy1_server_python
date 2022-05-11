from requests import Session
from flask import Flask, url_for, redirect, session
from flask_socketio import SocketIO, send
from flask_cors import CORS, cross_origin
from json_functions import write_json
from authlib.integrations.flask_client import OAuth
from datetime import timedelta
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app, support_credentials=True)

#oauth config
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id="1001583536419-cu87kebe4epqmvfq0lhe7q34o5tdhnjt.apps.googleusercontent.com",
    client_secret="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",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs'
)


@app.route('/letmein')
def letmein():
    email = dict(session).get('email', None)
    return f'Hello {email}'


@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')  # create the google oauth client
    print(google)
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    # user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    session['email'] = user_info['email']
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
    return redirect('/letmein')


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


@socketio.on('send-message')
@app.route("/")
def request_messages(data):

    bad_words = []
    # print(f'data in : {data}')
    data_to_parse = data.lower()
    f = open('no-no-words.txt', "r")
    open_file = f.readlines()
    for line in open_file:
        bad_words.append(line.strip())
    if len(data_to_parse) > 257:
        data = 'error 1'
    for line in bad_words:
        if line in data_to_parse:
            data = 'error 2'

    email = dict(session).get('email', None)
    json_data = {"postID": 0, "number posts by this account": 0, "account name": email, "postContents": data}
    write_json(json_data)
    return json_data


if __name__ == '__main__':
    socketio.run(app)
