from flask import Flask, request, render_template
import time
import requests
import webbrowser
import api_connect
import get_collabs
import remove_user
import terminal_view
import api_get_auth_code
from boxsdk import BoxAPIException
import os
PORT = 5000

TEMPLATE_DIR = os.path.abspath('./templates')
STATIC_DIR = os.path.abspath('./templates/static')
app = Flask(__name__,  template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)


@app.route("/")
def index():
    template = render_template("index.html")
    return template

@app.route("/get_box_access")
def get_access():
    response = api_get_auth_code.main()
    

@app.route("/auth")
def get_auth_token():
    #Get auth code from response:
    auth_code = request.args.get("code")  # Get the authorization code
    print(f"authcode: {auth_code}\n")

    # Get authtoken from box
    access_token, refresh_token = api_connect.get_access_token(auth_code)
    print(f"access_token: {access_token}\nrefresh_token: {refresh_token}\n")
    template = render_template("index_auth_temp.html")
    return template

@app.route("/auth_terminal")
def get_auth_token_term():
    #Get auth code from response:
    auth_code = request.args.get("code")  # Get the authorization code
    print(f"authcode: {auth_code}\n")

    # Get authtoken from box
    access_token, refresh_token = api_connect.get_access_token(auth_code)
    print(f"access_token: {access_token}\nrefresh_token: {refresh_token}\n")

    terminal_view.run()

@app.route("/get_collabs")
def callback():
    template = render_template('index.html')
    return template


if __name__ == "__main__":
    app.run(port=PORT)
    
