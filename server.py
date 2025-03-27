from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def callback():
    auth_code = request.args.get("code")  # Get the authorization code
    return f"Authorization Code: {auth_code}"

if __name__ == "__main__":
    app.run(port=5000)
