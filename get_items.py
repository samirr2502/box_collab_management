from boxsdk import Client, OAuth2, BoxAPIException
import time
from datetime import datetime
import api_connect
#GLOBAL VARIABLES
REFRESH_TOKEN= ''
DEV_TOKEN = "GcDK9FKHuyJgy1MvPDJRtKDylT2z0M2Z"
TIME_TO_REFRESH = 50*60

def start_connection(access_token, refresh_token):
    REFRESH_TOKEN = refresh_token

    print("started box connection\n")
    #Create Connection 
    auth = OAuth2(client_id=None, client_secret=None, access_token=access_token)
    client = Client(auth)
    print(f'box connection made: {client}\n')
    return client


def main(access_token, refresh_token,folder_id):
    #start connection
    client = start_connection(access_token,refresh_token)
    start= time.time()
    print("call got to server\n")
    folders = client.folder(folder_id=folder_id).get_items()
    f_ = [{folder.id: folder.name} for folder in folders]
    print(folders, f_)
    return f_

