from flask import Flask, request
import api_connect
import get_collabs
import remove_user
from boxsdk import BoxAPIException
PORT = 5000
app = Flask(__name__)

@app.route("/")
def callback():
    auth_code = request.args.get("code")  # Get the authorization code
    print(f"authcode: {auth_code}\n")
    try:
        access_token, refresh_token = api_connect.get_access_token(auth_code)
        print(f"access_token: {access_token}\nrefresh_token: {refresh_token}\n")
        option = -1
        while(option !=2):
            option = input("Select an option [0-1-2]\n [0]Find Collabs\n [1]Remove User\n [2]Exit:")
            print(f"you selected option {option}\n")
            thread_base = 0
            if (option =="0"):
                folder_id = input("file id: ")
                thread_base = input("Select an option [0/1]\n"+
                                    "[0] No\n[1] Yes:\n")

                print(f"You entered: {folder_id}")
                print("Start running main_threads\n")
                get_collabs.main(access_token, folder_id,thread_base)
                
                print("Finish running main_threads\n")
            elif (option=="1"):
                print(f"start typing...{option}\n")
                user_id = input("user id: ")
                folder_id = input("folder to remove from\n" +
                                    "note: it removes them from all files in the tree:\n")

                print(f"removing user {user_id} from parent folder {folder_id}\n")
                remove_user.main(access_token, user_id, folder_id, thread_base)
                print(f"finished removing user {user_id}")
            elif (option =="2"):
                break
    except BoxAPIException as e:
        api_connect.handle_box_exception(open("exception file.txt","w"),e)

    return f"{auth_code}"

if __name__ == "__main__":
    app.run(port=PORT)
