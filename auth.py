import os
import json
import time
import requests
from fitbit import Fitbit
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError

# Replace these with your own client ID and secret
CLIENT_ID = os.environ.get('FITBIT_CLIENT_ID')
CLIENT_SECRET = os.environ.get('FITBIT_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8080/'  # Set this in your Fitbit app settings

# Token storage file
TOKEN_FILE = 'data/fitbit_token.json'

# Fitbit OAuth 2.0 URLs
AUTHORIZATION_BASE_URL = 'https://www.fitbit.com/oauth2/authorize'
TOKEN_URL = 'https://api.fitbit.com/oauth2/token'


def save_token(token):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token, f)

def load_token():
    with open(TOKEN_FILE, 'r') as f:
        return json.load(f)

def authenticate():
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Disable the HTTPS requirement for local testing

    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=['activity', 'heartrate', 'nutrition', 'profile', 'settings', 'sleep', 'weight'])
    authorization_url, state = oauth.authorization_url(AUTHORIZATION_BASE_URL)
    
    print('Please go to {} and authorize access.'.format(authorization_url))
    authorization_response = input('Enter the full callback URL: ')

    token = oauth.fetch_token(TOKEN_URL, authorization_response=authorization_response,
                              client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    
    save_token(token)
    return token

def refresh_token(token):
    extra = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    oauth = OAuth2Session(client_id=CLIENT_ID, token=token)
    new_token = oauth.refresh_token(TOKEN_URL, **extra)
    save_token(new_token)
    return new_token

def get_fitbit_client():
    try:
        token = load_token()
    except FileNotFoundError:
        token = authenticate()

    fitbit_client = Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=token['access_token'], 
                           refresh_token=token['refresh_token'], expires_at=token['expires_at'], refresh_cb=refresh_token)
    return fitbit_client

def main():
    fitbit_client = get_fitbit_client()

    while True:
        try:
            profile = fitbit_client.user_profile_get()
            print(profile)
        except TokenExpiredError:
            print('Token expired, refreshing...')
            token = refresh_token(load_token())
            fitbit_client = Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=token['access_token'], 
                                   refresh_token=token['refresh_token'], expires_at=token['expires_at'], refresh_cb=refresh_token)
        except Exception as e:
            print('An error occurred: ', e)
        
        time.sleep(3600)  # Fetch data every hour

if __name__ == "__main__":
    main()