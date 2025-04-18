from flask import Flask, request, render_template
import time
import requests
import webbrowser
import api_connect
import get_collabs
import remove_user

from boxsdk import BoxAPIException
PORT = 5000
app = Flask(__name__)

@app.route("/not_in_use")
def callback():
    template = render_template('index.html')
    return template


@app.route("/get_auth")
def get_auth():
    CLIENT_ID = "020r4pyyewrt5si70y5mtvsg4g6kl3qq"
    REDIRECT_URI = "http://127.0.0.1:5000/auth"
    auth_code_url = f"https://account.box.com/api/oauth2/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    response = requests.get(auth_code_url)
    webbrowser.open(auth_code_url)

    #auth_code_response = response.json()

    #auth_code_ = auth_code_response.get("code")

    print(f"Response: {response}")
    return "redirecting "

#Toggle
#  for testing: use "/"
#  for prod: use "/auth"
#@app.route("/auth")
@app.route("/")
def auth():
    auth_code = request.args.get("code")  # Get the authorization code
    print(f"authcode: {auth_code}\n")
    template = render_template("home.html")
    
    #Comment Return template and uncomment 'try' to test in the console
    # return template

    
    access_token, refresh_token = api_connect.get_access_token(auth_code)
    print(f"access_token: {access_token}\nrefresh_token: {refresh_token}\n")

    try:
        option = -1
        while(option != 2):
            option = input("Select an option [0-1-2]\n [0]Find Collabs\n [1]Remove User\n [2]Exit:\n")
            print(f"You selected option {option}\n")

            if option == "0":
                
                folder_id = input("Folder ID: ")
               
                print(f"You entered: {folder_id}")

                exclude_folder_ids = input("Exclude Folder Id: ")
               
                print(f"You entered: {exclude_folder_ids}")

                
                restart = input("Press 1 to start, 0 to restart: ")
                if restart == 0:
                    continue
                
                print(">>Get Collabs started<<\n")
                try:
                    get_collabs.main(access_token,refresh_token, folder_id, exclude_folder_ids)
                    print("Finish running get_collabs\n")
                except BoxAPIException as e:
                    print(f"BoxAPIException caught while finding collabs: {e}")
                    api_connect.handle_box_exception(open("exception_file.txt", "w"), e)
                    e.close()
                except Exception as e:
                    print(f"Unexpected error during collab finding: {e}")
                    api_connect.handle_box_exception(open("exception_file.txt", "w"), e)
                    e.close()
            
            elif option == "1":
                print(f"access_token: {access_token}\nrefresh_token: {refresh_token}\n")
                print(f"Start typing... {option}\n")
                user_id = input("User ID: ")
                folder_id = input("Folder to remove from\n" +
                                "Note: It removes them from all files in the tree:\n")

                print(f"Removing user {user_id} from parent folder {folder_id}\n")
                try:
                    remove_user.main(access_token, user_id, folder_id)
                    print(f"Finished removing user {user_id}")
                except BoxAPIException as e:
                    print(f"BoxAPIException caught while removing user: {e}")
                    api_connect.handle_box_exception(open("exception_file.txt", "w"), e)
                except Exception as e:
                    print(f"Unexpected error during user removal: {e}")
            
            elif option == "2":
                return f"{option} ret"
            else:
                option =""

    except BoxAPIException as e:
        print("BoxAPIException caught during initial access token retrieval.\n")
        api_connect.handle_box_exception(open("exception_file.txt", "w"), e)
    except Exception as e:
        print(f"Unexpected error during initial access token retrieval: {e}")
        return f"{auth_code}"
    #"""
if __name__ == "__main__":
    app.run(port=PORT)
