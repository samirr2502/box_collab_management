import requests
from boxsdk import Client, OAuth2, BoxAPIException
from datetime import datetime, timedelta, timezone
from flask import session

CLIENT_ID = "020r4pyyewrt5si70y5mtvsg4g6kl3qq"
CLIENT_SECRET = "aInyr3WzN8XlOEyZYy8yptsD6siBHW5d"

EXPIRES_IN = 50*60

AUTH_CODE = ''
ACCESS_TOKEN = ''
REFRESH_TOKEN =''
DEV_TOKEN ='ST5Sr32IgJnUGnZcjbZApD5kZod6F9VW'
REDIRECT_URI = "http://127.0.0.1:5000"
token_url = "https://api.box.com/oauth2/token"
REFRESH_BUFFER = timedelta(minutes=5).total_seconds()

#print(f'authcode: {AUTH_CODE}\n')

def start_connection(access_token, refresh_token):
    REFRESH_TOKEN = refresh_token

    print("started box connection\n")
    #Create Connection 
    auth = OAuth2(client_id=None, client_secret=None, access_token=access_token)
    client = Client(auth)
    print(f'box connection made: {client}\n')
    return client


def get_access_token(code):
    AUTH_CODE = code
    #Uncomment the following line to use DEV_TOKEN
    #AUTH_CODE = DEV_TOKEN
    data_token = {
        "grant_type": "authorization_code",
        "code": AUTH_CODE,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(token_url, data=data_token)
    tokens = response.json()

    ACCESS_TOKEN = tokens.get("access_token")
    REFRESH_TOKEN = tokens.get("refresh_token")

    # print(f"Access Token: {access_token}")
    # print(f"Refresh Token: {refresh_token}")
    client = start_connection(ACCESS_TOKEN, REFRESH_TOKEN)
    username= client.user().get().name
    return ACCESS_TOKEN, REFRESH_TOKEN, username

def get_valid_access_token():
    now_ts    = datetime.now(timezone.utc).timestamp()
    expires   = session.get('expires_at', 0)

    # if already expired—or within the safety buffer—refresh
    if now_ts >= expires - REFRESH_BUFFER:
        new_access, new_refresh = refresh_token(session['refresh_token'])
        session['access_token']  = new_access
        session['refresh_token'] = new_refresh
        session['expires_at'] = (datetime.now(timezone.utc) + timedelta(seconds=EXPIRES_IN)).timestamp()

    return session['access_token']

def refresh_token(refresh_token):
    # Request body
    print("attempting to refresh token after 10 seconds")
    data_refresh = {
    "grant_type": "refresh_token",
    "refresh_token": refresh_token,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(token_url, data=data_refresh, headers=headers)
    if response.status_code == 200:
        tokens = response.json()
        ACCESS_TOKEN = tokens["access_token"]
        REFRESH_TOKEN = tokens["refresh_token"]
        print("Token refreshed successfully.")
    else:
        print("Failed to refresh token:", response.json())
    return ACCESS_TOKEN, REFRESH_TOKEN
        
def handle_box_exception(file,e):

    print(f"Failed to run box api: HTTP {e.status} - {e.message} - {e.getResponse}\n")
    file.write(f"Failed to run box api: HTTP {e.status} - {e.message}\n")
    file.flush()
    if e.status == 404:
        print("Folder not found!\n")
        file.write("Folder not found!\n")
        print("Trying to refresh token!\n")
        file.write("Trying to refresh token!\n")
        refresh_token(REFRESH_TOKEN)
    elif e.status == 401:
        print("No permissions [refresh token might have failed]")
    elif e.status == 403:
        print("No permission to access this folder!\n")
        file.write("No permission to access this folder!\n")
    elif e.status == 429:
        print("Rate limit exceeded! Try again later\n.")
        file.write("Rate limit exceeded! Try again later\n.")
