from flask import Flask, request, session, redirect, jsonify,send_from_directory
from flask_session import Session  
from celery import Celery
from tasks import run_collabs
from datetime import datetime, timedelta,timezone


import api_connect
import get_collabs
# import remove_user
import get_items
import terminal_view
from app import app
import os
EXPIRES_IN = 50*60

PORT = 5000

TEMPLATE_DIR = os.path.abspath('./box-collab/dist')
STATIC_DIR = os.path.abspath('./box-collab/dist/assets')



@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    if path != "" and os.path.exists(f"{TEMPLATE_DIR}/{path}"):
        return send_from_directory(TEMPLATE_DIR, path)
    else:
        return send_from_directory(TEMPLATE_DIR, 'index.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/auth")
def get_auth_token():
    #Get auth code from response:
    auth_code = request.args.get("code")  # Get the authorization code
    print(f"authcode: {auth_code}\n")

    # Get authtoken from box
    access_token, refresh_token, user_name = api_connect.get_access_token(auth_code)

    print(f"access_token: {access_token}\nrefresh_token: {refresh_token}\n")
    session['access_token'] = access_token
    session['refresh_token'] = refresh_token
    session['access_token']  = access_token
    session['expires_at']    = (datetime.now(timezone.utc)+ timedelta(seconds=EXPIRES_IN)).timestamp()
    session['session_user'] = user_name
    return redirect(f"http://127.0.0.1:5000?session_user={session['session_user']}")

@app.route("/auth_terminal")
def get_auth_token_term():
    #Get auth code from response:
    auth_code = request.args.get("code")  # Get the authorization code
    print(f"authcode: {auth_code}\n")

    # Get authtoken from box
    access_token, refresh_token, user_name = api_connect.get_access_token(auth_code)
    print(f"access_token: {access_token}\nrefresh_token: {refresh_token}\n")

    terminal_view.run()


@app.route('/get_collabs', methods=['POST'])
def get_collabs_endpoint():
    data = request.json
    task = run_collabs.delay(
        session['access_token'],
        session['refresh_token'],
        data.get('folderId'),
        data.get('excludeFolderIds','')
    )
    print(data, session)
    return jsonify({ 'task_id': task.id }), 202


@app.route('/tasks/<task_id>')
def get_status(task_id):
    task = run_collabs.AsyncResult(task_id)
    if task.state == 'PENDING':
        return jsonify(status='pending'), 202
    elif task.state == 'SUCCESS':
        return jsonify(status='done', result=task.result), 200
    else:
        return jsonify(status=task.state, info=task.info), 500

@app.route("/get_collabs")
def callback():
    folder_id = request.args.get("folderId")
    exclude_ids = request.args.get("excludeFolderIds", "")
    # Convert exclude IDs to a list
    exclude_list = []

    #get refresh token
    # refresh_token = request.args.get("refreshToken")
    # access_token = request.args.get("accessToken")
    refresh_token = session['refresh_token']
    access_token = session['access_token']
    print(f"folder_id: {folder_id}\nexcludeFolderIds: {exclude_ids}\n")

    print(f"access_token: {access_token}\nrefresh_token: {refresh_token}\n")

    # access_token, refresh_token = api_connect.refresh_token(refresh_token)

    # Call your processing function
    get_collabs.main(access_token, refresh_token,folder_id, exclude_ids)
    return jsonify({"status": "success", "message": "Collaboration complete"})


@app.route("/get_items")
def get_items_box():
    folder_id = request.args.get("folderId")
    # refresh_token = request.args.get("refreshToken")
    # access_token = request.args.get("accessToken")
    refresh_token = session['refresh_token']
    access_token = session['access_token']

    print(f"folder_id: {folder_id}\n")
    items = get_items.main(access_token,refresh_token, folder_id)
    jsoned = jsonify(items)
    return jsoned

if __name__ == "__main__":
    app.run(port=PORT)
    
