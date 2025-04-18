import requests

import webbrowser

def main():
    CLIENT_ID = "020r4pyyewrt5si70y5mtvsg4g6kl3qq"
    REDIRECT_URI = "http://127.0.0.1:5000/auth"


    auth_code_url = f"https://account.box.com/api/oauth2/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"


    response = requests.get(auth_code_url)
    webbrowser.open(auth_code_url)

    #auth_code_response = response.json()

    #auth_code_ = auth_code_response.get("code")

    print(f"Response: {response}")
