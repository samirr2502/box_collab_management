from flask import Flask, request, render_template
import requests
import webbrowser
import api_connect
import get_collabs
import remove_user

from boxsdk import BoxAPIException
PORT = 5000
app = Flask(__name__)

@app.route("/")
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



@app.route("/auth")
def auth():
    auth_code = request.args.get("code")  # Get the authorization code
    print(f"authcode: {auth_code}\n")
    template = render_template("home.html")
    
    #Comment Return template and uncomment 'try' to test in the console
    return template

    """
    try:
        option = -1
        while(option != 2):
            option = input("Select an option [0-1-2]\n [0]Find Collabs\n [1]Remove User\n [2]Exit:\n")
            print(f"You selected option {option}\n")
            thread_base = 0

            if option == "0":
                access_token, refresh_token = api_connect.get_access_token(auth_code)
                print(f"access_token: {access_token}\nrefresh_token: {refresh_token}\n")
                
                folder_id = input("File ID: ")
                thread_base = input("Select an option [0/1]\n" +
                                    "[0] No\n[1] Yes:\n")

                print(f"You entered: {folder_id}")
                print("Start running main_threads\n")
                try:
                    get_collabs.main(access_token, folder_id, thread_base)
                    print("Finish running main_threads\n")
                except BoxAPIException as e:
                    print(f"BoxAPIException caught while finding collabs: {e}")
                    api_connect.handle_box_exception(open("exception_file.txt", "w"), e)
                except Exception as e:
                    print(f"Unexpected error during collab finding: {e}")
                    api_connect.handle_box_exception(open("exception_file.txt", "w"), e)

            
            elif option == "1":
                access_token, refresh_token = api_connect.get_access_token(auth_code)
                print(f"access_token: {access_token}\nrefresh_token: {refresh_token}\n")
                print(f"Start typing... {option}\n")
                user_id = input("User ID: ")
                folder_id = input("Folder to remove from\n" +
                                "Note: It removes them from all files in the tree:\n")

                print(f"Removing user {user_id} from parent folder {folder_id}\n")
                try:
                    remove_user.main(access_token, user_id, folder_id, thread_base)
                    print(f"Finished removing user {user_id}")
                except BoxAPIException as e:
                    print(f"BoxAPIException caught while removing user: {e}")
                    api_connect.handle_box_exception(open("exception_file.txt", "w"), e)
                except Exception as e:
                    print(f"Unexpected error during user removal: {e}")
            
            elif option == "2":
                return f"{option} ret"

    except BoxAPIException as e:
        print("BoxAPIException caught during initial access token retrieval.\n")
        api_connect.handle_box_exception(open("exception_file.txt", "w"), e)
    except Exception as e:
        print(f"Unexpected error during initial access token retrieval: {e}")
        return f"{auth_code}"
    """
if __name__ == "__main__":
    app.run(port=PORT)
