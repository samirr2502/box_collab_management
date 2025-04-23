from flask import Flask, request, render_template, redirect, jsonify,send_from_directory
import time
import requests
import webbrowser
import api_connect
import get_collabs
import remove_user
import get_items
import terminal_view
import api_get_auth_code
from boxsdk import BoxAPIException
import os
PORT = 5000

TEMPLATE_DIR = os.path.abspath('./box-collab/dist')
STATIC_DIR = os.path.abspath('./box-collab/dist/assets')
app = Flask(__name__,  template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    if path != "" and os.path.exists(f"{TEMPLATE_DIR}/{path}"):
        return send_from_directory(TEMPLATE_DIR, path)
    else:
        return send_from_directory(TEMPLATE_DIR, 'index.html')


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
    return redirect(f"http://127.0.0.1:5000?refreshToken={refresh_token}&accessToken={access_token}")

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
    folder_id = request.args.get("folderId")
    exclude_ids = request.args.get("excludeFolderIds", "")
    # Convert exclude IDs to a list
    exclude_list = []

    #get refresh token
    refresh_token = request.args.get("refreshToken")
    access_token = request.args.get("accessToken")
    print(f"folder_id: {folder_id}\nexcludeFolderIds: {exclude_ids}\n")

    print(f"access_token: {access_token}\nrefresh_token: {refresh_token}\n")

    # access_token, refresh_token = api_connect.refresh_token(refresh_token)

    # Call your processing function
    get_collabs.main(access_token, refresh_token,folder_id, exclude_ids)
    return jsonify({"status": "success", "message": "Collaboration complete"})


@app.route("/get_items")
def get_items_box():
    folder_id = request.args.get("folderId")
    refresh_token = request.args.get("refreshToken")
    access_token = request.args.get("accessToken")

    print(f"folder_id: {folder_id}\n")
    items = get_items.main(access_token,refresh_token, folder_id)
    jsoned = jsonify(items)
    return jsoned

if __name__ == "__main__":
    app.run(port=PORT)
    
