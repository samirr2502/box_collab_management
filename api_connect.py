import requests
CLIENT_ID = "020r4pyyewrt5si70y5mtvsg4g6kl3qq"
CLIENT_SECRET = "aInyr3WzN8XlOEyZYy8yptsD6siBHW5d"
AUTH_CODE = ''
REDIRECT_URI = "http://127.0.0.1:5000"

token_url = "https://api.box.com/oauth2/token"

#print(f'authcode: {AUTH_CODE}\n')


def send_post_request(code):
    AUTH_CODE = code
    data = {
    "grant_type": "authorization_code",
    "code": AUTH_CODE,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI
}
    response = requests.post(token_url, data=data)
    tokens = response.json()

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    # print(f"Access Token: {access_token}")
    # print(f"Refresh Token: {refresh_token}")
    return access_token, refresh_token
