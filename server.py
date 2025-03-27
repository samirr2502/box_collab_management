from flask import Flask, request
import api_connect, main_threads
app = Flask(__name__)

@app.route("/")
def callback():
    auth_code = request.args.get("code")  # Get the authorization code
    print(f"authcode: {auth_code}\n")
    access_token, refresh_token = api_connect.send_post_request(auth_code)
    print(f"access_token: {access_token}\nrefresh_token: {refresh_token}\n")
    print(f"Start running main_threads\n")

    main_threads.main(access_token, refresh_token)
    print(f"Finish running main_threads\n")


    return f"{auth_code}"

if __name__ == "__main__":
    app.run(port=5000)
