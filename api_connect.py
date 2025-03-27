import requests

CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
AUTH_CODE = "code_from_previous_step"
REDIRECT_URI = "your_redirect_uri"

token_url = "https://api.box.com/oauth2/token"

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

print(f"Access Token: {access_token}")
print(f"Refresh Token: {refresh_token}")
