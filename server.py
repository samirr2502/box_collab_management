from flask import Flask, request
import api_connect
import main_threads
from boxsdk import BoxAPIException
PORT = 5001
app = Flask(__name__)

@app.route("/")
def callback():
    auth_code = request.args.get("code")  # Get the authorization code
    print(f"authcode: {auth_code}\n")
    access_token, refresh_token = api_connect.send_post_request(auth_code)
    print(f"access_token: {access_token}\nrefresh_token: {refresh_token}\n")

    folder_id = input("file id: ")
    thread_base = input("thread?[1 - yes, 0 - no]: ")

    print(f"You entered: {folder_id}")
    print("Start running main_threads\n")
    try:
        main_threads.main(access_token, folder_id,thread_base)
    except BoxAPIException as e:
        api_connect.handle_box_exception(open("exception file.txt","w"),e)
    print("Finish running main_threads\n")


    return f"{auth_code}"

if __name__ == "__main__":
    app.run(port=PORT)
